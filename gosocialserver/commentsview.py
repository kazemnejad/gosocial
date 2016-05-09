from flask import abort, request, g

from gosocialserver.models import Post, Comment
from gosocialserver.server import app
from gosocialserver.userviews import login_required


@app.route("/posts/<int:post_id>/comments/add", methods=['POST'])
@app.route("/posts/<int:post_id>/comments/add/<int:parent_id>", methods=['POST'])
@login_required
def add_comment(post_id, parent_id=None):
    post = Post.get_by_id(post_id)
    if not post:
        abort(404)

    parent = None
    if parent_id:
        parent = Comment.get_by_id(parent_id)
        if not parent:
            abort(404)
        post = None

    cm_body = request.form['body']
    if len(cm_body) < 4:
        abort(400)

    comment = Comment.new_comment(cm_body,parent, post, g.user)
    if comment:
        return "0"
    else:
        return "-1"
