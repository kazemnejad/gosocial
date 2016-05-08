from flask import Flask

from gosocialserver import config

app = Flask(__name__)
app.debug = True
app.secret_key = config.SECRET_KEY

import gosocialserver.userviews
import gosocialserver.postviews


def run():
    global app
    app.run()
