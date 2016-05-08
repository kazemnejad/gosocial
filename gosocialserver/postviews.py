from flask import render_template, g

from gosocialserver.models import Post
from gosocialserver.server import app


@app.route("/")
def index():
    posts = Post.get_main_page_posts()
    return render_template("home.html", posts=posts, user=g.user)
