# SSN Holiday UI (demo)

This is a small demo Flask app added to the repository to provide a simple login -> dashboard -> group -> Christmas homepage flow.

How to run (PowerShell):

1. Create a virtual environment and activate it (recommended):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Install requirements:

```powershell
pip install -r requirements.txt
```

3. Run the app:

```powershell
python webapp.py
```

4. Open http://127.0.0.1:5000 in your browser. Use one of the usernames defined in `users.py` (e.g., `josh`, `jen`, `brian`).

Notes and next steps:
- This demo uses in-memory data and a simple session secret; it's not production-ready.
- To make it persistent, wire a DB, add password auth, and host properly behind a WSGI server.
