"""
INTENTIONALLY VULNERABLE API for CI/CD security pipeline demo.
The pipeline (Semgrep + Gitleaks + Trivy + ZAP) should fail on this file.

Do NOT deploy this.
"""

from flask import Flask, request, jsonify
import sqlite3
import hashlib
import os

app = Flask(__name__)

# VULN: hardcoded secret (Gitleaks + Semgrep will flag)
API_KEY = "DEMO_FAKE_KEY_FOR_CI_LAB"
DB_PASSWORD = "supersecretpassword123"

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
    # VULN: MD5 is weak (Semgrep: insecure-hash-algorithm-md5)
    return hashlib.md5(pw.encode()).hexdigest()


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
    # VULN: SQL injection via string formatting (Semgrep: sqlalchemy-execute-raw-query)
    query = f"SELECT * FROM users WHERE username='{username}' AND password_hash='{hash_pw(password)}'"
    row = conn.execute(query).fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "invalid"}), 401
    return jsonify({"username": row["username"], "email": row["email"]})


@app.route("/calc", methods=["GET"])
def calc():
    expr = request.args.get("expr", "1+1")
    # VULN: eval on user input (Semgrep: eval-usage)
    try:
        result = eval(expr)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/debug", methods=["GET"])
def debug_info():
    # VULN: exposes environment variables
    return jsonify({"env": dict(os.environ)})


if __name__ == "__main__":
    init_db()
    seed()
    # VULN: debug=True in production
    app.run(host="0.0.0.0", port=5001, debug=True)