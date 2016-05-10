from flask import Flask

from gosocialserver import config

app = Flask(__name__)
app.debug = True
app.secret_key = config.SECRET_KEY


def run():
    global app
    app.run("0.0.0.0", 5000)
