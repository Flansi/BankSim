import random
from datetime import date, timedelta
from getpass import getpass
from werkzeug.security import generate_password_hash

from app import db, User, Transaction, app

INCOME_DESCRIPTIONS = [
    "Gehalt Muster AG",
    "Bonuszahlung",
    "Dividende BlueChip AG",
    "Überweisung Max Mustermann",
    "Rückerstattung Versicherung",
    "Ebay Verkauf",
    "Kreditrückzahlung",
    "Barzahlung",
]

EXPENSE_DESCRIPTIONS = [
    "Miete Wohnung",
    "Handyrechnung",
    "Strom Stadtwerke",
    "Fitnessstudio",
    "Versicherung",
    "Tankstelle",
    "Apotheke",
    "Online Shop",
    "Restaurant",
    "Streamingdienst",
]


def generate_transactions(user_id, num=30):
    transactions = []
    today = date.today()
    for _ in range(num):
        if random.random() < 0.4:  # income
            desc = random.choice(INCOME_DESCRIPTIONS)
            amount = round(random.uniform(100, 3000), 2)
        else:
            desc = random.choice(EXPENSE_DESCRIPTIONS)
            amount = -round(random.uniform(10, 1000), 2)
        days_ago = random.randint(0, 60)
        txn_date = today - timedelta(days=days_ago)
        transactions.append(Transaction(user_id=user_id, date=txn_date, description=desc, amount=amount))
    return transactions


def main():
    username = input("Benutzername: ")
    password = getpass("Passwort: ")
    with app.app_context():
        if User.query.filter_by(username=username).first():
            print("Benutzer existiert bereits")
            return
        user = User(username=username, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        txns = generate_transactions(user.id, random.randint(20, 50))
        db.session.add_all(txns)
        db.session.commit()
        print(f"Benutzer '{username}' mit {len(txns)} Transaktionen angelegt.")


if __name__ == "__main__":
    main()
