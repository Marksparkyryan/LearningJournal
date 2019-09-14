from functools import wraps
from urllib.parse import urlparse

from flask import (Flask, render_template, redirect, url_for, g, request,
                   abort, flash)
from flask_bcrypt import check_password_hash
from flask_login import (login_required, LoginManager, login_user, logout_user,
                         current_user)
from werkzeug.exceptions import HTTPException

import handlers
import models
import forms
import dummy_data


DUMMYDATA = True
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
    """Retrieves instance of User"""

    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        abort(404, message="That user doesn't exist.")


def check_ownership(func):
    """Verifies that current user is owner of requested post"""

    @wraps(func)
    def decorator(*args, **kwargs):
        slug = kwargs["slug"]
        try:
            entry = models.Entry.get(
                models.Entry.slug == slug,
            )
        except models.DoesNotExist:
            abort(404, "That entry doesn't exist.")
        if entry.author != current_user:
            abort(403, "You aren't the owner of this post.")
        return func(*args, **kwargs)
    return decorator


@app.route("/login", methods=("GET", "POST",))
def login():
    """
    View that requests user's credentials and creates a new session for user
    """

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
                next = request.args.get('next')
                safe = urlparse(next).netloc == ""
            if next:
                if not safe:
                    return abort(400, "That's not a valid redirect.")
            return redirect(next or url_for('index'))
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    """Ends current user's session"""

    logout_user()
    flash("You've been logged out!")
    return redirect(url_for('index'))


@app.route("/signup", methods=("GET", "POST",))
def signup():
    """Registers new user if they don't already exist"""

    form = forms.SignUpForm()
    if form.validate_on_submit():
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        flash("Yay! You registered!")
        return redirect(url_for("login"))
    return render_template("signup.html", form=form)


@app.before_request
def before_request():
    """
    Connect to the database before each request. Share the current 
    user in a global variable.
    """

    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """
    Close the database connection after each request and return a response
    """

    g.db.close()
    return response


@app.route("/")
@app.route("/entries")
@app.route("/entries/<tag>/topic")
def index(tag=None):
    """Main view of journal. All entries are displayed here"""

    if tag:
        try:
            tag_model = models.Tag.get(
                models.Tag.topic == tag,
            )
            context = {
                "entries": (
                    models.Entry.select().join(
                        models.EntryTag, on=models.EntryTag.entry
                    ).where(
                        models.EntryTag.tag == tag_model,
                    )),
                "heading": "{} posts".format(tag),
            }
        except models.DoesNotExist:
            abort(404, "That tag doesn't exist.")
    else:
        context = {
            "entries": models.Entry.select().order_by(
                models.Entry.date.desc()
            ),
            "heading": "all posts"
        }
    return render_template("index.html", **context)


@app.route("/entries/new", methods=("GET", "POST",))
@login_required
def add():
    """View to create new journal entry"""

    form = forms.AddEntryForm()
    if form.validate_on_submit():
        try:
            models.Entry.get(
                models.Entry.title == form.title.data,
            )
        except models.DoesNotExist:
            models.Entry.create_entry(
                author=g.user._get_current_object(),
                title=form.title.data,
                content=form.content.data,
                date=form.date.data,
                time_spent=form.time_spent.data,
            )
            entry = models.Entry.get(
                models.Entry.title**form.title.data
            )
            if form.tags.data:
                handlers.tag_handler(entry, form)
            if form.resources.data:
                handlers.resource_handler(entry, form)
                flash("New entry created!")
                return redirect(url_for("index"))
        flash("That title is taken! Please change.")
        return render_template("new.html", form=form)
    return render_template("new.html", form=form)


@app.route("/entries/<slug>", methods=("GET",))
def detail(slug):
    """View to display details of a single post"""

    try:
        entry = models.Entry.get(
            models.Entry.slug == slug
        )
        resource = models.Entry.resources
    except models.DoesNotExist:
        abort(404, "That entry doesn't exist.")
    context = {
        "entry": entry,
        "resources": resource,
    }
    return render_template("detail.html", **context)


@app.route("/entries/<slug>/edit", methods=("GET", "POST"))
@login_required
@check_ownership
def edit(slug):
    """View to allow editing of a single post"""

    try:
        entry = models.Entry.get(
            models.Entry.slug == slug,
        )
    except models.DoesNotExist:
        abort(404, "That entry doesn't exist")
    else:
        form = forms.EditEntryForm(obj=entry)
        if form.validate_on_submit():
            with models.DATABASE.transaction():
                if form.resources.data:
                    handlers.resource_handler(entry, form)
                else:
                    handlers.delete_resource_handler(entry)
                if form.tags.data:
                    handlers.tag_handler(entry, form)
                else:
                    handlers.delete_tag_handler(entry)
                entry.title = form.title.data
                entry.slug = "-".join(form.title.data.lower().split())
                entry.time_spent = form.time_spent.data
                entry.content = form.content.data
                entry.date = form.date.data
                entry.save()
                flash("Entry edited successfuly!")
                return redirect(url_for("detail", slug=entry.slug))
        return render_template("edit.html", form=form, entry=entry)


@app.route("/entries/<slug>/delete")
@login_required
@check_ownership
def delete(slug):
    """Deletes instance of current entry"""

    models.Entry.get(
        models.Entry.slug == slug
    ).delete_instance()
    flash("Entry deleted successfuly")
    return redirect(url_for('index'))


@app.errorhandler(HTTPException)
def http_error(HTTPException):
    """Handles abort calls and renders appropriate error page"""

    return render_template(
        "{}.html".format(HTTPException.code),
        message=HTTPException.description), HTTPException.code


if __name__ == "__main__":
    models.initialize_database()
    if DUMMYDATA:
        dummy_data.dummy_data()
        app.run(debug=DEBUG, host=HOST, port=PORT)
