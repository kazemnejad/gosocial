from flask import Flask

from gosocialserver import config

app = Flask(__name__)
app.debug = True
app.secret_key = config.SECRET_KEY


@app.route('/')
def hello_world():
    return 'Hello World!'


def run():
    global app
    app.run()
