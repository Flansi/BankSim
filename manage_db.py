import argparse
from getpass import getpass
from datetime import date

from werkzeug.security import generate_password_hash

from app import app, db, User, Transaction


def list_users():
    with app.app_context():
        users = User.query.order_by(User.id).all()
        for u in users:
            print(f"{u.id}: {u.username}")


def add_user(username):
    password = getpass("Passwort: ")
    with app.app_context():
        if User.query.filter_by(username=username).first():
            print("Benutzer existiert bereits")
            return
        user = User(username=username, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        print(f"Benutzer angelegt mit ID {user.id}")


def delete_user(username):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print("Benutzer nicht gefunden")
            return
        Transaction.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        print("Benutzer gelöscht")


def list_transactions(username):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print("Benutzer nicht gefunden")
            return
        txns = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.date).all()
        for t in txns:
            print(f"{t.id}: {t.date} {t.description} {t.amount}")


def add_transaction(username, amount, description, txn_date=None):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print("Benutzer nicht gefunden")
            return
        if txn_date:
            txn_date = date.fromisoformat(txn_date)
        else:
            txn_date = date.today()
        txn = Transaction(user_id=user.id, date=txn_date, description=description, amount=amount)
        db.session.add(txn)
        db.session.commit()
        print(f"Transaktion angelegt mit ID {txn.id}")


def delete_transaction(txn_id):
    with app.app_context():
        txn = Transaction.query.get(txn_id)
        if not txn:
            print("Transaktion nicht gefunden")
            return
        db.session.delete(txn)
        db.session.commit()
        print("Transaktion gelöscht")


def main():
    parser = argparse.ArgumentParser(description="Datenbank verwalten")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("list-users")

    p_add_user = sub.add_parser("add-user")
    p_add_user.add_argument("username")

    p_del_user = sub.add_parser("delete-user")
    p_del_user.add_argument("username")

    p_list_tx = sub.add_parser("list-tx")
    p_list_tx.add_argument("username")

    p_add_tx = sub.add_parser("add-tx")
    p_add_tx.add_argument("username")
    p_add_tx.add_argument("amount", type=float)
    p_add_tx.add_argument("description")
    p_add_tx.add_argument("--date")

    p_del_tx = sub.add_parser("delete-tx")
    p_del_tx.add_argument("id", type=int)

    args = parser.parse_args()

    if args.cmd == "list-users":
        list_users()
    elif args.cmd == "add-user":
        add_user(args.username)
    elif args.cmd == "delete-user":
        delete_user(args.username)
    elif args.cmd == "list-tx":
        list_transactions(args.username)
    elif args.cmd == "add-tx":
        add_transaction(args.username, args.amount, args.description, args.date)
    elif args.cmd == "delete-tx":
        delete_transaction(args.id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
