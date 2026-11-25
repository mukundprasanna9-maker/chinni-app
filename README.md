# Cadence — chinni-app

A study rhythm and score tracker for JEE / CBSE students. Built with Python, FastAPI, CustomTkinter, and MySQL.

Track your Maths, Physics, and Chemistry mock test scores across G1/G2/G3 topic groups, see where you are losing marks, and allocate study hours using a data-driven spend-ranking algorithm.

---

## What you need before you start

| Requirement | Minimum version | Download link |
|---|---|---|
| Python | 3.10 | https://www.python.org/downloads/ |
| MySQL Server | 8.0 | https://dev.mysql.com/downloads/mysql/ |
| Git | any | https://git-scm.com/downloads |

> **During Python install:** tick **"Add Python to PATH"** before clicking Install Now.
>
> **During MySQL install:** when asked to set a root password, write it down — you will need it in Step 3.

---

## 1 — Clone the repository

Open a terminal (PowerShell on Windows, Terminal on Mac/Linux) and run:

```bash
git clone https://github.com/mukundprasanna9-maker/chinni-app.git
cd chinni-app
```

---

## 2 — Create the virtual environment and install packages

Run these three commands one after another. Each one must finish before you run the next.

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Mac / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

You will see packages downloading and installing. Wait for the prompt to come back before moving on.

> **If you see `Activate.ps1 cannot be loaded` on Windows**, run this once first, then retry:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

---

## 3 — Configure the database

Copy the example config file and open it in Notepad (or any editor):

**Windows:**
```powershell
copy .env.example .env
notepad .env
```

**Mac / Linux:**
```bash
cp .env.example .env
nano .env
```

The file looks like this:

```
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=chinni_db
```

**Only change `DB_PASSWORD`** — replace the empty value with the MySQL root password you set during installation, then save and close.

Example if your password is `abc123`:
```
DB_PASSWORD=abc123
```

> **No MySQL installed?** That is fine. If the app cannot reach MySQL, it automatically falls back to a local file (`chinni_offline.db`) so you can still run and test everything. You can connect MySQL later and it will switch over automatically.

---

## 4 — Load the demo data

This creates all the database tables and loads sample student profiles, JEE and CBSE 12 tracks, and three mock test results (T1, T2, T3).

**Windows:**
```powershell
.\.venv\Scripts\python.exe -m backend.seed.seed_data Mukund
```

**Mac / Linux:**
```bash
.venv/bin/python -m backend.seed.seed_data Mukund
```

Replace `Mukund` with any name. You will see output like:

```
Initializing database schema...
[Database] MySQL not reachable — using offline storage for now.
Created student 'Mukund' with ID 1
Created track 'JEE Main 2026' (ID: 1)
Created track 'CBSE 12th Board' (ID: 2)
Created sample test runs T1, T2, T3 with subject and group scores.
Database seeding completed successfully!
```

---

## 5 — Run the backend server

The backend must be running before you open the UI. Keep this terminal open.

**Windows:**
```powershell
.\.venv\Scripts\python.exe run_backend.py
```

**Mac / Linux:**
```bash
.venv/bin/python run_backend.py
```

You will see:

```
Starting Cadence API Server (chinni-app)
[Server] Listening at http://127.0.0.1:8000
[Docs] Swagger UI available at http://127.0.0.1:8000/docs
```

You can visit `http://127.0.0.1:8000/docs` in your browser to explore all API endpoints interactively.

---

## 6 — Launch the UI

Open a **second** terminal in the same folder. Activate the virtual environment again, then run:

**Windows:**
```powershell
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe run_app.py
```

**Mac / Linux:**
```bash
source .venv/bin/activate
.venv/bin/python run_app.py
```

The desktop app will open. The bottom-left corner shows a green **● API Connected** badge when the backend is running correctly.

---

## 7 — Run the tests

With the virtual environment active, run the full test suite from the project folder:

**Windows:**
```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
```

**Mac / Linux:**
```bash
.venv/bin/python -m pytest tests -v
```

Expected output: `16 passed`.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `python` not found | Use `python3` instead, or reinstall Python and tick "Add to PATH" |
| `pip install` fails with no network | Make sure you are connected to the internet during install |
| `Activate.ps1` blocked on Windows | Run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` once |
| MySQL connection refused | Check that the MySQL service is running, or just ignore it — the app uses a local fallback |
| `Module not found` error | Make sure the virtual environment is activated (you should see `(.venv)` in your prompt) |
| UI opens but shows no data | Make sure the backend (`run_backend.py`) is running in a separate terminal first |

---

## Project structure

```
chinni-app/
├── run_backend.py          ← start the API server
├── run_app.py              ← start the desktop UI
├── requirements.txt        ← all Python packages
├── .env.example            ← copy this to .env and fill in your DB password
│
├── backend/
│   ├── api/                ← HTTP routes (FastAPI)
│   ├── schemas/            ← request & response shapes (Pydantic)
│   ├── services/           ← scoring maths & spend ranking
│   ├── repositories/       ← all SQL queries (mysql-connector-python)
│   └── seed/               ← demo data loader
│
├── ui/
│   ├── api_client.py       ← only file that makes HTTP calls
│   ├── home_screen.py      ← dashboard with student & track selector
│   ├── tests_screen.py     ← log a test (Maths/Physics/Chem + G1/G2/G3)
│   ├── trends_screen.py    ← score trends & study hour recommendations
│   └── focus_timer.py      ← Pomodoro timer & adherence tracker
│
└── tests/
    ├── test_api.py
    ├── test_scoring.py
    ├── test_planning.py
    └── test_repositories.py
```

---

## Architecture in one sentence per layer

```
UI (CustomTkinter)  →  API Client (HTTP only)  →  FastAPI Routes  →  Service Logic  →  Repository SQL  →  MySQL
```

Each layer has exactly one job and calls only the layer directly beneath it. The UI never writes SQL. The routes never do maths. The services never know about HTTP.
