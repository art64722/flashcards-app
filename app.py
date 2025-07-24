from flask import Flask, render_template, redirect, request, session, flash # type: ignore
from flask_session import Session
import sqlite3

from helpers import *

app = Flask(__name__)

#Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.secret_key = "" # blank until production!

@app.route("/")
def index_route():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register_route():
    if request.method == "POST":
        # Validate username
        form_data = request.form
        required = ["username"]

        valid, error = validate_fields(form_data, required)
        if not valid:
            return apology(error)
        
        # Validate password and confirmation
        valid, error = validate_password(form_data)
        if not valid:
            return apology(error)
        
        # Add user
        success, message = register_user(form_data["username"], form_data["password"])
        if not success:
            return apology(message)
        
        # Log in user
        user_id = authenticate_user(form_data["username"], form_data["password"])
        if not user_id:
            return apology("Invalid username or password!")
        session["user_id"] = user_id

        return redirect("/")
    
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login_route():
    if request.method == "POST":
        # Validate input
        form_data = request.form
        required = ["username", "password"]

        valid, error = validate_fields(form_data, required)
        if not valid:
            return apology(error)
        
        # Log in user
        user_id = authenticate_user(form_data["username"], form_data["password"])
        if not user_id:
            return apology("Invalid username or password!")
        session["user_id"] = user_id

        return redirect("/")
    
    return render_template("login.html")


@app.route("/logout")
def logout_route():
    session.clear()
    return redirect("/")


@app.route("/decks")
@login_required
def decks_route():
    user_id = session["user_id"]
    # Get user's decks
    decks = get_decks_by_user(user_id)

    return render_template("decks.html", decks=decks)


@app.route("/decks/create", methods=["GET", "POST"])
@login_required
def create_deck_route():
    if request.method == "POST":
        user_id = session["user_id"]

        # Validate deck name
        form_data = request.form
        required = ["name"]

        valid, error = validate_fields(form_data, required)
        if not valid:
            return apology(error)
        
        # Create deck
        create_deck(user_id, form_data["name"])

        return redirect("/decks")

    return render_template("create_deck.html")


@app.route("/decks/<int:deck_id>")
@login_required
def view_deck_route(deck_id):
    user_id = session["user_id"]

    # Confirm deck belongs to user
    if not user_owns_deck(user_id, deck_id):
        return apology("Deck not found or not yours")
    
    # Get deck
    deck = get_deck(deck_id)

    # Get all cards in this deck
    cards = get_cards_by_deck(deck_id)

    return render_template("view_deck.html", deck=deck, cards=cards)


@app.route("/decks/<int:deck_id>/add", methods=["GET", "POST"])
@login_required
def add_card_route(deck_id):
    user_id = session["user_id"]

    # Confirm deck belongs to user
    if not user_owns_deck(user_id, deck_id):
        return apology("Deck not found or not yours")
    
    if request.method == "POST":
        # Validate input
        form_data = request.form
        required = ["question", "answer"]

        valid, error = validate_fields(form_data, required)
        if not valid:
            return apology(error)

        # Add card to deck
        add_card(deck_id, form_data["question"], form_data["answer"])

        return redirect(f"/decks/{deck_id}")
    
    # Get deck
    deck = get_deck(deck_id) 

    return render_template("add_card.html", deck=deck)


@app.route("/study/<int:deck_id>")
@login_required
def study_route(deck_id):
    user_id = session["user_id"]

    # Confirm deck belongs to user
    if not user_owns_deck(user_id, deck_id):
        return apology("Deck not found or not yours")
    
    # Get deck
    deck = get_deck(deck_id)
    
    # Get cards
    cards_rows = get_cards_by_deck(deck_id)

    # Convert rows to dicts
    cards = [dict(card) for card in cards_rows]

    return render_template("study.html", deck=deck, cards=cards)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
