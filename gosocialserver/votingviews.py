from gosocialserver.server import app
from gosocialserver.userviews import login_required


@app.route("/posts/<int:id>/like")
@login_required
def like_post(post_id):
    pass


@app.route("/posts/<int:id>/dislike")
@login_required
def dislike_post(post_id):
    pass
