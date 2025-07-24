## Flashcards Study App
An interactive web-based flashcard tool that lets users create, manage,and
study decks of flashcards.


## Setup & Run Locally
**Clone the repo:**
git clone https://github.com/YOUR_USERNAME/flashcards-app.git
cd flashcards-app

**Set up virtual environment**
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

**Create DB**
sqlite3 database.db < schema.sql

**Run app**
python app.py
