from functools import wraps
from flask import session, redirect # type: ignore

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwags):
        if not session.get("user_id"):
            return redirect("/login")
        return f(*args, **kwags)
    return decorated_function


def validate_fields(data, required_fields):
    """
    Validate that all required fields exist and are not empty in the given dict.
    Returns (True, None) if all valid,
    or (False, 'Field name is missing') if something is wrong.
    """
    for field in required_fields:
        if not data.get(field):
            return False, f"Missing {field}"
    return True, None
