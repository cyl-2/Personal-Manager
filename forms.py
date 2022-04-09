from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators, SelectField, TextAreaField, RadioField
from wtforms.widgets import TextArea
from wtforms.validators import InputRequired, EqualTo
from wtforms.fields.html5 import DateField
from datetime import datetime

class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=5, max=25)])
    password = PasswordField("Password", validators=[InputRequired()])
    password2 = PasswordField("Confirm password", validators=[InputRequired("Password doesn't match"), EqualTo("password")])
    email = StringField("Email Address", [validators.Length(min=6, max=100)])
    accept_rules = BooleanField("I accept the terms and conditions", validators=[InputRequired()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired("Username doesn't exist")])
    password = PasswordField("Password", validators=[InputRequired()])
    password2 = PasswordField("Confirm password", validators=[InputRequired("Password doesn't match"), EqualTo("password")])
    submit = SubmitField("Login")

class TaskForm(FlaskForm):
    task = TextAreaField("Enter task", validators=[InputRequired("Please enter in a task")], widget=TextArea())
    location = StringField("Where does the task take place? ", default="")
    task_date = DateField("Date of task", validators=[InputRequired()])
    submit = SubmitField("Add task")

class DiaryForm(FlaskForm):
    entry = TextAreaField("Diary Entry", validators=[InputRequired()], widget=TextArea())
    title = StringField("Title", validators=[InputRequired()])
    weather = StringField("Weather", [validators.Length(min=0, max=25)])
    date = DateField("Today's date", default=datetime.now().date(), validators=[InputRequired()])
    submit = SubmitField("Save diary")

class PasswordForm(FlaskForm):
    new_password = PasswordField("New Password", validators=[InputRequired()])
    password2 = PasswordField("Confirm new password", validators=[InputRequired("Password doesn't match"), EqualTo("new_password")])
    submit = SubmitField("Change password")

class DeleteAccForm(FlaskForm):
    reason = StringField("Reason for deleting:", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])
    password2 = PasswordField("Confirm password:", validators=[InputRequired("Password doesn't match"), EqualTo("password")])
    submit = SubmitField("Submit")

class ResetPasswordForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired("Username doesn't exist")])
    email = StringField("Email Address", validators=[InputRequired("Please fill in an email address")])
    submit = SubmitField("Change password")

class CodeForm(FlaskForm):
    code = StringField('Enter the 5 digit code here', validators=[InputRequired("Wrong code")])
    submit = SubmitField("Submit")

class SurveyForm(FlaskForm):
    likeness = RadioField("Do you enjoy using this website?", 
    choices = [("yes", "Yes"),
                ("no", "No"),
                ("depends on my mood", "Depends on my mood")], validators=[InputRequired()])

    navigation = RadioField("Is the website easy to navigate?", 
    choices = [("yes", "Yes"),
                ("no", "No"),
                ("easier than finding my lost socks", "Easier than finding my lost socks")], validators=[InputRequired()])

    feature = RadioField("Which feature do you like better?", 
    choices = [("task manager", "Task Manager"),
                ("diary", "Diary"),
                ("they all suck", "They all suck")], validators=[InputRequired()])

    occurrence = RadioField("How often would you use this website?", 
    choices = [("every day", "Every day"),
                ("three days a week", "Three days a week"),
                ("twice a month", "Twice a month"),
                ("once a year", "Once a year")], validators=[InputRequired()])

    recommend = RadioField("Would you recommend this website to your family/friends?", 
    choices = [("yes", "Yes"),
                ("no", "No"),
                ("never", "Never")], validators=[InputRequired()])
    submit = SubmitField("Submit")

class ContactForm(FlaskForm):
    email = StringField(validators=[InputRequired()])
    name = StringField(validators=[InputRequired()])
    subject = StringField(validators=[InputRequired()])
    message = TextAreaField(validators=[InputRequired()], widget=TextArea())
    submit = SubmitField("Send message")

class ReplyForm(FlaskForm):
    email = StringField(validators=[InputRequired()])
    subject = StringField(validators=[InputRequired()])
    message = TextAreaField(validators=[InputRequired()], widget=TextArea())
    submit = SubmitField("Send message")