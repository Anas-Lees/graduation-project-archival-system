from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, SelectField, SelectMultipleField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional
from flask_babel import lazy_gettext as _l


class RegisterForm(FlaskForm):
    full_name = StringField(_l("Full name"), validators=[DataRequired(), Length(max=120)])
    email = StringField(_l("Email"), validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField(_l("Password"), validators=[DataRequired(), Length(min=8, max=128)])
    confirm = PasswordField(_l("Confirm password"), validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField(_l("Create account"))


class LoginForm(FlaskForm):
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    remember = BooleanField(_l("Remember me"))
    submit = SubmitField(_l("Sign in"))


class ProjectForm(FlaskForm):
    title = StringField(_l("Title"), validators=[DataRequired(), Length(max=255)])
    abstract = TextAreaField(_l("Abstract"), validators=[DataRequired(), Length(min=50)])
    keywords = StringField(_l("Keywords (comma-separated)"), validators=[Optional(), Length(max=500)])
    year = IntegerField(_l("Year"), validators=[DataRequired(), NumberRange(min=2000, max=2099)])
    department = StringField(_l("Department"), validators=[DataRequired(), Length(max=120)])
    categories = SelectMultipleField(_l("Categories"), coerce=int)
    file = FileField(_l("Project file (PDF or DOCX)"),
                     validators=[FileRequired(), FileAllowed(["pdf", "docx", "doc"], _l("PDF or DOCX only"))])
    submit = SubmitField(_l("Submit for approval"))


class RejectForm(FlaskForm):
    reason = TextAreaField(_l("Reason"), validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField(_l("Reject"))


class UserAdminForm(FlaskForm):
    full_name = StringField(_l("Full name"), validators=[DataRequired()])
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    role = SelectField(_l("Role"), choices=[("student", "Student"), ("faculty", "Faculty"),
                                            ("admin", "Admin"), ("sysadmin", "System Admin")])
    password = PasswordField(_l("Password (leave blank to keep)"), validators=[Optional(), Length(min=8)])
    submit = SubmitField(_l("Save"))
