from flask import Flask, render_template, redirect, url_for, flash
import datetime
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_gravatar import Gravatar
from forms import FeedbackForm, TaskForm, LoginUser, RegisterUser, ForgotPassword, ResetPassword, CodeVerication
import os
import random
import smtplib


app = Flask(__name__)
Bootstrap(app)
# Gravatar Image
gravatar = Gravatar(app, size=50, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False,
                    base_url=None)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE')
SHOUNAK_EMAIL = os.environ.get("SHOUNAK_EMAIL")
SHOUNAK_EMAIL_PASSWORD = os.environ.get("SHOUNAK_EMAIL_PASSWORD")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


def send_email(email, message):
    with smtplib.SMTP('smtp.gmail.com') as connection:
        connection.starttls()
        connection.login(SHOUNAK_EMAIL, SHOUNAK_EMAIL_PASSWORD)
        connection.sendmail(SHOUNAK_EMAIL,
                            f"{email}",
                            f"Subject: Password Reset Code\n\nHi !!\n Your password reset code is {message} \n\n"                            
                            f"Thanks and Regards,\n(On behalf of Indomitable Tech)\nShounak Deshpande\n9970536215")


class UsersDB(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    registration_date = db.Column(db.String(100), nullable=False)
    # relationship call
    user_tasks = relationship('TasksDB', back_populates='tasks')


class TasksDB(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(250), nullable=False)
    subtask_name = db.Column(db.String(250), nullable=False)
    delegated_to = db.Column(db.String(250), nullable=False)
    task_start_date = db.Column(db.String(250), nullable=False)
    task_completed_date = db.Column(db.String(250), nullable=False)
    status = db.Column(db.String(250), nullable=False)
    notes = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    tasks = relationship('UsersDB', back_populates='user_tasks')


class FeedbackFormDB(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=False)
    commentator_name = db.Column(db.Text, nullable=False)
    commentator_email = db.Column(db.Text, nullable=False)
    comment_date = db.Column(db.String(100), nullable=False)


db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return UsersDB.query.get(int(user_id))


@app.route("/", methods=["GET", "POST"])
def home():
    login_form = LoginUser()
    if login_form.submit.data and login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        if UsersDB.query.filter_by(email=email).first():
            user = UsersDB.query.filter_by(email=email).first()
            if check_password_hash(user.password, password):
                login_user(user)
                load_user(user.id)
                return redirect(url_for('todo'))
            else:
                flash("Wrong Password")
                return redirect(url_for('home'))
        else:
            flash("User not registered. Please Register.")
            return redirect(url_for('home'))

    return render_template("index.html", login_form=login_form,current_user=current_user,
                           logged_in=current_user.is_authenticated)


@app.route("/register", methods=["POST","GET"])
def register():
    register_form = RegisterUser()
    if register_form.submit.data and register_form.validate_on_submit():
        email = register_form.email.data
        username = register_form.username.data
        if UsersDB.query.filter_by(email=email).first():
            flash("Email already registered. Please Login instead.")
            return redirect(url_for('home'))
        elif UsersDB.query.filter_by(username=username).first():
            flash("Username already exists. Please select another username.")
            return redirect(url_for('home'))
        else:
            new_user = UsersDB(email=register_form.email.data,
                               username=register_form.username.data,
                               password=generate_password_hash(register_form.password.data,
                                                               method='pbkdf2:sha256',
                                                               salt_length=8),
                               registration_date=datetime.datetime.now().strftime("%d-%B-%Y at %H:%M:%S %p"))
            db.session.add(new_user)
            db.session.commit()
            flash('Registration Successful. Please Login using your Credentials')
            return redirect(url_for('home'))
    return render_template("register.html", register_form=register_form,current_user=current_user,
                           logged_in=current_user.is_authenticated)




@app.route("/send_code",methods=["POST","GET"])
def send_code():
    forgot_password = ForgotPassword()
    if forgot_password.validate_on_submit():
        email = forgot_password.email.data
        code = str(random.choice(list(range(1000, 10000))))
        send_email(email=email, message=code)
        email_code = email+'&'+code
        return redirect(url_for('forgot_password', email_code=email_code))
    return render_template("send_code.html", forgot_password=forgot_password, logged_in=current_user.is_authenticated,current_user=current_user)

# send_email(email, message)
@app.route("/forgot_password/<email_code>",methods=["POST","GET"])
def forgot_password(email_code):
    code_verification = CodeVerication()
    email,code = email_code.split("&")
    if code_verification.validate_on_submit():
        if str(code_verification.code.data) == code:
            return redirect(url_for('reset_password',email=email))
        else:
            flash('Wrong Code Entered')
            redirect(url_for('home'))

    return render_template("enter_code.html", logged_in=current_user.is_authenticated, code_verification=code_verification,current_user=current_user)


@app.route("/reset_password/<email>",methods=["POST","GET"])
def reset_password(email):
    print(email)
    reset_password = ResetPassword()
    user = UsersDB.query.filter_by(email=email).first()
    print(user.username)
    if reset_password.validate_on_submit():

        user.password = generate_password_hash(reset_password.new_password.data,
                               method='pbkdf2:sha256',
                               salt_length=8)
        db.session.commit()
        flash('Password reset successfully')
        return redirect(url_for('home'))
    return render_template("reset_password.html", logged_in=current_user.is_authenticated,current_user=current_user,
                           reset_password=reset_password)


@app.route("/todo", methods=["GET", "POST"])
@login_required
def todo():
    display_tasks = TasksDB.query.filter_by(user_id=current_user.id).all()
    return render_template("todo.html", display_tasks=display_tasks, logged_in=current_user.is_authenticated,current_user=current_user)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_task():
    task_form = TaskForm()
    if task_form.validate_on_submit():
        new_task = TasksDB(task_name=task_form.task_name.data,
                           subtask_name=task_form.subtask_name.data,
                           delegated_to=task_form.delegated_to.data,
                           task_start_date=datetime.datetime.now().strftime("%d-%B-%Y at %H:%M:%S %p"),
                           task_completed_date=task_form.task_completed_date.data,
                           status=task_form.status.data,
                           notes=task_form.notes.data,
                           user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('todo'))
    return render_template("task_form.html", task_form=task_form, task='add', logged_in=current_user.is_authenticated,current_user=current_user)


@app.route("/edit/<int:index>", methods=["GET", "POST"])
@login_required
def edit_task(index):
    current_task = TasksDB.query.filter_by(id=index).first()
    task_form = TaskForm(task_name=current_task.task_name,
                         subtask_name=current_task.subtask_name,
                         delegated_to=current_task.delegated_to,
                         task_completed_date=current_task.task_completed_date,
                         status=current_task.status,
                         notes=current_task.notes)
    if task_form.validate_on_submit():
        current_task.task_name = task_form.task_name.data
        current_task.subtask_name = task_form.subtask_name.data
        current_task.delegated_to = task_form.delegated_to.data
        current_task.task_completed_date = task_form.task_completed_date.data
        current_task.status = task_form.status.data
        current_task.notes = task_form.notes.data
        db.session.commit()
        return redirect(url_for('todo'))
    return render_template("task_form.html", task_form=task_form, task='edit', logged_in=current_user.is_authenticated,current_user=current_user)


@app.route("/delete/<int:index>", methods=["GET", "POST"])
@login_required
def delete_task(index):
    current_task = TasksDB.query.filter_by(id=index).first()
    db.session.delete(current_task)
    db.session.commit()
    return redirect(url_for("todo"))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Successfully Logged Out")
    return redirect(url_for('home'))


@app.route("/about", methods=["GET", "POST"])
def about():
    feedback_form = FeedbackForm()

    if feedback_form.validate_on_submit():
        comment_entry = FeedbackFormDB(comment=feedback_form.comment.data,
                                       commentator_name=feedback_form.commentator_name.data,
                                       commentator_email=feedback_form.commentator_email.data,
                                       comment_date=datetime.datetime.now().strftime("%d-%B-%Y at %H:%M:%S %p"))
        db.session.add(comment_entry)
        db.session.commit()
    feedback_display = FeedbackFormDB.query.all()
    return render_template("about.html", feedback_form=feedback_form, feedback_display=feedback_display,
                           logged_in=current_user.is_authenticated,current_user=current_user)




if __name__ == "__main__":
    app.run(debug=True)
