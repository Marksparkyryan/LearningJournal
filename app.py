import datetime
from functools import wraps
import json
import re
from flask import Flask, render_template, redirect, url_for, g, request, abort, flash
from werkzeug.exceptions import HTTPException

from flask_bcrypt import check_password_hash
from flask_login import (login_required, LoginManager, login_user, logout_user,
                         current_user)

import models
import forms

DEBUG = True
PORT = 8000
HOST = "0.0.0.0"

app = Flask(__name__)
app.secret_key = "secretkey"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        abort(404, message="That user doesn't exist.")


def check_ownership(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        slug = kwargs["slug"]
        print("slug: ", slug)
        try:
            entry = models.Entry.get(
                models.Entry.slug == slug,
            )
            print(slug, entry)
        except models.DoesNotExist:
            abort(404, "That entry doesn't exist.")
        if entry.author != current_user:
            abort(403, "You aren't the owner of this post.")
        return func(*args, **kwargs)
    return decorator


@app.route("/login", methods=("GET", "POST",))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Username and password is incorrect!")
            return redirect(url_for("login"))
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You're now logged in!")
                return redirect(url_for("index"))
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash("You've been logged out!")
    return redirect(url_for('index'))


@app.before_request
def before_request():
    """Connect to the database before each request"""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user
    g.now = datetime.datetime.now()


@app.after_request
def after_request(response):
    """Close the database connection after each request"""
    g.db.close()
    return response


@app.route("/")
@app.route("/entries")
@app.route("/entries/<tag>/topic")
def index(tag=None):
    if tag:
        try:
            tag_model = models.Tag.select().where(
                models.Tag.topic == tag,
            )
            context = {
                "entries": (
                    models.Entry.select().join(
                        models.EntryTag, on=models.EntryTag.entry
                    ).where(
                        models.EntryTag.tag == tag_model,
                    )
                ),
                "heading": "{} posts".format(tag)
            }
        except models.DoesNotExist:
            abort(404, "That tag doesn't exist.")
    else:
        context = {
            "entries": models.Entry.select().order_by(models.Entry.date.desc()),
            "heading": "all posts"
        }
    return render_template("index.html", **context)


@app.route("/entries/new", methods=("GET", "POST",))
@login_required
def add():
    form = forms.AddEntryForm()
    if form.validate_on_submit():
        try:
            models.Entry.get(
                models.Entry.title**form.title.data,
            )
        except models.DoesNotExist:
            if form.resources.data:
                resource_dict = parse_resources(form)
            models.Entry.create_entry(
                author=g.user._get_current_object(),
                title=form.title.data,
                content=form.content.data,
                date=form.date.data,
                time_spent=form.time_spent.data,
                resources=json.dumps(resource_dict),
            )
            if form.text_tags.data:
                this_entry = models.Entry.get(
                    models.Entry.title**form.title.data
                )
                data = form.text_tags.data
                tag_pattern = re.compile(r"[#]\w+\b")
                tags = tag_pattern.findall(data)
                for tag in tags:
                    try:
                        new_tag = models.Tag.create(
                            topic=tag
                        )
                    except models.IntegrityError:
                        new_tag = models.Tag.select().where(
                            models.Tag.topic == tag
                        )
                    try:
                        models.EntryTag.create(
                            entry=this_entry,
                            tag=new_tag,
                        )
                    except models.IntegrityError:
                        pass
                flash("New entry created!")
                return redirect(url_for("index"))
        flash("That title is taken! Please change.")
        return render_template("new.html", form=form)
    return render_template("new.html", form=form)


@app.route("/entries/<slug>", methods=("GET",))
def detail(slug):
    try:
        entry = models.Entry.get(
            models.Entry.slug == slug
        )
        resources = json.loads(entry.resources)
    except models.DoesNotExist:
        abort(404, "That entry doesn't exist.")
    context = {
        "entry": entry,
        "resources": resources
    }
    return render_template("detail.html", **context)


@app.route("/entries/<slug>/edit", methods=("GET", "POST"))
@login_required
@check_ownership
def edit(slug):
    try:
        entry = models.Entry.get(
            models.Entry.slug == slug,
        )
    except models.DoesNotExist:
        abort(404, "That entry doesn't exist")
    else:
        form = forms.EditEntryForm(obj=entry)

        if form.validate_on_submit():
            if form.resources.data:
                resources_dict = parse_resources(form)
                print(resources_dict)
            if form.text_tags.data:
                this_entry = models.Entry.get(
                    models.Entry.slug == slug,
                )
                old_tags = this_entry.text_tags.split()
                new_data = form.text_tags.data
                tag_pattern = re.compile(r"[#]\w+\b")
                new_tags = tag_pattern.findall(new_data)
                for tag in old_tags:
                    if tag not in new_tags:
                        try:
                            q = models.Tag.get(
                                models.Tag.topic == tag
                            )
                            entry_tag = models.EntryTag.get(
                                models.EntryTag.tag == q,
                                models.EntryTag.entry == this_entry,
                            )
                            entry_tag.delete_instance()
                        except:
                            pass

                for tag in new_tags:
                    try:
                        new_tag = models.Tag.create(
                            topic=tag
                        )
                    except models.IntegrityError:
                        new_tag = models.Tag.get(
                            models.Tag.topic == tag
                        )
                    except:
                        pass
                    try:
                        models.EntryTag.create(
                            entry=new_entry,
                            tag=new_tag,
                        )
                    except models.IntegrityError:
                        pass
                    except:
                        pass
            else:
                delete_all_tags_query = models.EntryTag.select().where(
                    models.EntryTag.entry == entry,
                )
                for instance in delete_all_tags_query:
                    instance.delete_instance()
                print("deleted all tags")
            flash("Entry edited successfuly!")
            return redirect(url_for("detail", slug=entry.slug))
        return render_template("edit.html", form=form, entry=entry)


@app.route("/entries/<slug>/delete")
@login_required
@check_ownership
def delete(slug):
    models.Entry.get_by_id(slug).delete_instance()
    flash("Entry deleted successfuly")
    return redirect(url_for('index'))


def parse_resources(form):
    resource_dict = {}
    url_pattern = re.compile(
        r"(\b(http[s]*:\/\/|(www\.))(\S)*\b/?)")
    resources_lines = form.resources.data.splitlines()
    for line in resources_lines:
        url_match = url_pattern.search(line)
        title = re.sub(url_pattern, "", line)
        cleaned_title = cleaned_title = re.sub(
            r"[\b|\b]", "", title)
        if url_match:
            resource_dict[cleaned_title] = url_match[0]
        else:
            resource_dict[cleaned_title] = ""
    return resource_dict


@app.errorhandler(HTTPException)
def http_error(HTTPException):
    return render_template("{}.html".format(HTTPException.code),
                           message=HTTPException.description), HTTPException.code


if __name__ == "__main__":
    models.initialize_database()
    try:
        models.User.create_user(
            username="sparky",
            email="sparky@email.com",
            password="password",
            admin=True
        )
        models.User.create_user(
            username="jess",
            email="jess@email.com",
            password="password",
            admin=True
        )
    except ValueError:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)
