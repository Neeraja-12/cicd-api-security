# Security Findings

This document lists the vulnerabilities present in the `main` branch and
their fixes in the `secure` branch. Each was detected by at least one of
the four pipeline scanners.

## Finding 1 - Hardcoded API key
- **Detected by:** Gitleaks, Semgrep
- **File:** api/app.py
- **Line:** API_KEY = "sk_live_51H8x..."
- **Severity:** Critical
- **Fix:** Move to environment variable; add `.env` to `.gitignore`
- **OWASP:** A02:2021 Cryptographic Failures

## Finding 2 - Hardcoded DB password
- **Detected by:** Gitleaks
- **File:** api/app.py
- **Severity:** Critical
- **Fix:** Use env vars / secrets manager

## Finding 3 - MD5 password hashing
- **Detected by:** Semgrep (insecure-hash-algorithm-md5)
- **File:** api/app.py, hash_pw()
- **Severity:** High
- **Fix:** Use bcrypt or argon2

## Finding 4 - SQL injection via f-string
- **Detected by:** Semgrep (sqlalchemy-execute-raw-query)
- **File:** api/app.py, /login
- **Severity:** Critical
- **Fix:** Use parameterized query with `?` placeholders
- **OWASP API Top 10:** API8:2023 Security Misconfiguration

## Finding 5 - eval() on user input
- **Detected by:** Semgrep (eval-usage)
- **File:** api/app.py, /calc
- **Severity:** Critical
- **Fix:** Remove endpoint or use ast.literal_eval with allowlist

## Finding 6 - Debug mode enabled
- **Detected by:** Semgrep, manual review
- **File:** api/app.py, __main__
- **Severity:** High
- **Fix:** debug=False, loaded from env

## Finding 7 - Sensitive data exposure
- **Detected by:** Manual review / ZAP
- **File:** api/app.py, /debug
- **Severity:** High
- **Fix:** Remove endpoint

## Finding 8 - Missing security headers
- **Detected by:** OWASP ZAP baseline
- **Fix:** Add Flask-Talisman or configure headers

---

## Remediation Summary

All findings are fixed in the `secure` branch. The pipeline status badge
above reflects `main` (failing) and `secure` (passing).