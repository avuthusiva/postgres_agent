# PostgreSQL Agent

A starter app for asking questions in plain English, generating PostgreSQL `SELECT` queries, and displaying the SQL and results.

## Stack

- Frontend: React, TypeScript, Vite
- API: FastAPI
- Database: PostgreSQL via SQLAlchemy and psycopg
- SQL generation: OpenAI API

## Prerequisites

- Python 3.10+
- Node.js 20+
- A local PostgreSQL database
- An OpenAI API key

## Configure the backend

In PowerShell, from the project root:

```powershell
Copy-Item backend\.env.example backend\.env
```

Edit `backend\.env` and set `DATABASE_URL`, `OPENAI_API_KEY`, and `ALLOWED_SCHEMAS`. Use a PostgreSQL role with read-only `SELECT` access only to the tables this agent should use. Do not put database credentials or API keys in frontend files.

Create and start the API:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`; interactive API documentation is at `http://localhost:8000/docs`.

## Start the frontend

In a second PowerShell window, from the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal (normally `http://localhost:5173`).

## Safety notes

- The API accepts only one parsed `SELECT` statement and verifies table references against `ALLOWED_SCHEMAS`.
- Database execution uses a read-only transaction, a 5-second statement timeout, and returns at most 500 rows.
- These controls are defense in depth, not a substitute for a dedicated least-privilege database role. Do not use a PostgreSQL superuser.
- Generated SQL may be incorrect. Review it before relying on results.
- Keep `.env` files private and out of source control.

## Run backend tests

From `backend` with its virtual environment activated:

```powershell
python -m pytest
```
