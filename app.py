from flask import Flask, render_template, redirect, request, session, flash # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
from flask_session import Session
import sqlite3

from helpers import login_required, validate_fields, validate_password, apology

app = Flask(__name__)

#Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.secret_key = "" # blank until production!

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Validate input
        form_data = request.form
        required = ["username"]

        valid, error = validate_fields(form_data, required)
        if not valid:
            return apology(error)
        
        # Validate password and confirmation
        valid, error = validate_password(form_data)
        if not valid:
            return apology(error)
        
        # Hash the password
        hash = generate_password_hash(form_data["password"])

        # Insert into db
        try:
            with sqlite3.connect("database.db", timeout=5) as db:
                cursor = db.cursor()
                cursor.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (form_data["username"], hash))
        except sqlite3.IntegrityError:
            return apology("Username already exists")
        
        return redirect("/login")
    
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Validate input
        form_data = request.form
        required = ["username", "password"]

        valid, error = validate_fields(form_data, required)
        if not valid:
            return apology(error)
        
        # Fetch user from db
        with sqlite3.connect("database.db", timeout=5) as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (form_data["username"],))
            user = cursor.fetchone()

        # Cheack user and password
        if user and check_password_hash(user["hash"], form_data["password"]):
            session["user_id"] = user["id"]
            return redirect("/")
        else:
            return apology("Invalid username or password")
    
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/decks")
@login_required
def decks():
    user_id = session["user_id"]

    # Fetch all user's decks
    with sqlite3.connect("database.db", timeout=5) as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute("SELECT * FROM decks WHERE user_id = ?", (user_id,))
        decks = cursor.fetchall()

    return render_template("decks.html", decks=decks)


@app.route("/decks/create", methods=["GET", "POST"])
@login_required
def create_deck():
    if request.method == "POST":
        user_id = session["user_id"]

        # Validate input
        form_data = request.form
        required = ["name"]

        valid, error = validate_fields(form_data, required)
        if not valid:
            return apology(error)
        
        with sqlite3.connect("database.db", timeout=5) as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO decks (name, user_id) VALUES (?, ?)", (form_data["name"], user_id))
            db.commit()

        return redirect("/decks")

    return render_template("create_deck.html")


@app.route("/decks/<int:deck_id>")
@login_required
def view_deck(deck_id):
    user_id = session["user_id"]

    with sqlite3.connect("database.db") as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()

        # Make sure the deck belongs to the user
        cursor.execute("SELECT * FROM decks WHERE id = ? AND user_id = ?", (deck_id, user_id))
        deck = cursor.fetchone()
        if not deck:
            return apology("Deck not found or not yours")
        
        # Get all cards in this deck
        cursor.execute("SELECT * FROM cards WHERE deck_id = ?", (deck_id,))
        cards = cursor.fetchall()

    return render_template("view_deck.html", deck=deck, cards=cards)


@app.route("/decks/<int:deck_id>/add", methods=["GET", "POST"])
@login_required
def add_card(deck_id):
    user_id = session["user_id"]

    with sqlite3.connect("database.db") as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()

        # Confirm deck belongs to user
        cursor.execute("SELECT * FROM decks WHERE id = ? AND user_id = ?", (deck_id, user_id))
        deck = cursor.fetchall()
        if not deck:
            return apology("Deck not found or not yours")
        
        if request.method == "POST":
            # Validate input
            form_data = request.form
            required = ["question", "answer"]

            valid, error = validate_fields(form_data, required)
            if not valid:
                return apology(error)

            # Inset card into DB
            cursor.execute(
                "INSERT INTO cards (question, answer, deck_id) VALUES (?, ?, ?)",
                (form_data["question"], form_data["answer"], deck_id)
            )
            db.commit()

            return redirect(f"/decks/{deck_id}")
    
    return render_template("add_card.html", deck=deck)


@app.route("/study/<int:deck_id>")
@login_required
def study(deck_id):
    user_id = session["user_id"]

    # Make sure the deck belongs to user
    with sqlite3.connect("database.db") as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()

        cursor.execute("SELECT * FROM decks WHERE id = ? AND user_id = ?", (deck_id, user_id))
        deck = cursor.fetchone()
        if not deck:
            return apology("Deck not found or not yours")
        
        cursor.execute("SELECT * FROM cards WHERE deck_id = ?", (deck_id,))
        # Convert rows to dicts
        cards = [dict(card) for card in cursor.fetchall()]

    return render_template("study.html", deck=deck, cards=cards)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)