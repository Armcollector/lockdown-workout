from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateTimeField,
    FloatField,
    HiddenField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.fields.html5 import IntegerRangeField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, optional

from app.databasefunctions import getteams
from app.models import Pushupchallenge_user


class RegisterUser(FlaskForm):
    username = StringField("Brukernavn", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    team = SelectField("Team", choices=getteams())
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = Pushupchallenge_user.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        user = Pushupchallenge_user.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")


class Logpushups(FlaskForm):
    day = IntegerRangeField("day")
    push_reps = IntegerRangeField("push_reps")
    pull_reps = IntegerRangeField("pull_reps")
    air_reps = IntegerRangeField("air_reps")
    sit_reps = IntegerRangeField("sit_reps")
    dt = HiddenField("date")


class LoginForm(FlaskForm):
    username = StringField("Brukernavn", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")
