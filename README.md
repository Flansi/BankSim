# BankSim

BankSim is a small banking website for **Wien ONline-Bank** built with [Flask](https://flask.palletsprojects.com/). It features a basic login and registration system and several HTML pages in German for various banking services.

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
   This starts a development server on `http://127.0.0.1:80/`.

On first run, a SQLite database (`database.db`) will be created automatically. You can then register a user and log in to access the pages.

## Windows Setup

If you are using Windows, open **Command Prompt** or **PowerShell** and run the following commands:

1. Create and activate a virtual environment:
   ```cmd
   py -3 -m venv venv
   venv\Scripts\activate
   ```
2. Install the dependencies:
   ```cmd
   pip install -r requirements.txt
   ```
3. Run the application:
   ```cmd
   python app.py
   ```
   The development server will be available at `http://127.0.0.1:80/`.

## Datenbank direkt bearbeiten

Mit dem Skript `manage_db.py` können Sie die SQLite-Datenbank ohne die Weboberfläche verwalten. Einige Beispiele:

```bash
# Benutzer auflisten
python manage_db.py list-users

# Neuen Benutzer anlegen
python manage_db.py add-user USERNAME

# Benutzer löschen
python manage_db.py delete-user USERNAME

# Transaktionen eines Benutzers anzeigen
python manage_db.py list-tx USERNAME

# Neue Transaktion hinzufügen
python manage_db.py add-tx USERNAME BETRAG "Beschreibung" --date 2023-12-31
```

So können Sie Daten verändern, ohne die eigentliche Bankseite zu starten.
