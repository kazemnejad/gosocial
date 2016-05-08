from gosocialserver.server import app
from gosocialserver.userviews import login_required


@app.route("/posts/<int:id>/comments/add", methods=['GET'])
@login_required
def add_comment(post_id):
    pass
