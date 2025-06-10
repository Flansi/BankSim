# BankSim

BankSim is a small demo of a banking website built with [Flask](https://flask.palletsprojects.com/). It features a basic login and registration system and several HTML pages in German for various banking services.

## Setup

1. **Clone the repository** (if you haven't already) and change into the project directory.
2. **Create a virtual environment** (recommended) and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application**:
   ```bash
   python app.py
   ```
   This starts a development server on `http://127.0.0.1:5000/`.

On first run, a SQLite database (`database.db`) will be created automatically. You can then register a user and log in to access the demo pages.
