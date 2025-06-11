from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

app = Flask(__name__, template_folder='.')
app.config['SECRET_KEY'] = 'change_this_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))

with app.app_context():
    db.create_all()

@app.route('/')
def dashboard():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        transactions = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.date.desc()).all()
        balance = sum(t.amount for t in transactions)
        return render_template('index.html', transactions=transactions, balance=balance)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    from_index = request.args.get('from_index')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session.permanent = True
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        error = "Ungültige Anmeldedaten"
        if from_index:
            return render_template('index.html', error=error)
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
    """Zeigt die Startseite an."""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
