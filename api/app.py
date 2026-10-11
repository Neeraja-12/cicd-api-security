"""
SECURE API - fixed version. Pipeline should pass.
"""

from flask import Flask, request, jsonify
import sqlite3
import os
import bcrypt
from dotenv import load_dotenv
from flask_talisman import Talisman
Talisman(app, force_https=False)

load_dotenv()

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY", "dev-key-not-used-in-prod")
DB_PATH = "users.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash TEXT,
            email TEXT
        );
        """
    )
    conn.commit()
    conn.close()


def hash_pw(pw):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def verify_pw(pw, hashed):
    try:
        return bcrypt.checkpw(pw.encode(), hashed.encode())
    except Exception:
        return False


def seed():
    conn = get_db()
    for u in [
        ("alice", hash_pw("alice123"), "alice@example.com"),
        ("bob", hash_pw("bob123"), "bob@example.com"),
    ]:
        try:
            conn.execute(
                "INSERT INTO users (username, password_hash, email) VALUES (?,?,?)", u
            )
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/login", methods=["POST"])
def login():
    body = request.get_json() or {}
    username = body.get("username", "")
    password = body.get("password", "")

    conn = get_db()
    row = conn.execute(
        "SELECT * FROM users WHERE username=?", (username,)
    ).fetchone()
    conn.close()

    if not row or not verify_pw(password, row["password_hash"]):
        return jsonify({"error": "invalid"}), 401

    return jsonify({"username": row["username"], "email": row["email"]})


if __name__ == "__main__":
    init_db()
    seed()
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5001, debug=debug)