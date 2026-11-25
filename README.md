# Cadence — chinni-app

A study rhythm and score tracker for **JEE** and **CBSE** students (including **JEE Main 2026**, **CBSE 8th Grade**, **CBSE 12th Board**, and custom tracks). Built with Python, FastAPI, CustomTkinter, and MySQL (with automatic local SQLite fallback).

Log mock tests and unit tests by ticking the exact **syllabus chapters** included in each exam, track your scores across flexible exam patterns, get a schedule-friendly **Suggested Study Mix** linked directly to an interactive **Focus Timer**, and manage accounts and tracks from **Settings**.

---

## What you need before you start

| Requirement | Minimum version | Required? | Download link |
|---|---|---|---|
| Python | 3.10 | Yes | https://www.python.org/downloads/ |
| Git | any | Yes | https://git-scm.com/downloads |
| MySQL Server | 8.0 | Optional | https://dev.mysql.com/downloads/mysql/ |

> **During Python install on Windows:** tick **"Add Python to PATH"** before clicking Install Now.
>
> **No MySQL installed?** That is completely fine — if the app cannot reach MySQL, it automatically uses a local SQLite file (`chinni_offline.db`), so you can run everything out of the box on a fresh laptop without installing MySQL.

---

## 1 — Clone the repository

Open a terminal (**PowerShell** on Windows, **Terminal** on Mac/Linux) and run:

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

Wait for packages to finish downloading and installing before moving on.

> **If you see `Activate.ps1 cannot be loaded` on Windows**, run this once first, then retry:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

---

## 3 — Configure the database (Optional if using offline mode)

- **If you are testing quickly without MySQL:** you can skip straight to **Step 4** — the app creates and uses `chinni_offline.db` automatically.
- **If you want to use MySQL Server:** copy `.env.example` to `.env` and set `DB_PASSWORD` to your MySQL root password:

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

```ini
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=chinni_db
```

---

## 4 — Load the demo accounts & syllabus data

This creates all database tables, sets up the **Admin** account, and seeds 3 demo student accounts with JEE Main 2026 & CBSE 12th Board tracks, chapter-wise syllabi, sample tests (`T1`–`T3`), study plans, and focus sessions:

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\python.exe -m backend.seed.seed_data
```

**Mac / Linux:**
```bash
.venv/bin/python -m backend.seed.seed_data
```

### Seeded Accounts

| Role | Username | Password |
|---|---|---|
| Admin (sees all students) | `admin` | `admin123` |
| Student | `Mukund Prasanna` | `1studyproject` |
| Student | `Sarvesh Umesh Kulkarni` | `2studyproject` |
| Student | `Arya Nandan Srinivas` | `3studyproject` |

*(You can also skip seeding or create brand-new accounts anytime via **Sign Up** in the app — e.g. selecting **CBSE 8th Grade**, **JEE Main 2026**, or **CBSE 12th Board**.)*

---

## 5 — Run the backend server

The backend must be running before you open the UI. Keep this terminal open.

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\python.exe run_backend.py
```

**Mac / Linux:**
```bash
.venv/bin/python run_backend.py
```

You will see:

```text
Starting Cadence API Server (chinni-app)
[Server] Listening at http://127.0.0.1:8000
[Docs] Swagger UI available at http://127.0.0.1:8000/docs
```

---

## 6 — Launch the desktop UI

Open a **second** terminal in the `chinni-app` folder and run:

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\python.exe run_app.py
```

**Mac / Linux:**
```bash
.venv/bin/python run_app.py
```

1. **Log In or Sign Up** on the Cadence login screen (`admin / admin123`, one of the 3 seeded accounts, or **Sign Up** to create a new account and pick a starting track such as **CBSE 8th Grade**).
2. The bottom-left corner shows a green **`● API Connected (8000)`** badge when connected to the backend.
3. Explore the 5 screens in the sidebar:
   - **Dashboard**: Scorecard, target deficit, momentum, and subject averages.
   - **Log a Test**: Multi-subject mode (e.g. JEE Main) or Single-Subject flexible-marks mode (e.g. CBSE 8th Grade) with chapter checkboxes.
   - **Trends & Ranking**: Score progression and a flexible **Suggested Study Mix** with one-click **`▶ Start Sprint`** buttons.
   - **Focus Timer**: Pomodoro sprints with **`✨ Suggested Next Up`** that dynamically rebalance future suggestions as you log sessions.
   - **Settings**: Change username/password (requires current password), add new tracks, edit target scores, or delete tracks with confirmation.

---

## 7 — Run the tests

With the backend stopped (or running), run the full test suite from the project folder:

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
```

**Mac / Linux:**
```bash
.venv/bin/python -m pytest tests -v
```

Expected output: `21 passed`.

> **Note:** Running `pytest` writes sample test records into the active database (`chinni_offline.db` or MySQL). If you run tests and want a clean demo database afterward, delete `chinni_offline.db` and re-run Step 4 (`seed_data`).

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `python` not found | Use `python3` (Mac/Linux) or `py` (Windows), or reinstall Python and tick **"Add to PATH"** |
| `pip install` fails with no network | Make sure you are connected to the internet during install |
| `Activate.ps1` blocked on Windows | Run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` once |
| `No module named tkinter` (Linux) | Install Tk support: `sudo apt install python3-tk` |
| MySQL connection refused | Ignore if testing locally — Cadence automatically falls back to `chinni_offline.db` |
| `ModuleNotFoundError` | Make sure you are inside the `chinni-app` folder and using `.venv` |
| Login shows "Cannot reach backend" | Make sure `run_backend.py` is running in a separate terminal first |

---

## Project structure

```text
chinni-app/
├── run_backend.py          ← start the FastAPI server
├── run_app.py              ← start the CustomTkinter desktop UI
├── login_page.py           ← Login / Sign Up gate with starting track picker
├── requirements.txt        ← all Python packages
├── .env.example            ← optional MySQL config template
│
├── backend/
│   ├── api/                ← HTTP routes (FastAPI: auth, students, tracks, tests, plans, analytics)
│   ├── schemas/            ← request & response shapes (Pydantic)
│   ├── services/           ← scoring maths, flexible study mix, adherence
│   ├── repositories/       ← SQL queries & SQLite fallback
│   └── seed/               ← demo accounts & JEE / CBSE 8th / CBSE 12th syllabi
│
├── ui/
│   ├── api_client.py       ← only file that makes HTTP calls
│   ├── home_screen.py      ← dashboard with student & track selector
│   ├── tests_screen.py     ← log tests with syllabus chapter checkboxes & flexible marks
│   ├── trends_screen.py    ← score progression & flexible study mix -> timer launch
│   ├── focus_timer.py      ← Pomodoro timer linked with Suggested Next Up
│   └── settings_screen.py  ← account security, track CRUD, target score editing
│
└── tests/
    ├── test_api.py
    ├── test_scoring.py
    ├── test_planning.py
    └── test_repositories.py
```

---

## Architecture in one sentence per layer

```text
UI (CustomTkinter)  →  API Client (HTTP only)  →  FastAPI Routes  →  Service Logic  →  Repository SQL  →  MySQL / SQLite
```

Each layer has one job and calls only the layer directly beneath it. The UI never writes SQL. The routes never do maths. The services never know about HTTP.
