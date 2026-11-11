# Flask Login Demo

A small Flask app demonstrating a login form and a session-protected dashboard.

## Setup (Windows PowerShell)

From the project directory:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:FLASK_SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
$env:SESSION_COOKIE_SECURE = "false"
python -m flask --app app run --debug
```

Open <http://127.0.0.1:5000/login> in your browser.
Set `SESSION_COOKIE_SECURE` to `"true"` when serving the app over HTTPS; leave it `"false"` for local HTTP development.

## Implemented

- GET and POST handling for `/login`, with email normalization and generic failure feedback.
- Accessible login fields with labels, autocomplete, and conditional autofocus.
- Redirect to `/dashboard` after successful login; the dashboard redirects unauthenticated visitors to `/login`.
- Flask session-based login state.
- `SameSite=Lax` session cookies and a one-hour permanent session lifetime.
- SQLite user-table creation and parameterized user lookup/creation helpers with Argon2 password hashing.

The credential check is a hardcoded placeholder: use `test@example.com` and `password` to log in. Replace it with a real password-hash check before using this app beyond local testing. The session secret is generated for the current PowerShell session above; set a stable, private `FLASK_SECRET_KEY` in your deployment environment.
