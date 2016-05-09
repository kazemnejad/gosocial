from flask import abort, g

from gosocialserver.models import Post, Like, Dislike
from gosocialserver.orm import Select, column
from gosocialserver.server import app
from gosocialserver.userviews import login_required


@app.route("/posts/<int:post_id>/like", methods=['GET'])
@login_required
def like_post(post_id):
    post = Post.get_by_id(post_id)
    if not post:
        abort(404)

    like = Select().star().From(Like.table_name) \
        .filter(column("post_id").equal(post.id)) \
        .And() \
        .filter(column("user_id").equal(g.user.id)) \
        .to_query().with_model(Like) \
        .first()

    if like:
        return "-1"

    dislike = Select().star().From(Dislike.table_name) \
        .filter(column("post_id").equal(post.id)) \
        .And() \
        .filter(column("user_id").equal(g.user.id)) \
        .to_query().with_model(Dislike) \
        .first()
    if dislike:
        return "-2"

    like = Like.new(post, g.user)
    if like:
        return str(Like.get_count_for(post))
    else:
        return "-3"


@app.route("/posts/<int:post_id>/dislike", methods=['GET'])
@login_required
def dislike_post(post_id):
    post = Post.get_by_id(post_id)
    if not post:
        abort(404)

    dislike = Select().star().From(Dislike.table_name) \
        .filter(column("post_id").equal(post.id)) \
        .And() \
        .filter(column("user_id").equal(g.user.id)) \
        .to_query().with_model(Dislike) \
        .first()
    if dislike:
        return "-1"

    like = Select().star().From(Like.table_name) \
        .filter(column("post_id").equal(post.id)) \
        .And() \
        .filter(column("user_id").equal(g.user.id)) \
        .to_query().with_model(Like) \
        .first()
    if like:
        return "-2"

    dislike = Dislike.new(post, g.user)
    if dislike:
        return str(Dislike.get_count_for(post))
    else:
        return "-3"
