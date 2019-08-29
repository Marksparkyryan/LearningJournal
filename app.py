import datetime
from flask import Flask, render_template, redirect, url_for, g

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
        return None


@app.route("/login", methods=("GET", "POST",))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            pass  # add message here?
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                # message here?
                return redirect(url_for("index"))
    return render_template("login.html", form=form)


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
def index():
    context = {
        "entries": models.Entry.select().order_by(models.Entry.date.desc())
    }
    return render_template("index.html", **context)


@app.route("/entries/new", methods=("GET", "POST",))
def add():
    form = forms.AddEntryForm()
    if form.validate_on_submit():
        try:
            models.Entry.create_entry(
                author=g.user._get_current_object(),
                title=form.title.data,
                content=form.content.data,
                date=form.date.data,
                time_spent=form.time_spent.data,
                resources=form.resources.data,
            )
        except:
            Print("Entry not made!")
        return redirect(url_for("index"))
    return render_template("new.html", form=form)


@app.route("/entries/<int:id>", methods=("GET",))
def detail(id):
    try:
        entry = models.Entry.get_by_id(id)
    except models.DoesNotExist:
        pass
    context = {
        "entry": entry,
    }
    return render_template("detail.html", **context)


@login_required
@app.route("/entries/<id>/edit")
def edit(id):
    pass


@login_required
@app.route("/entries/<id>/delete")
def delete(id):
    pass


if __name__ == "__main__":
    models.initialize_database()
    try:
        models.User.create_user(
            username="sparky",
            email="sparky@email.com",
            password="password",
            admin=True
        )
    except ValueError:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)
