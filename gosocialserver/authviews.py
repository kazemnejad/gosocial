from functools import wraps

from flask import g, redirect, request, url_for, session, flash, render_template

from gosocialserver.models import User
from gosocialserver.server import app


@app.before_request
def load_user():
    if session["user_id"]:
        user = User.get_by_id(session["user_id"])
    else:
        user = None

    g.user = user


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('/auth/login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/auth/login", methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for("/"))

    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.check_user(username, password)
        if not user:
            error = "Invalid credentials"
        else:
            g.user = user
            flash("You were successfully logged in")
            return redirect(url_for("index"))

    return render_template("", errors=[error] if error else [])
