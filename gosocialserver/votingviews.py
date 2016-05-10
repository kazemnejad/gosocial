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
        like.delete()
    else:
        Like.new(post, g.user)

    dislike = Select().star().From(Dislike.table_name) \
        .filter(column("post_id").equal(post.id)) \
        .And() \
        .filter(column("user_id").equal(g.user.id)) \
        .to_query().with_model(Dislike) \
        .first()
    if dislike:
        dislike.delete()

    like_count = Like.get_count_for(post)
    dislike_count = Dislike.get_count_for(post)
    return str(like_count) + '|' + str(dislike_count)


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
        dislike.delete()
    else:
        Dislike.new(post, g.user)

    like = Select().star().From(Like.table_name) \
        .filter(column("post_id").equal(post.id)) \
        .And() \
        .filter(column("user_id").equal(g.user.id)) \
        .to_query().with_model(Like) \
        .first()
    if like:
        like.delete()

    like_count = Like.get_count_for(post)
    dislike_count = Dislike.get_count_for(post)
    return str(dislike_count) + '|' + str(like_count)
