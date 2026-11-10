"""WTForms used by the authentication pages."""
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp


class RegisterForm(FlaskForm):
    name = StringField(
        "Full name",
        validators=[DataRequired(), Length(min=3, max=80)],
        render_kw={"placeholder": "e.g. Aarav Sharma"},
    )
    email = StringField(
        "Email address",
        validators=[DataRequired(), Email(), Length(max=120)],
        render_kw={"placeholder": "you@example.com"},
    )
    phone = StringField(
        "Phone number",
        validators=[DataRequired(), Regexp(r"^[+]?[0-9\s\-]{10,15}$", message="Enter a valid phone number.")],
        render_kw={"placeholder": "+91 98765 43210"},
    )
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField(
        "Confirm password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Create account")


class LoginForm(FlaskForm):
    email = StringField(
        "Email address",
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "you@example.com"},
    )
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Keep me signed in")
    submit = SubmitField("Sign in")
