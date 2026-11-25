# Cadence — chinni-app

A study rhythm and score tracker for **JEE** and **CBSE** students (including **JEE Main 2026**, **CBSE 8th Grade**, **CBSE 12th Board**, and custom tracks). Built with Python, FastAPI, CustomTkinter, and MySQL (with automatic local SQLite fallback).

Log mock tests and unit tests by ticking the exact **syllabus chapters** included in each exam, track your scores across flexible exam patterns, get a schedule-friendly **Suggested Study Mix** linked directly to an interactive **Focus Timer**, and manage accounts and tracks from **Settings**.

---

## What you need before you start

| Requirement | Version | Required? | Download link |
|---|---|---|---|
| Python | 3.10+ (any latest stable version works) | Yes | https://www.python.org/downloads/ |
| Git | Any recent version | Yes | https://git-scm.com/downloads |
| MySQL Server | 8.0+ | Optional | https://dev.mysql.com/downloads/mysql/ |

> **Important during Python install on Windows:**
> Tick **"Add python.exe to PATH"** on the very first installer screen before clicking **Install Now**.
>
> **No MySQL installed?** No problem — if Cadence cannot reach MySQL, it automatically creates and uses a local SQLite database (`chinni_offline.db`), so everything runs out of the box on a fresh laptop.

---

## 1 — Open a regular terminal and clone the repository

On Windows, open a **normal (non-Administrator) PowerShell** window (`Win + X` → **Terminal** or search **PowerShell** — **do not** choose *Run as Administrator*, which opens in `C:\Windows\System32` and blocks folder creation).

Clone into a dedicated folder under your user directory (this avoids both `System32` permission errors and OneDrive/Defender locks on `Desktop` or `Documents`):

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\Projects" | Out-Null
Set-Location "$env:USERPROFILE\Projects"
git clone https://github.com/mukundprasanna9-maker/chinni-app.git
Set-Location "$env:USERPROFILE\Projects\chinni-app"
```

**Mac / Linux (Terminal):**
```bash
mkdir -p ~/Projects && cd ~/Projects
git clone https://github.com/mukundprasanna9-maker/chinni-app.git
cd ~/Projects/chinni-app
```

---

## 2 — Create the virtual environment and install packages

First verify Python is installed on your machine (and make sure you are inside the `chinni-app` folder):

**Windows (PowerShell):**
```powershell
Set-Location "$env:USERPROFILE\Projects\chinni-app"
py --version
```
*(If `py` is not found, try `python --version`. Note: if `python` opens the Microsoft Store or prints "Python was not found", install the latest Python (3.10+) from https://www.python.org/downloads/ and tick **"Add python.exe to PATH"**.)*

Once `py --version` (or `python --version`) prints Python 3.10 or newer, create `.venv` and install packages:

```powershell
if (Get-Command py -ErrorAction SilentlyContinue) { py -m venv .venv } else { python -m venv .venv }
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Mac / Linux (Terminal):**
```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

Wait until all packages finish installing before continuing.

> **If `python` is not recognized on Windows:** try `py -m venv .venv` instead, or reinstall Python with **"Add python.exe to PATH"** checked.

---

## 3 — Database setup (Optional for offline mode)

- **Testing quickly without MySQL:** Skip straight to **Step 4**. Cadence will automatically create and use `chinni_offline.db`.
- **Using MySQL Server (optional):** Copy `.env.example` to `.env` and fill in your MySQL root password:

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
notepad .env
```

**Mac / Linux (Terminal):**
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

## 4 — Initialize the database and load demo accounts

This creates all tables, ensures the **Admin** account exists, and seeds 3 demo student accounts with JEE Main 2026 & CBSE 12th Board tracks, chapter-wise syllabi, sample tests (`T1`–`T3`), study plans, and focus sessions:

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\python.exe -m backend.seed.seed_data
```

**Mac / Linux (Terminal):**
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

*(You can also create brand-new accounts anytime via **Sign Up** in the app and pick a starting track such as **CBSE 8th Grade**, **JEE Main 2026**, or **CBSE 12th Board**.)*

---

## 5 — Start the backend server

Keep this terminal open while using the app.

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\python.exe run_backend.py
```

**Mac / Linux (Terminal):**
```bash
.venv/bin/python run_backend.py
```

Wait until you see:
```text
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## 6 — Launch the desktop UI

Open a **second** terminal window, navigate into `chinni-app`, and launch the app:

**Windows (PowerShell):**
```powershell
Set-Location "$env:USERPROFILE\Projects\chinni-app"
.\.venv\Scripts\python.exe run_app.py
```

**Mac / Linux (Terminal):**
```bash
cd ~/Projects/chinni-app
.venv/bin/python run_app.py
```

1. **Log In or Sign Up** on the Cadence login screen (`admin / admin123`, any seeded student account, or click **Don't have an account? Sign Up** to create a new account and choose a starting track like **CBSE 8th Grade**).
2. The bottom-left corner shows a green **`● API Connected (8000)`** badge when connected to the backend.
3. Explore the 5 screens in the sidebar:
   - **Dashboard**: Track scorecard, target deficit, momentum, and subject averages.
   - **Log a Test**: Multi-subject mode (e.g. JEE Main) or Single-Subject flexible-marks mode (e.g. CBSE 8th Grade) with chapter checkboxes.
   - **Trends & Ranking**: Score progression and a flexible **Suggested Study Mix** with one-click **`▶ Start Sprint`** buttons.
   - **Focus Timer**: Pomodoro sprints with **`✨ Suggested Next Up`** that dynamically rebalance future suggestions as you log sessions.
   - **Settings**: Change username/password (requires current password), add new tracks, edit target scores, or delete tracks with confirmation.

---

## 7 — Run the test suite

From the `chinni-app` folder:

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
```

**Mac / Linux (Terminal):**
```bash
.venv/bin/python -m pytest tests -v
```

Expected output: `21 passed`.

> **Note:** Running `pytest` writes test records into the active database (`chinni_offline.db` or MySQL). To reset back to clean demo data afterward on offline storage:
> ```powershell
> Remove-Item chinni_offline.db -ErrorAction SilentlyContinue
> .\.venv\Scripts\python.exe -m backend.seed.seed_data
> ```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `could not create work tree dir ... Permission denied` | You are in a protected folder (like `C:\Windows\System32` from an Admin PowerShell, or a OneDrive-locked folder). Follow Step 1 to clone into `$env:USERPROFILE\Projects` instead. |
| `.\.venv\Scripts\python.exe was not recognized` | `.venv` was not created — usually because `python -m venv .venv` failed (Python wasn't installed / hit Microsoft Store stub) or you were not inside `chinni-app`. Run `Set-Location "$env:USERPROFILE\Projects\chinni-app"` and `py -m venv .venv` (or install Python 3.10+ from python.org). |
| `python` not found or opens Microsoft Store | Install the latest Python (3.10+) from python.org and tick **"Add python.exe to PATH"**, or use `py` instead of `python` on Windows. |
| `Activate.ps1 cannot be loaded` | Not needed if you run `.\.venv\Scripts\python.exe ...` directly as shown in Steps 2–7. (If you still want activation, run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` once.) |
| `pip install` fails building wheels | Upgrade pip first (`.\.venv\Scripts\python.exe -m pip install --upgrade pip`) and make sure you have an active internet connection (if testing a brand-new pre-release Python like an alpha/beta, use the latest stable release). |
| `No module named tkinter` (Linux) | Install Tk support: `sudo apt install python3-tk`. |
| MySQL connection refused | Ignore if testing locally — Cadence automatically falls back to `chinni_offline.db`. |
| Login shows "Cannot reach backend" | Make sure Step 5 (`run_backend.py`) is running in another terminal first. |

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
