from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, PasswordField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField


class AddEntryForm(FlaskForm):
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
        "resource title, wwww.resourcelink.com",
    )


class LoginForm(FlaskForm):
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
