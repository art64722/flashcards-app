from functools import wraps
from flask import session, redirect, render_template # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
from zxcvbn import zxcvbn # type: ignore
import sqlite3

DATABASE = "database.db"

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

    
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # Now access to columns by name
    return conn


def register_user(username, password):
    """
    Tries to insert new user. Returns True, None if successful; else False, error.
    """
    # Hash the password
    hash = generate_password_hash(password)

    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash))

        db.commit()
        db.close()
        return True, None
    except sqlite3.IntegrityError:
        return False, "Username already exists"
    except Exception:
        return False, "Can't add user"


def authenticate_user(username, password):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    db.close()

    if user and check_password_hash(user["hash"], password):
        return user["id"]
    return None


def get_user_by_id(user_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    db.close()
    return user


def create_deck(user_id, name):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("INSERT INTO decks (user_id, name) VALUES (?, ?)", (user_id, name))
    db.commit()
    db.close()


def get_decks_by_user(user_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM decks WHERE user_id = ?", (user_id,))
    decks = cursor.fetchall()

    db.close()
    return decks


def get_deck(deck_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM decks WHERE id = ?", (deck_id,))
    deck = cursor.fetchone()

    db.close()
    return deck


def add_card(deck_id, question, answer):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO cards (deck_id, question, answer) VALUES (?, ?, ?)",
        (deck_id, question, answer)
    )

    db.commit()
    db.close()


def get_cards_by_deck(deck_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM cards WHERE deck_id = ?", (deck_id,))
    cards = cursor.fetchall()

    db.close()
    return cards


def delete_deck(deck_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("DELETE FROM decks WHERE id = ?", (deck_id,))
    db.commit()
    db.close()


def user_owns_deck(user_id, deck_id):
    """
    Returns True if the deck with given deck_id belongs to user_id, else False.
    """
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id FROM decks WHERE id = ? AND user_id = ?", (deck_id, user_id))
    result = cursor.fetchone()

    db.close()

    return result is not None