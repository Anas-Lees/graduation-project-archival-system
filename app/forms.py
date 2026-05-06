from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, SelectField, SelectMultipleField, BooleanField, SubmitField, URLField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional, URL, Regexp
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
    thumbnail = FileField(_l("Thumbnail image (optional, JPG / PNG / WebP)"),
                          validators=[Optional(),
                                      FileAllowed(["jpg", "jpeg", "png", "webp", "svg"],
                                                  _l("Images only (JPG, PNG, WebP, SVG)"))])
    file = FileField(_l("Project document (PDF or DOCX)"),
                     validators=[FileRequired(),
                                 FileAllowed(["pdf", "docx", "doc"], _l("PDF or DOCX only"))])
    video = FileField(_l("Demo video (optional, MP4 / WebM / MOV)"),
                      validators=[Optional(),
                                  FileAllowed(["mp4", "webm", "mov", "m4v"],
                                              _l("MP4, WebM, MOV, or M4V only"))])
    slides = FileField(_l("Slides (optional, PPTX / PPT / PDF)"),
                       validators=[Optional(),
                                   FileAllowed(["pptx", "ppt", "pdf"],
                                               _l("PPTX, PPT, or PDF only"))])
    github_url = URLField(_l("GitHub repository (optional)"),
                          validators=[Optional(), Length(max=500),
                                      Regexp(r"^https?://(www\.)?github\.com/[\w.-]+/[\w.-]+/?",
                                             message=_l("Must be a github.com URL, e.g. https://github.com/user/repo"))])
    submit = SubmitField(_l("Submit for approval"))


class RejectForm(FlaskForm):
    reason = TextAreaField(_l("Reason"), validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField(_l("Reject"))


class UserAdminForm(FlaskForm):
    full_name = StringField(_l("Full name"), validators=[DataRequired()])
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    role = SelectField(_l("Role"), choices=[("student", _l("Student")),
                                            ("doc", _l("Doctor"))])
    password = PasswordField(_l("Password (leave blank to keep)"), validators=[Optional(), Length(min=8)])
    submit = SubmitField(_l("Save"))
