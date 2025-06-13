import random
from datetime import date, timedelta
from getpass import getpass
from werkzeug.security import generate_password_hash

from app import db, User, Transaction, app

# Length of an Austrian IBAN is 20 characters: 'AT' followed by 18 digits
def random_iban():
    return "AT" + "".join(str(random.randint(0, 9)) for _ in range(18))


PURPOSES = [
    "Miete Wohnung",
    "Lebensmitteleinkauf",
    "Stromrechnung",
    "Internetgebühr",
    "Handyrechnung",
    "Gehalt",
    "Bonus",
    "Steuererstattung",
    "Kreditrate",
    "Restaurantbesuch",
    "Online Einkauf",
    "Geschenk {name}",
    "Mitgliedsbeitrag",
    "Spende",
]

AUSTRIAN_FIRST_NAMES = [
    "Anna",
    "Johann",
    "Franz",
    "Katrin",
    "Lukas",
    "Maria",
    "Martin",
    "Julia",
    "Stefan",
    "Ingrid",
]

AUSTRIAN_LAST_NAMES = [
    "Gruber",
    "Huber",
    "Bauer",
    "M\u00fcller",
    "Fischer",
    "Hofer",
    "Wagner",
    "Berger",
    "Schmid",
    "Pichler",
]


def random_name():
    """Return a random Austrian style full name."""
    return f"{random.choice(AUSTRIAN_FIRST_NAMES)} {random.choice(AUSTRIAN_LAST_NAMES)}"


INCOME_DESCRIPTIONS = [
    "Gehalt Alpen AG",
    "Bonuszahlung",
    "Dividende BlueChip AG",
    "\u00dcberweisung {name}",
    "R\u00fcckerstattung Versicherung",
    "Ebay Verkauf",
    "Kreditr\u00fcckzahlung",
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
    "\u00dcberweisung an {name}",
]


def generate_transactions(user_id, num=30):
    transactions = []
    today = date.today()
    for _ in range(num):
        if random.random() < 0.4:  # income
            desc_template = random.choice(INCOME_DESCRIPTIONS)
            if "{name}" in desc_template:
                desc = desc_template.format(name=random_name())
            else:
                desc = desc_template
            amount = round(random.uniform(100, 3000), 2)
        else:
            desc_template = random.choice(EXPENSE_DESCRIPTIONS)
            if "{name}" in desc_template:
                desc = desc_template.format(name=random_name())
            else:
                desc = desc_template
            amount = -round(random.uniform(10, 1000), 2)
        days_ago = random.randint(0, 60)
        txn_date = today - timedelta(days=days_ago)

        purpose_template = random.choice(PURPOSES)
        if "{name}" in purpose_template:
            purpose = purpose_template.format(name=random_name())
        else:
            purpose = purpose_template

        transactions.append(
            Transaction(
                user_id=user_id,
                date=txn_date,
                description=desc,
                amount=amount,
                iban=random_iban(),
                bic="n.A",
                purpose=purpose,
            )
        )
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
