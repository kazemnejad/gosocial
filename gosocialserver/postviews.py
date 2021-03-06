import datetime
import os
import random

from flask import render_template, g, request, current_app, url_for, make_response, abort, redirect

import gosocialserver.config as config
from gosocialserver.models import Post, Like, Dislike, Comment
from gosocialserver.server import app
from gosocialserver.utils import login_required


@app.route("/")
def index():
    posts = Post.get_main_page_posts()
    return render_template("home.html", posts=posts, user=g.user)


@app.route("/posts/<int:post_id>", methods=['GET'])
def show_post(post_id):
    post = Post.get_by_id(post_id)
    if not post:
        abort(404)

    like_count = Like.get_count_for(post)
    dislike_count = Dislike.get_count_for(post)
    image_none = False
    if not post.image:
        post.image = config.DEFAULT_POST_IMAGE
        image_none = True

    return render_template("postview.html",
                           post=post,
                           like_count=like_count,
                           dislike_count=dislike_count,
                           comments=render_comments(post.comments),
                           user=g.user,
                           image_none=image_none)


@app.route("/posts/add", methods=['GET', 'POST'])
@login_required
def add_post():
    errors = []
    if request.method == 'POST':
        title = request.form['title'] if 'title' in request.form else None
        body = request.form['editor-body'] if 'editor-body' in request.form else None
        image_file = request.files['image'] if 'image' in request.files else None

        address = None
        if image_file and title and len(title) > 0:
            if allowed_file(image_file.filename):
                address, error = save_file(image_file, os.path.join("media", "upload"))
                if address == '' or error != '':
                    abort(403)
            else:
                abort(403)

        if not title or len(title) == 0:
            errors.append("You should provide Title")

        if not body and not image_file:
            errors.append("You should provide at least one picture or body")

        if len(errors) == 0:
            post = Post.new_post(title, body, address, g.user)
            return redirect(url_for('show_post', post_id=post.id))

    return render_template('addpost.html', user=g.user, errors=errors)


@app.route("/posts/<int:post_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.get_by_id(post_id)
    if not post:
        abort(404)

    if post.author.id != g.user.id:
        abort(403)

    errors = []
    if request.method == 'POST':
        title = request.form['title'] if 'title' in request.form else None
        body = request.form['editor-body'] if 'editor-body' in request.form else None
        image_file = request.files['image'] if 'image' in request.files else None

        address = None
        if image_file and title and len(title) > 0:
            if allowed_file(image_file.filename):
                address, error = save_file(image_file, os.path.join("media", "upload"))
                if address == '' or error != '':
                    abort(403)
            else:
                abort(403)

        if not title or len(title) == 0:
            errors.append("You should provide Title")

        if not body and not image_file:
            errors.append("You should provide at least one picture or body")

        if len(errors) == 0:
            post.title = title
            post.body = body if body and len(body) > 0 else None
            if address:
                post.image = address

            post.save_or_update()

            return redirect(url_for('show_post', post_id=post.id))

    return render_template('addpost.html', post=post, user=g.user, errors=errors)


@app.route("/posts/<int:post_id>/delete", methods=['GET'])
@login_required
def delete_post(post_id):
    post = Post.get_by_id(post_id)
    if not post:
        abort(404)

    if post.author.id != g.user.id:
        abort(403)

    post.delete()
    return redirect(url_for("profile", username=post.author.username))


@app.route("/posts/<int:post_id>/comments/add", methods=['POST'])
@app.route("/posts/<int:post_id>/comments/add/<int:parent_id>", methods=['POST'])
@login_required
def add_comment(post_id, parent_id=None):
    comment_post = post = Post.get_by_id(post_id)
    if not post:
        abort(404)

    parent = None
    if parent_id:
        parent = Comment.get_by_id(parent_id)
        if not parent:
            abort(404)
        comment_post = None

    cm_body = request.form['body']
    if len(cm_body) < 1:
        abort(400)

    Comment.new_comment(cm_body, parent, comment_post, g.user)
    return render_comments(post.comments)


@app.route('/ckupload/', methods=['POST', 'OPTIONS'])
def ckupload():
    error = ''
    url = ''

    callback = request.args.get("CKEditorFuncNum")
    if request.method == 'POST' and 'upload' in request.files:
        f = request.files['upload']
        if allowed_file(f.filename):
            address, error = save_file(request.files['upload'], os.path.join('media', 'upload'))
            url = url_for('static', filename=address)
        else:
            error = "Unable to upload file"
    else:
        error = 'post error'

    res = """<script type="text/javascript">
             window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
             </script>""" % (callback, url, error)

    response = make_response(res)
    response.headers["Content-Type"] = "text/html"

    return response


def render_comments(comments, level=1):
    is_child = level > 1
    result = '<ul %s >' % ('style="width: 90%; margin-left: 10%;"' if is_child else "")
    for comment in comments:
        result += "<li>"
        result += render_comment(comment, level)
        if len(comment.children) != 0:
            result += render_comments(comment.children, level + 1)
        result += "</li>"
    result += "</ul>"
    return result


def render_comment(comment, level):
    return app.jinja_env.get_template("comment.html").render(comment=comment, is_child=level > 1)


def save_file(file_obj, parent_dir_path):
    error = ''
    address = ''

    file_name, file_extension = os.path.splitext(file_obj.filename)
    rnd_name = '%s%s' % (gen_rnd_filename(), file_extension)

    file_path = os.path.join(parent_dir_path, rnd_name)
    full_file_path = os.path.join(current_app.static_folder, file_path)
    dir_name = os.path.dirname(full_file_path)

    if not os.path.exists(dir_name):
        try:
            os.makedirs(dir_name)
        except:
            error = 'Error while uploading image'
    elif not os.access(dir_name, os.W_OK):
        error = 'Error while uploading image'
    if not error:
        file_obj.save(full_file_path)
        address = file_path

    return address, error


def gen_rnd_filename():
    filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in config.ALLOWED_EXTENSIONS
