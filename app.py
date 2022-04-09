from flask import Flask, render_template, redirect, url_for, session, g, flash, Markup, request, make_response
from forms import RegistrationForm, TaskForm, DiaryForm, LoginForm, PasswordForm, DeleteAccForm, ResetPasswordForm, CodeForm, SurveyForm, ContactForm, ReplyForm
from database import get_db, close_db
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
from flask_mail import Mail, Message
from random import sample
from itertools import * 

# BEST VIEWED ON A DEVICE BIGGER THAN AN IPAD

''' There are two type of users - admin and regular ones
TO GET ACCESS TO ADMIN ACCOUNT, LOGIN AS :
username = admin
password = Admin123
Admin can view survey results and read/reply to queries from users.

TO GET ACCESS AS A REGULAR USER:
Register for an account!
Regular users can use the task manager and diary feature. '''

app = Flask(__name__)
app.config["SECRET_KEY"] = "so-secret-tea"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Email idea from https://pythonhosted.org/Flask-Mail/ ; I copied some code but modified for my own use
mail= Mail(app)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'no.reply.please.and.thank.you@gmail.com'
app.config['MAIL_PASSWORD'] = 'justanemailformyflaskapp'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail.init_app(app)

@app.teardown_appcontext
def close_db_at_end_of_requests(e=None):
    close_db(e)

@app.before_request
def logged_in():
    g.user = session.get("username", None)

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("login"))
        return view(**kwargs)
    return wrapped_view

def admin_only(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user != "admin":
            return redirect(url_for("profile"))
        return view(**kwargs)
    return wrapped_view

# 404 error page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('oh_no.html', title="Error"), 404

# Home page
@app.route("/")
def index():
    form = TaskForm()
    form2 = DiaryForm()
    return render_template("index.html", title="Home",form=form, form2=form2)

# Register for an account
@app.route("/registration", methods=["GET", "POST"])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()
        password = form.password.data
        code = "None"

        db = get_db()
        if db.execute("""SELECT * FROM users WHERE email =?;""", (email,)).fetchone() is not None:
            form.email.errors.append("Sorry, the email you entered already exists, please use another email.")
        elif db.execute("""SELECT * FROM users WHERE username =?;""", (username,)).fetchone() is not None:
            form.username.errors.append("Sorry, the username you entered already exists, please create a new username.")
        elif password.isupper() or password.isdigit() or password.islower() or password.isalpha():
            form.password.errors.append("Create a STRONG password with one uppercase character, one lowercase character and one number")
        else:
            db.execute("""INSERT INTO users (username, email, password, code)
                        VALUES (?,?,?,?);""", (username, email, generate_password_hash(password), code))
            db.commit()
            flash("Successful Registration! Please login now")
            return redirect( url_for("login"))
    return render_template("register.html", form=form, title="Register")

# Shows terms and conditions
@app.route("/terms")
def terms():
    return render_template("terms_con.html", title="Terms and Conditions")

# Login to account
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data
        
        db = get_db() 
        user = db.execute("""SELECT * FROM users WHERE username = ?;""", (username,)).fetchone()

        if 'counter' not in session:
            session['counter'] = 0

        if user is None:
            form.username.errors.append("Username doesn't exist, please check your spelling")
        elif not check_password_hash(user["password"], password):
            form.password.errors.append("Incorrect password")
            session['counter'] = session.get('counter') + 1
            if session.get('counter')==3:
                flash(Markup('Oh no, are you having trouble logging in? Click <a href="forgot_password">here</a> to reset your password.'))
                session.pop('counter', None)
        else:
            session.clear()
            session["username"] = username
            if username == "admin":
                return redirect(url_for("admin"))
            else:
                return redirect(url_for("profile"))
    return render_template("login.html", form=form, title="Login")

# Logout from account
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# Change password
@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = PasswordForm()
    if form.validate_on_submit():
        new_password = form.new_password.data

        db = get_db() 
        user = db.execute("""SELECT * FROM users WHERE username = ?;""", (g.user,)).fetchone()

        if new_password.isupper() or new_password.islower() or new_password.isdigit():
            form.new_password.errors.append("Create a STRONG password with one uppercase character, one lowercase character and one number")
        else:
            db.execute("""UPDATE users SET password=? WHERE username=?;""", (generate_password_hash(new_password),g.user))
            db.commit()
            session.clear()
            flash("Successfully changed password! Please login now.")
            return redirect(url_for("login"))
    return render_template("change_password.html", title ="Change password", form=form)
    
# Leads user to reset password
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()
        pin = sample(range(10000, 99999), 1)

        random_code = ""
        for i in pin:
            random_code += str(i)

        db = get_db() 
        user = db.execute("""SELECT * FROM users WHERE username = ?;""", (username,)).fetchone()

        if user is None:
            form.username.errors.append("There is no account associated with this username, please check your spelling")
        elif email != user["email"]:
            form.email.errors.append("The username is not associated with this email, please check your spelling")
        else:
            db.execute("""UPDATE users SET code=? WHERE username=?;""", (random_code,username))
            db.commit()
            msg = Message(f"Hello, {username}", sender='no.reply.please.and.thank.you@gmail.com', recipients=[user["email"]])
            msg.body = f"""
            Hello darling, 
            I heard you lost your password. 
            To reset your password, enter this code: 
            {random_code}"""
            mail.send(msg)
            flash("Great news! An email containing a 5 digit code has been sent to your email account. Enter the code below!")
            return redirect(url_for("confirm_code", username=username))
    return render_template("forgot_password.html", form=form, title= "Forgot Password")

if __name__ == '__main__':
   app.run(debug = True)

# Checks whether the code the user received corresponds to the one in the database
@app.route("/confirm_code/<username>", methods=["GET", "POST"])
def confirm_code(username):
    form = CodeForm()
    user = None
    if form.validate_on_submit():
        code = form.code.data.strip()
        
        db = get_db() 
        user = db.execute("""SELECT * FROM users WHERE username = ?;""", (username,)).fetchone()

        if code != user["code"]:
            form.code.errors.append("Oh no, that's not the code in your email!")
        else:
            flash("Code correct! Now you can reset your password :)")
            session["username"] = username
            return redirect(url_for("change_password"))
    return render_template("confirm_code.html", form=form, title= "Confirm code")

# Main profile
@app.route("/profile")
@login_required
def profile():
    db = get_db() 
    user = db.execute("""SELECT * FROM users WHERE username = ?;""", (g.user,)).fetchone()
    return render_template("profile.html", title="My Profile", user=user)

# Delete account
@app.route("/delete_account", methods=["GET", "POST"])
@login_required
def delete_acc():
    form = DeleteAccForm()
    if form.validate_on_submit():
        password = form.password.data
        reason = form.reason.data

        db = get_db() 
        user = db.execute("""SELECT * FROM users WHERE username = ?;""", (g.user,)).fetchone()

        if not check_password_hash(user["password"], password):
            form.password.errors.append("Incorrect password")
        else:
            db.execute("""DELETE FROM tasks WHERE username=?;""", (g.user,))
            db.execute("""DELETE FROM users WHERE username=?;""", (g.user,))
            db.execute("""DELETE FROM diary WHERE username=?;""", (g.user,))
            db.commit()
            session.clear()
            return render_template("final_goodbye.html", reason=reason)
    return render_template("goodbye.html", title ="Delete Account", form=form)

# Task manager page
@app.route("/task_manager", methods=["GET", "POST"])
@login_required
def task_manager():
    form = TaskForm()
    tasks = None
    if form.validate_on_submit():
        task = form.task.data
        location = form.location.data
        task_date = form.task_date.data

        db = get_db()
        tasks = db.execute("""SELECT * FROM tasks WHERE username=?;""", (g.user,)).fetchall()

        if task_date < datetime.now().date():
            form.task_date.errors.append("Date must be in the future") 
        else:
            db = get_db()
            db.execute("""INSERT INTO tasks (username, task, location, task_date)
                            VALUES (?,?,?,?);""", (g.user, task, location, task_date))
            db.commit()
            flash ("Yay! Task successfully added!")
            return redirect(url_for("task_manager"))
    else:
        db = get_db()
        tasks = db.execute("""SELECT * FROM tasks WHERE username=?;""", (g.user,)).fetchall()
    return render_template("task.html", form=form, title="My Task Manager", tasks=tasks)    

# Deletes task
@app.route("/delete_task/<int:id>")
@login_required
def delete_task(id):
    db = get_db()
    db.execute("""DELETE FROM tasks WHERE username =? AND task_id=?;""", (g.user,id)).fetchone()
    db.commit()
    flash ("Task deleted!")
    return redirect(url_for("task_manager"))

# Main diary page
@app.route("/my_diary", methods=["GET", "POST"])
@login_required
def my_diary():
    form = DiaryForm()
    diary = None
    if form.validate_on_submit():
        entry = form.entry.data
        weather = form.weather.data
        date = form.date.data
        title = form.title.data
        
        db = get_db()
        db.execute("""INSERT INTO diary (username, title, entry, weather, date)
                        VALUES (?,?,?,?,?);""", (g.user, title, entry, weather, date))
        db.commit()

        entry = db.execute("""SELECT * FROM diary WHERE entry_id in 
                                (SELECT max(entry_id) FROM diary WHERE username=?);""", (g.user,)).fetchone()
        flash ("Yay! You just successfully submitted a diary entry!")  # got the flash idea from : https://flask.palletsprojects.com/en/1.1.x/patterns/flashing/ , copied some code.
        return redirect(url_for("show_diary", id=entry["entry_id"]))
    else:
        db = get_db()
        diary = db.execute("""SELECT * FROM diary WHERE username=?;""", (g.user,)).fetchall()
    return render_template("diary.html", form=form, title="My Diary", diary=diary)

# Opens existing diary entry in another webpage
@app.route("/show_diary/<int:id>")
@login_required
def show_diary(id):
    db = get_db()
    entry = db.execute("""SELECT * FROM diary WHERE username=? AND entry_id=?;""", (g.user,id)).fetchone()
    return render_template("show_diary.html",title="My Diary", entry=entry)

# Edits existing diary entry
@app.route("/edit_diary/<int:id>", methods=["GET", "POST"])
@login_required
def edit_diary(id):
    form = DiaryForm()
    entry = None
    if form.validate_on_submit():
        entry = form.entry.data
        weather = form.weather.data
        date = form.date.data
        title = form.title.data

        db = get_db()
        db.execute("""UPDATE diary SET title=?, entry=?, weather=?, date=? WHERE entry_id=?;""", (title, entry, weather, date, id))
        db.commit()

        flash ("Diary entry updated!")
        return redirect(url_for("show_diary", id=id))
    else:
        db = get_db()
        entry = db.execute("""SELECT * FROM diary WHERE username=? AND entry_id=?;""", (g.user, id)).fetchone()
        form.entry.data = entry['entry']
    return render_template("edit_diary.html", title ="Edit Diary", form=form, entry=entry)

# Deletes diary entry
@app.route("/delete_diary/<int:id>")
@login_required        
def delete_diary(id):
    db = get_db()
    db.execute("""DELETE FROM diary WHERE username=? AND entry_id=?;""", (g.user,id)).fetchone()
    db.commit()
    flash ("Diary entry deleted!")
    return redirect(url_for("my_diary"))

# Contact form so users can communicate with me
# I saved the data to a database and also sent an email containing the data to my own email 
# The emails to myself acts as a back up in case admin deletes an unresponded query from the database
@app.route("/contact_us", methods=["GET", "POST"])
def contact_us():
    form = ContactForm()
    if form.validate_on_submit() == False:
      flash('All fields are required.')
    else:
        name = form.name.data
        email = form.email.data.lower().strip()
        subject = form.subject.data
        message = form.message.data
        date = datetime.now().date()

        db = get_db()
        db.execute("""INSERT INTO user_queries (name, email, subject, message, date)
                        VALUES (?,?,?,?,?);""", (name, email, subject, message, date))
        db.commit()

        msg = Message(subject, sender='no.reply.please.and.thank.you@gmail.com', recipients=['no.reply.please.and.thank.you@gmail.com'])   
        msg.body = f"""
        From: {name} <{email}>
        {message}
        """
        mail.send(msg)
        flash("Message sent. We will reply to you in 2-3 business days.")
    return render_template("contact_us.html",form=form, title="Contact Us")

# Admin account
@app.route("/admin")
@admin_only
def admin():
    db = get_db()
    queries = db.execute("""SELECT * FROM user_queries;""").fetchall()
    return render_template("admin_account.html",queries=queries)

# Delete queries from users
@app.route("/delete_query/<int:id>")
@admin_only
def delete_query(id):
    db = get_db()
    db.execute("""DELETE FROM user_queries WHERE query_id=?;""", (id,)).fetchone()
    db.commit()
    flash ("Deleted!")
    return redirect(url_for("admin"))

# Admin can reply to user queries
@app.route("/reply_email/<id>", methods=["GET", "POST"])
@admin_only
def reply_email(id):
    form = ReplyForm()
    db = get_db()
    query = db.execute("""SELECT * FROM user_queries WHERE query_id=?;""", (id,)).fetchone()

    if form.validate_on_submit() == False:
        flash('All fields are required.')
    else:
        email = form.email.data
        subject = form.subject.data
        message = form.message.data

        msg = Message("Replying to your query: "+subject, sender='no.reply.please.and.thank.you@gmail.com', recipients=[email])   
        msg.body = f"""{message}"""
        mail.send(msg)
        flash("Message sent successfully.")
    return render_template("reply_email.html",form=form, title="Reply", query=query)

# Survey to get user input about my flask app
@app.route("/survey", methods=["GET", "POST"])
@login_required
def survey():
    if request.cookies.get("submitted") == "yes":
        flash("You have already submitted a survey form, thank you!")
        return render_template("survey_success.html", title ="Survey Submitted")
    form = SurveyForm()
    if form.validate_on_submit():
        likeness = form.likeness.data
        navigation = form.navigation.data
        feature = form.feature.data
        occurrence = form.occurrence.data
        recommend = form.recommend.data

        db = get_db()
        db.execute("""INSERT INTO survey (likeness,navigation,feature,occurrence,recommend)
                        VALUES (?,?,?,?,?);""", (likeness,navigation,feature,occurrence,recommend))
        db.commit()

        response = make_response(render_template("survey_success.html", title ="Survey"))
        response.set_cookie("submitted", "yes")  
        return response
    return render_template("survey.html", title ="Survey", form=form)

# Just a lot of SQL to present survey results in a webpage
@app.route("/survey_results")
@admin_only
def survey_results():
    db = get_db()

    total = db.execute("""SELECT count(*) FROM survey;""")
    like1 = db.execute("""SELECT count(*) FROM survey WHERE likeness="yes";""")
    like2 = db.execute("""SELECT count(*) FROM survey WHERE likeness="depends on my mood";""")
    navigate1 = db.execute("""SELECT count(*) FROM survey WHERE navigation="yes";""")
    navigate2 = db.execute("""SELECT count(*) FROM survey WHERE navigation="easier than finding my lost socks";""")
    feature1 = db.execute("""SELECT count(*) FROM survey WHERE feature="task manager";""")
    feature2 = db.execute("""SELECT count(*) FROM survey WHERE feature="diary";""")
    occurrence1 = db.execute("""SELECT count(*) FROM survey WHERE occurrence="every day";""")
    occurrence2 = db.execute("""SELECT count(*) FROM survey WHERE occurrence="three days a week";""")
    occurrence3 = db.execute("""SELECT count(*) FROM survey WHERE occurrence="twice a month";""")
    recommend1 = db.execute("""SELECT count(*) FROM survey WHERE recommend="yes";""")
    recommend2 = db.execute("""SELECT count(*) FROM survey WHERE recommend="no";""")

    for x in total:
        total_users = x["count(*)"]

    for (x,y) in zip(like1,like2):
        like_website = round(x["count(*)"]/total_users*100, 2)
        like_website_depends_on_mood = round(y["count(*)"]/total_users*100, 2)
    dislike_website = round(100 - (like_website + like_website_depends_on_mood),2)

    for (x,y) in zip(navigate1, navigate2):
        easy_to_navigate_than_socks = round(x["count(*)"]/total_users*100, 2)
        easy_to_navigate = round(y["count(*)"]/total_users*100, 2)
    hard_to_navigate = round(100-(easy_to_navigate + easy_to_navigate_than_socks),2)

    for (x,y) in zip(feature1,feature2):
        feature_task = round(x["count(*)"]/total_users*100, 2)
        feature_diary = round(y["count(*)"]/total_users*100, 2)    
    feature_sucks = round(100 - (feature_task +feature_diary),2)

    for (x,y,z) in zip(occurrence1,occurrence2,occurrence3):
        daily = round(x["count(*)"]/total_users*100, 2)
        sometimes = round(y["count(*)"]/total_users*100, 2)
        occasional = round(z["count(*)"]/total_users*100, 2)
    yearly = round(100-(daily+sometimes+occasional),2)

    for (x,y) in zip(recommend1, recommend2):
        recommend_yes = round(x["count(*)"]/total_users*100, 2)
        recommend_no = round(y["count(*)"]/total_users*100, 2)
    recommend_never = round(100-(recommend_yes+recommend_no),2)

    return render_template("survey_results.html", title ="Admin", total_users=total_users, like_website=like_website,
    like_website_depends_on_mood=like_website_depends_on_mood, dislike_website=dislike_website, easy_to_navigate=easy_to_navigate,
    easy_to_navigate_than_socks=easy_to_navigate_than_socks,hard_to_navigate=hard_to_navigate,feature_task=feature_task,feature_diary=feature_diary,
    feature_sucks=feature_sucks,daily=daily,sometimes=sometimes,occasional=occasional,yearly=yearly,recommend_yes=recommend_yes,
    recommend_no=recommend_no, recommend_never=recommend_never)