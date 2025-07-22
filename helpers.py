from functools import wraps
from flask import session, redirect # type: ignore

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwags):
        if not session.get("user_id"):
            return redirect("/login")
        return f(*args, **kwags)
    return decorated_function