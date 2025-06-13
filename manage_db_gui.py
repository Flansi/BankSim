import tkinter as tk
from tkinter import simpledialog, messagebox
from app import app, db, User, Transaction
from werkzeug.security import generate_password_hash
from datetime import date


def refresh_users(listbox):
    listbox.delete(0, tk.END)
    with app.app_context():
        users = User.query.order_by(User.id).all()
        for u in users:
            listbox.insert(tk.END, f"{u.id}: {u.username}")


def add_user(listbox):
    username = simpledialog.askstring("Benutzer", "Neuen Benutzernamen eingeben:")
    if not username:
        return
    password = simpledialog.askstring("Passwort", "Passwort eingeben:", show='*')
    if not password:
        return
    with app.app_context():
        if User.query.filter_by(username=username).first():
            messagebox.showerror("Fehler", "Benutzer existiert bereits")
            return
        user = User(username=username, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
    refresh_users(listbox)


def delete_user(listbox):
    selection = listbox.curselection()
    if not selection:
        return
    item = listbox.get(selection[0])
    user_id = int(item.split(":", 1)[0])
    with app.app_context():
        user = User.query.get(user_id)
        if user:
            if messagebox.askyesno("Löschen", f"Benutzer {user.username} löschen?"):
                Transaction.query.filter_by(user_id=user.id).delete()
                db.session.delete(user)
                db.session.commit()
                refresh_users(listbox)


def change_password(listbox):
    selection = listbox.curselection()
    if not selection:
        return
    item = listbox.get(selection[0])
    user_id = int(item.split(":", 1)[0])
    new_pw = simpledialog.askstring("Passwort ändern", "Neues Passwort eingeben:", show='*')
    if not new_pw:
        return
    with app.app_context():
        user = User.query.get(user_id)
        if user:
            user.password = generate_password_hash(new_pw)
            db.session.commit()
            messagebox.showinfo("Erfolg", f"Passwort für {user.username} aktualisiert")


def show_transactions(user_id):
    txn_win = tk.Toplevel()
    txn_win.title("Transaktionen")
    listbox = tk.Listbox(txn_win, width=50)
    listbox.pack(fill=tk.BOTH, expand=True)

    def refresh_tx():
        listbox.delete(0, tk.END)
        with app.app_context():
            txns = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date).all()
            for t in txns:
                listbox.insert(tk.END, f"{t.id}: {t.date} {t.description} {t.amount}")

    def add_tx():
        desc = simpledialog.askstring("Beschreibung", "Beschreibung der Transaktion:")
        if desc is None:
            return
        amount_str = simpledialog.askstring("Betrag", "Betrag eingeben:")
        if amount_str is None:
            return
        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Fehler", "Ungültiger Betrag")
            return
        with app.app_context():
            txn = Transaction(user_id=user_id, date=date.today(), description=desc, amount=amount)
            db.session.add(txn)
            db.session.commit()
        refresh_tx()

    def delete_tx():
        sel = listbox.curselection()
        if not sel:
            return
        item = listbox.get(sel[0])
        txn_id = int(item.split(":", 1)[0])
        with app.app_context():
            txn = Transaction.query.get(txn_id)
            if txn and messagebox.askyesno("Löschen", f"Transaktion {txn.description} löschen?"):
                db.session.delete(txn)
                db.session.commit()
                refresh_tx()

    btn_frame = tk.Frame(txn_win)
    btn_frame.pack(fill=tk.X)
    tk.Button(btn_frame, text="Neu", command=add_tx).pack(side=tk.LEFT)
    tk.Button(btn_frame, text="Löschen", command=delete_tx).pack(side=tk.LEFT)

    refresh_tx()
    txn_win.mainloop()


def view_transactions(listbox):
    selection = listbox.curselection()
    if not selection:
        return
    item = listbox.get(selection[0])
    user_id = int(item.split(":", 1)[0])
    show_transactions(user_id)


def main():
    root = tk.Tk()
    root.title("DB Verwaltung")
    user_list = tk.Listbox(root, width=40)
    user_list.pack(fill=tk.BOTH, expand=True)

    btn_frame = tk.Frame(root)
    btn_frame.pack(fill=tk.X)
    tk.Button(btn_frame, text="Aktualisieren", command=lambda: refresh_users(user_list)).pack(side=tk.LEFT)
    tk.Button(btn_frame, text="Neu", command=lambda: add_user(user_list)).pack(side=tk.LEFT)
    tk.Button(btn_frame, text="Löschen", command=lambda: delete_user(user_list)).pack(side=tk.LEFT)
    tk.Button(btn_frame, text="Transaktionen", command=lambda: view_transactions(user_list)).pack(side=tk.LEFT)
    tk.Button(btn_frame, text="Passwort ändern", command=lambda: change_password(user_list)).pack(side=tk.LEFT)

    refresh_users(user_list)
    root.mainloop()


if __name__ == "__main__":
    main()
