from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, Email, Length
from flask_ckeditor import CKEditorField

##WTForm
class RegisterUser(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(),Email()])
    password = PasswordField("Password (Minimum 6 characters)", validators=[DataRequired(),Length(min=6)])
    submit = SubmitField("Submit")


class LoginUser(FlaskForm):
    email = StringField("Email", validators=[DataRequired(),Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class TaskForm(FlaskForm):
    task_name = StringField("Task Name", validators=[DataRequired()])
    subtask_name = StringField("Subtask Name", validators=[DataRequired()])
    delegated_to = StringField("Delegated to", validators=[DataRequired()])
    task_completed_date = StringField("Completed On (leave blank if not completed)")
    status = SelectField('Status',choices=['🔴 Not Started','🟡 Work in Progress','🟢 Completed'], validators=[DataRequired()])
    notes = StringField("Notes", validators=[DataRequired()])
    submit = SubmitField("Submit")


class FeedbackForm(FlaskForm):
    comment = StringField("Comment", validators=[DataRequired()])
    commentator_name = StringField("Your Display Name", validators=[DataRequired()])
    commentator_email = StringField("Email",validators=[DataRequired(),Email()])
    submit = SubmitField("Add Comment")


class ForgotPassword(FlaskForm):
    email = StringField("Enter Registered Email:", validators=[DataRequired(),Email()])
    submit = SubmitField("Send Password Reset Code")

class CodeVerication(FlaskForm):
    code = StringField("Enter the code:", validators=[DataRequired()])
    submit = SubmitField("Submit Code")

class ResetPassword(FlaskForm):
    new_password = StringField("Enter new password (Minimum 6 characters)", validators=[DataRequired(),Length(min=6)])
    submit = SubmitField("Reset Password")




