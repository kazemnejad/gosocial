import os
from functools import wraps

from PIL import Image
from flask import g, redirect, request, url_for, session, flash, render_template, escape, abort, current_app


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function
