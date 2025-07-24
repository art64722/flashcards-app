from functools import wraps
from flask import session, redirect, render_template # type: ignore
from zxcvbn import zxcvbn # type: ignore

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


def validate_password(form_data):
    password = form_data["password"]
    confirmation = form_data["confirmation"]

    if not password:
        return False, "Missing password"
    
    if not confirmation:
        return False, "Missing confirmation"
    
    result = zxcvbn(password)

    if result["score"] < 3:
        return False, f"Password too weak: {result['feedback']['warning'] or 'Try a longer or more complex password'}"
    
    if password != confirmation:
        return False, "Password must match confirmation"
    
    return True, None


def apology(message, code=400):
    return render_template("apology.html", message=message), code
