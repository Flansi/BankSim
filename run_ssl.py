"""Startet die Flask-App mit SSL-Unterstützung."""

from app import app


if __name__ == "__main__":
    app.run(debug=True, port=443, ssl_context=("cert.pem", "key.pem"))
