from flask import Flask, render_template, request, redirect, url_for, session
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, date
import random
import os

app = Flask(__name__, template_folder='.')
app.config['SECRET_KEY'] = 'change_this_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

db = SQLAlchemy(app)


def random_account_number():
    """Return a random 10-digit account number."""
    return "".join(str(random.randint(0, 9)) for _ in range(10))


def random_iban():
    """Return a random Austrian IBAN starting with AT."""
    return "AT" + "".join(str(random.randint(0, 9)) for _ in range(18))


def load_config():
    """Load configuration from config.json if it exists."""
    path = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return {"pwmod": 0, "humancheck": 0}

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    account_number = db.Column(db.String(20))
    account_iban = db.Column(db.String(34))


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    iban = db.Column(db.String(34))
    bic = db.Column(db.String(11))
    purpose = db.Column(db.String(200))
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))

with app.app_context():
    db.create_all()
    inspector = db.inspect(db.engine)
    cols = {c["name"] for c in inspector.get_columns("user")}
    added = False
    if "account_number" not in cols:
        db.session.execute(
            text("ALTER TABLE user ADD COLUMN account_number VARCHAR(20)")
        )
        added = True
    if "account_iban" not in cols:
        db.session.execute(
            text("ALTER TABLE user ADD COLUMN account_iban VARCHAR(34)")
        )
        added = True
    if added:
        db.session.commit()

@app.route('/')
def dashboard():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if not user:
            session.pop('user_id', None)
            return redirect(url_for('login'))
        transactions = (
            Transaction.query.filter_by(user_id=user.id)
            .order_by(Transaction.date.desc(), Transaction.id.desc())
            .all()
        )
        balance = sum(t.amount for t in transactions)
        recent_transactions = transactions[:5]
        account_number = user.account_number or random_account_number()
        account_iban = user.account_iban or random_iban()
        return render_template(
            'index.html',
            transactions=transactions,
            recent_transactions=recent_transactions,
            balance=balance,
            username=user.username,
            account_number=account_number,
            account_iban=account_iban,
        )
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session.permanent = True
            cfg = load_config()
            if cfg.get('humancheck') == 1:
                session['pending_user_id'] = user.id
                return redirect(url_for('humancheck'))
            session['user_id'] = user.id
            if cfg.get('pwmod') in (1, 2, 3):
                return redirect(url_for('change_password'))
            return redirect(url_for('dashboard'))
        error = "Ungültige Anmeldedaten"
        return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Benutzer existiert bereits')
        hashed = generate_password_hash(password)
        user = User(username=username, password=hashed)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/humancheck')
def humancheck():
    if 'pending_user_id' not in session:
        return redirect(url_for('login'))
    return render_template('humancheck.html')


@app.route('/humancheck-complete')
def humancheck_complete():
    uid = session.pop('pending_user_id', None)
    if not uid:
        return redirect(url_for('login'))
    session['user_id'] = uid
    cfg = load_config()
    if cfg.get('pwmod') in (1, 2, 3):
        return redirect(url_for('change_password'))
    return redirect(url_for('dashboard'))


@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    cfg = load_config()
    pwmod = cfg.get('pwmod', 0)
    if pwmod == 0:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        new_pw = request.form['new_password']
        user = User.query.get(session['user_id'])
        user.password = generate_password_hash(new_pw)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('login.html', show_pw_change=True, pwmod=pwmod)


@app.route('/transfer', methods=['POST'])
def transfer():
    """Create a new outgoing transaction for the logged in user."""
    if 'user_id' not in session:
        return '', 401

    recipient = request.form['recipient']
    iban = request.form['iban']
    bic = request.form['bic']
    amount_raw = request.form['amount']
    purpose = request.form.get('purpose', '')

    try:
        amount = float(amount_raw)
    except ValueError:
        return 'Invalid amount', 400

    description = f"\u00dcberweisung an {recipient}"  # "Überweisung an" with Umlaut
    if purpose:
        description += f": {purpose}"

    txn = Transaction(
        user_id=session['user_id'],
        date=date.today(),
        description=description,
        amount=-abs(amount),
        iban=iban,
        bic=bic,
        purpose=purpose,
    )
    db.session.add(txn)
    db.session.commit()
    return '', 204

@app.route('/sepa-transfer', methods=['POST'])
def sepa_transfer():
    """Create a new domestic SEPA transaction for the logged in user."""
    if 'user_id' not in session:
        return '', 401

    recipient = request.form['recipient']
    iban = request.form['iban']
    amount_raw = request.form['amount']
    purpose = request.form.get('purpose', '')

    try:
        amount = float(amount_raw)
    except ValueError:
        return 'Invalid amount', 400

    description = f"\u00dcberweisung an {recipient}"
    if purpose:
        description += f": {purpose}"

    txn = Transaction(
        user_id=session['user_id'],
        date=date.today(),
        description=description,
        amount=-abs(amount),
        iban=iban,
        purpose=purpose,
    )
    db.session.add(txn)
    db.session.commit()
    return '', 204

# Routen für statische Informationsseiten
@app.route('/karriere.html')
def karriere_page():
    """Zeigt die Karriereseite an."""
    return render_template('karriere.html')


@app.route('/rechner.html')
def rechner_page():
    """Zeigt die Rechnerseite an."""
    return render_template('rechner.html')


@app.route('/filialen.html')
def filialen_page():
    """Zeigt die Filialenseite an."""
    return render_template('filialen.html')


# Neue Routen für zusätzliche statische Seiten
@app.route('/sperrhotline.html')
def sperrhotline_page():
    """Zeigt die Sperrhotline an."""
    return render_template('sperrhotline.html')


@app.route('/kundenservice.html')
def kundenservice_page():
    """Zeigt den Kundenservice an."""
    return render_template('kundenservice.html')


@app.route('/mitarbeiter.html')
def mitarbeiter_page():
    """Zeigt die Mitarbeiterseite an."""
    return render_template('mitarbeiter.html')


@app.route('/index.html')
def index_page():
    """Leitet zur Startseite weiter."""
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=80)
