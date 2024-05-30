import os

from datetime import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta


# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///data.db")


@app.route("/")
def index():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template('login.html', message='Invalid Username or Password', message_color='red')

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template('login.html', message='Invalid Username or Password', message_color='red')

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return render_template('login.html', message='Invalid Username or Password', message_color='red')

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]


        # Redirect user to home page
        return redirect("/home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/home")
def home():
    result = db.execute("SELECT username FROM users WHERE id= :user_id", user_id=session["user_id"])
    name = result[0]["username"]

    result_colour = db.execute("SELECT theme FROM users WHERE id= :user_id", user_id=session["user_id"])
    theme_colour = result_colour[0]["theme"]

    to_do = db.execute("SELECT task_id, task_title, description, deadline_datetime, level FROM tasks WHERE user_id = :user_id ORDER BY deadline_datetime ASC;", user_id = session["user_id"])

    return render_template("home.html", name=name, theme_colour=theme_colour, to_do=to_do, datetime=datetime)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template('register.html', message='Please provide username', message_color='red')

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template('register.html', message='Please provide password', message_color='red')


        # Ensure confirmation password was submitted
        elif not request.form.get("confirmation"):
            return render_template('register.html', message='Please provide confirmation password', message_color='red')

        # Ensure password and confirmation password match
        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template('register.html', message='Password did not match', message_color='red')

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username doesnt exist yet
        if len(rows) != 0:
            return render_template('register.html', message='Username already exist', message_color='red')

        # Key into database, new user and password
        db.execute(
            "INSERT INTO users (username, hash) VALUES(? , ?)", request.form.get("username"), generate_password_hash(request.form.get("password"))
        )
        # Redirect user to success page
        return redirect("/success")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("register.html")


@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/setting")
def setting():
    result_colour = db.execute("SELECT theme FROM users WHERE id= :user_id", user_id=session["user_id"])
    theme_colour = result_colour[0]["theme"]

    """Setting to change Username, password and Theme"""
    result = db.execute("SELECT username FROM users WHERE id= :user_id", user_id=session["user_id"])
    name = result[0]["username"]

    return render_template("setting.html", name=name, theme_colour=theme_colour)

@app.route("/change_username", methods=["GET", "POST"])
def change_username():
    result_colour = db.execute("SELECT theme FROM users WHERE id= :user_id", user_id=session["user_id"])
    theme_colour = result_colour[0]["theme"]

    if request.method == "POST":
        # Ensure new username was submitted
        if not request.form.get("new_username"):
            return render_template("change_username.html", message="Please provide new username", message_color='red', theme_colour=theme_colour)

        # Ensure confirmation username was submitted
        elif not request.form.get("new_confirmation_username"):
            return render_template("change_username.html", message="Please re-enter new username", message_color='red', theme_colour=theme_colour)

        # Ensure new username and confirmation username match
        elif request.form.get("new_username") != request.form.get("new_confirmation_username"):
            return render_template("change_username.html", message="Confirmation username did not match", message_color='red', theme_colour=theme_colour)


        # storing new username
        new_name = request.form.get("new_username")

        # Update new username into database
        db.execute(
            "UPDATE users SET username = :new_name WHERE id = :user_id", new_name=new_name, user_id = session["user_id"]
            )

        flash("Username Changed Successfully")
        return render_template("change_username.html",message="Username Changed Successfully", theme_colour=theme_colour, message_color='green')
    return render_template("change_username.html", theme_colour=theme_colour)


@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    result_colour = db.execute("SELECT theme FROM users WHERE id= :user_id", user_id=session["user_id"])
    theme_colour = result_colour[0]["theme"]

    if request.method == "POST":
        # Ensure old password was submitted
        if not request.form.get("old_password"):
            return render_template("change_password.html", message="Please provide old password", message_color='red', theme_colour=theme_colour)

        # Ensure new password was submitted
        elif not request.form.get("new_password"):
            return render_template("change_password.html", message="Please provide new password", message_color='red', theme_colour=theme_colour)

        # Ensure confirmation password was submitted
        elif not request.form.get("new_confirmation_password"):
            return render_template("change_password.html", message="Please re-enter new password", message_color='red', theme_colour=theme_colour)

        # Ensure old password and new password dont match
        elif request.form.get("old_password") == request.form.get("new_password"):
            return render_template("change_password.html", message="New password cannot be the same as Old password", message_color='red', theme_colour=theme_colour)

        # Ensure password and confirmation password match
        elif request.form.get("new_password") != request.form.get("new_confirmation_password"):
            return render_template("change_password.html", message="Confirmation password did not match", message_color='red', theme_colour=theme_colour)

        # Check if old password is actually correct
        old_hashed_password = db.execute("SELECT hash FROM users WHERE id = :user_id", user_id=session["user_id"])

        if not old_hashed_password or not check_password_hash(old_hashed_password[0]["hash"], request.form.get("old_password")):
            return render_template("change_password.html", message="Old password is incorrect", message_color='red', theme_colour=theme_colour)


        # Hash Password
        hash_password = generate_password_hash(request.form.get("new_password"))

        # Update new password into database
        db.execute(
            "UPDATE users SET hash = :hash_password WHERE id = :user_id", hash_password=hash_password, user_id = session["user_id"]
            )

        flash("Password Changed Successfully")
        return render_template("change_password.html",theme_colour=theme_colour, message="Password Changed Successfully", message_color='green')
    return render_template("change_password.html", theme_colour=theme_colour)

@app.route("/theme", methods=["GET", "POST"])
def theme():
    result_colour = db.execute("SELECT theme FROM users WHERE id= :user_id", user_id=session["user_id"])
    theme_colour = result_colour[0]["theme"]
    if request.method == "POST":
        if not request.form.get("colour"):
            return render_template("theme.html", message="Please Select a Theme", message_color='red', theme_colour=theme_colour)

        new_theme = request.form.get("colour")

        colour_mapping = {
            "blue": "#CFE0FE",
            "green" : "#CFFEED",
            "purple" : "#E5DAFE",
            "pink" : "#FED9FB",
            "orange" : "#FEDDC4",
            "yellow" : "#FEFEAC",
            "grey" :  "#D9D9D9"
        }
        db.execute(
            "UPDATE users SET theme = :theme WHERE id = :user_id", theme=colour_mapping[new_theme], user_id = session["user_id"]
            )

        session["theme_colour"] = colour_mapping[new_theme]
        return render_template("theme.html",message="Theme Changed Successfully", message_color='green', theme_colour=session["theme_colour"])
    return render_template("theme.html", theme_colour=theme_colour)

@app.route("/new_task", methods=["GET", "POST"])
def new_task():
    result_colour = db.execute("SELECT theme FROM users WHERE id= :user_id", user_id=session["user_id"])
    theme_colour = result_colour[0]["theme"]

    result = db.execute("SELECT username FROM users WHERE id= :user_id", user_id=session["user_id"])
    name = result[0]["username"]

    if request.method == "POST":
        # Ensure Title was submitted
        if not request.form.get("task_title"):
            return render_template('new_task.html', message='Please provide Task Title', message_color='red', name=name, theme_colour=theme_colour)

        # Ensure Dateline date was submitted
        elif not request.form.get("deadline_date"):
            return render_template('new_task.html', message='Please provide Date of Deadline', message_color='red', name=name, theme_colour=theme_colour)

        # Ensure Dateline time was submitted
        elif not request.form.get("deadline_time"):
            return render_template('new_task.html', message='Please provide Time of Deadline', message_color='red', name=name, theme_colour=theme_colour)

        # Ensure importance level was submitted
        elif not request.form.get("level"):
            return render_template('new_task.html', message='Please Select Importance level', message_color='red', name=name, theme_colour=theme_colour)


        #combining Date and Time
        date_time = request.form["deadline_date"] + ' ' + request.form["deadline_time"]


        # Key into database, new user and password
        db.execute(
            "INSERT INTO tasks (user_id, task_title, deadline_datetime, description, level) VALUES(? , ? , ? , ? , ?)", session["user_id"], request.form.get("task_title"), date_time, request.form.get("description"), request.form.get("level")
        )

        to_do = db.execute("SELECT task_id, task_title, description, deadline_datetime, level FROM tasks WHERE user_id = :user_id ORDER BY deadline_datetime ASC;", user_id = session["user_id"])

        return render_template("home.html", name=name, theme_colour=theme_colour, to_do=to_do, datetime=datetime)

    return render_template("new_task.html", theme_colour=theme_colour, name=name, datetime=datetime)


@app.route("/task/<int:task_id>/complete", methods=["GET", "POST"])
def complete_task(task_id):
    db.execute("UPDATE tasks SET level = 'completed' WHERE task_id = :task_id AND user_id= :user_id",  task_id=task_id, user_id= session["user_id"])

    result_colour = db.execute("SELECT theme FROM users WHERE id= :user_id", user_id=session["user_id"])
    theme_colour = result_colour[0]["theme"]

    result = db.execute("SELECT username FROM users WHERE id= :user_id", user_id=session["user_id"])
    name = result[0]["username"]

    to_do = db.execute("SELECT task_id, task_title, description, deadline_datetime, level FROM tasks WHERE user_id = :user_id ORDER BY deadline_datetime ASC;", user_id = session["user_id"])

    return render_template("home.html", name=name, theme_colour=theme_colour, to_do=to_do, datetime=datetime)


@app.route("/task/<int:task_id>/delete", methods=["GET", "POST"])
def delete_task(task_id):
    db.execute("DELETE FROM tasks WHERE task_id = :task_id AND user_id= :user_id",  task_id=task_id, user_id= session["user_id"])

    result_colour = db.execute("SELECT theme FROM users WHERE id= :user_id", user_id=session["user_id"])
    theme_colour = result_colour[0]["theme"]

    result = db.execute("SELECT username FROM users WHERE id= :user_id", user_id=session["user_id"])
    name = result[0]["username"]

    to_do = db.execute("SELECT task_id, task_title, description, deadline_datetime, level FROM tasks WHERE user_id = :user_id ORDER BY deadline_datetime ASC;", user_id = session["user_id"])

    return render_template("home.html", name=name, theme_colour=theme_colour, to_do=to_do, datetime=datetime)

@app.route("/refresh", methods=["GET", "POST"])
def refresh():

    result_colour = db.execute("SELECT theme FROM users WHERE id= :user_id", user_id=session["user_id"])
    theme_colour = result_colour[0]["theme"]

    result = db.execute("SELECT username FROM users WHERE id= :user_id", user_id=session["user_id"])
    name = result[0]["username"]

    to_do = db.execute("SELECT task_id, task_title, description, deadline_datetime, level FROM tasks WHERE user_id = :user_id ORDER BY deadline_datetime ASC;", user_id = session["user_id"])

    for task in to_do:
        deadline = datetime.strptime(task['deadline_datetime'], '%Y-%m-%d %H:%M')
        #https://www.geeksforgeeks.org/python-datetime-timedelta-function/
        if deadline - datetime.now() <= timedelta(days=1) and task['level'] != 'completed':
            db.execute("UPDATE tasks SET level = 'warning' WHERE task_id = :task_id AND user_id = :user_id", task_id=task['task_id'], user_id=session["user_id"])

    return render_template("home.html", name=name, theme_colour=theme_colour, to_do=to_do, datetime=datetime)
