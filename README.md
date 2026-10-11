# CI/CD API Security Pipeline

[![API Security Pipeline](https://github.com/Neeraja-12/cicd-api-security/actions/workflows/security.yml/badge.svg)](https://github.com/Neeraja-12/cicd-api-security/actions/workflows/security.yml)

Shift-left security lab: a Flask API with a GitHub Actions pipeline that
runs four security scanners on every push and pull request.

## Scanners integrated

| Tool | Type | What it catches |
|---|---|---|
| Semgrep | SAST | Insecure code patterns (SQL injection, eval, weak hash, hardcoded secrets) |
| Gitleaks | Secret scan | Committed API keys, tokens, passwords |
| Trivy | SCA + IaC | Vulnerable dependencies, misconfigured Dockerfiles |
| OWASP ZAP | DAST | Runtime issues against the running API (headers, XSS, misconfig) |

## How it works

    Push / PR
        |
        v
    .github/workflows/security.yml
        |
        +--> Semgrep  -> SARIF -> GitHub Security tab
        +--> Gitleaks -> fails if secrets found
        +--> Trivy    -> fails on CRITICAL/HIGH
        +--> ZAP      -> fails on runtime issues
        |
        v
    Build fails on high-severity findings

## Branch model

- `main`   -> intentionally vulnerable API. The pipeline FAILS. This proves the scanners work.
- `secure` -> fixed API. The pipeline PASSES.

## How to run locally

    # Build and run the API
    cd api
    pip install -r requirements.txt
    python app.py

    # Run Semgrep locally
    pip install semgrep
    semgrep --config .semgrep.yml --config p/python --error

## Findings

See [FINDINGS.md](FINDINGS.md) for the list of vulnerabilities detected on
`main` and their fixes on `secure`.

## Warning
The `main` branch is intentionally vulnerable. Do not deploy it.