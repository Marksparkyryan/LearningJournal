from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, PasswordField
from wtforms.fields.html5 import DateField
from wtforms.validators import (DataRequired, Email, ValidationError, Length,
                                EqualTo, Regexp)

from models import User


class AddEntryForm(FlaskForm):
    """Form to add data to a journal entry"""

    title = StringField(
        "Title",
        validators=[
            DataRequired()
        ]
    )
    content = TextAreaField(
        "What I learned",
        validators=[
            DataRequired()
        ],
        render_kw={
            "rows": 5,
        }
    )
    date = DateField(
        "Date",
        validators=[
            DataRequired()
        ],
        format="%Y-%m-%d",
    )
    time_spent = IntegerField(
        "Time Spent (hours)",
        validators=[
            DataRequired()
        ]
    )
    resources = TextAreaField(
        "example title example link \nexample title example link",
    )
    tags = StringField(
        "#exampletag #exampletag",

    )


class EditEntryForm(FlaskForm):
    """Form to edit data in existing entry"""

    title = StringField(
        "Title",
        validators=[
            DataRequired()
        ]
    )
    content = TextAreaField(
        "What I learned",
        validators=[
            DataRequired()
        ]
    )
    date = DateField(
        "Date",
        validators=[
            DataRequired()
        ],
        format="%Y-%m-%d",
    )
    time_spent = IntegerField(
        "Time Spent (hours)",
        validators=[
            DataRequired()
        ]
    )
    resources = TextAreaField(
        "Resources",
    )
    tags = StringField(
        "Tags",
    )


class LoginForm(FlaskForm):
    """Form to capture user credentials to create user session"""

    email = StringField(
        "email",
        validators=[
            DataRequired()
        ]
    )
    password = PasswordField(
        "password",
        validators=[
            DataRequired()
        ]
    )


def name_exists(form, field):
    """Verifies that username is unique"""

    if User.select().where(User.username == field.data).exists():
        raise ValidationError("User with that username already exists!")


def email_exists(form, field):
    """Verifies that email address is unique"""

    if User.select().where(User.email == field.data).exists():
        raise ValidationError("User with that email already exists!")


class SignUpForm(FlaskForm):
    """Form to capture new user data"""

    username = StringField(
        "username",
        validators=[
            DataRequired(),
            name_exists,
            Regexp(
                r"^[a-zA-Z0-9_]+$",
                message="Username should be one word, letters, numbers, "
                "and underscores only."
            )
        ]
    )
    email = StringField(
        "email",
        validators=[
            DataRequired(),
            Email(),
            email_exists,
        ]
    )
    password = PasswordField(
        "password",
        validators=[
            DataRequired(),
            Length(min=8),
            EqualTo("password2", message="Passwords must match!")
        ]
    )
    password2 = PasswordField(
        "confirm password",
        validators=[
            DataRequired()
        ]
    )
