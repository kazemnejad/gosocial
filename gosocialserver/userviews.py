from functools import wraps

import os
from PIL import Image
from flask import g, redirect, request, url_for, session, flash, render_template, escape, abort, current_app

import gosocialserver.config as config
from gosocialserver.auth import AuthExceptions
from gosocialserver.models import User, Post
from gosocialserver.orm import Select, column
from gosocialserver.postviews import allowed_file, save_file
from gosocialserver.server import app
from gosocialserver.utils import login_required


@app.before_request
def load_user():
    if str(request.path).startswith("static"):
        return

    if session.get("user_id", None):
        user = User.get_by_id(session["user_id"])
    else:
        user = None

    g.user = user


@app.route("/auth/login", methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for("index"))

    error = None
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['pass']

        user = User.check_user(username, password)
        if not user:
            error = "Invalid credentials"
        else:
            session['user_id'] = user.id
            g.user = user
            flash("You were successfully logged in")
            return redirect(url_for("index"))

    return render_template("loginpage.html", errors=[error] if error else [])


@app.route("/auth/register", methods=['GET', 'POST'])
def register():
    if g.user:
        return redirect(url_for("index"))

    error = None
    if request.method == 'POST':
        username = escape(request.form['unname'])
        email = request.form['email']
        password = request.form['pass']
        first_name = request.form['fname']
        last_name = request.form['lname']

        try:
            user = User.new_user(username, email, password, first_name, last_name)
            if not user:
                error = "Unable to register1!"
            else:
                print(user.id)
                session['user_id'] = user.id
                g.user = user
                flash("You have successfully signed up!")
                return redirect(url_for("index"))
        except AuthExceptions.UserExistException:
            error = "Username or email exists!, try another one!"

    print(error)
    return render_template("loginpage.html", errors=[error] if error else [])


@app.route("/auth/logout", methods=['GET'])
def logout():
    session.pop('user_id', None)
    g.user = None
    flash('You were logged out')
    return redirect(url_for('index'))


@app.route("/users/<string:username>", methods=['GET'])
def profile(username):
    if len(username) == 0:
        abort(404)

    user = Select().star().From(User.table_name).filter(column("username").equal(username)).to_query().with_model(User).first()
    if not user:
        abort(404)

    posts = Select().star().From(Post.table_name).filter(column("user_id").equal(user.id)).to_query().with_model(Post).all()

    return render_template("profile.html", user=user, posts=posts, is_my_profile=(g.user and g.user.id == user.id))


@app.route("/users/<string:username>/edit", methods=["GET", "POST"])
@login_required
def edit_profile(username):
    if len(username) == 0:
        abort(404)

    user = Select().star().From(User.table_name).filter(column("username").equal(username)) \
        .to_query().with_model(User).first()
    if not user:
        abort(404)

    if g.user.id != user.id:
        abort(403)

    if request.method == "POST":
        first_name = request.form['fname']
        last_name = request.form['lname']
        profile_pic = request.files['profile_pic']

        address = None
        if profile_pic:
            if allowed_file(profile_pic.filename):
                address, error = save_file(profile_pic, os.path.join("media", "upload"))
                if address == '' or error != '':
                    abort(403)
                make_square(address)
            else:
                abort(403)

        user.first_name = first_name
        user.last_name = last_name
        if address:
            user.profile_pic = address

        user.save_or_update()
        return redirect(url_for('profile', username=username))

    return render_template("editprofile.html", user=user)


def make_square(address):
    full_path = os.path.join(current_app.static_folder, address)
    im = Image.open(full_path)
    width, height = im.size

    new_width = new_height = min(width, height)

    left = (width - new_width) / 2
    top = (height - new_height) / 2
    right = (width + new_width) / 2
    bottom = (height + new_height) / 2

    im.crop((left, top, right, bottom)).save(full_path)
