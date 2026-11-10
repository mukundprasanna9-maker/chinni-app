# Cadence (`chinni-app`)
### Study Rhythm, Multi-Subject Score Tracker & Focus Planner

Cadence is a teachable four-layer Python application designed for competitive exam aspirants (such as JEE Main & Advanced, CBSE 12th Board, and custom academic tracks). It helps students track multi-subject test scores (Mathematics, Physics, Chemistry), diagnose group-level weaknesses (G1, G2, G3), allocate study hours using data-driven spend ranking, and log deep work sessions via an integrated focus timer.

---

## 1. Architecture Overview (The 4-Layer Rule)

The codebase strictly adheres to a **four-layer architecture** where each layer has exactly one job and calls only the layer directly beneath it:

```
┌──────────────────────────────────────────────────────────┐
│                   Layer 1: UI Layer                      │
│            (CustomTkinter screens in `ui/`)             │
│        Dynamic student selector, cards & focus timer     │
└────────────────────────────┬─────────────────────────────┘
                             │  HTTP requests via api_client.py
                             ▼
┌──────────────────────────────────────────────────────────┐
│                  Layer 2: API Layer                      │
│               (FastAPI in `backend/api/`)                │
│       Pydantic validation, routes, and responses         │
└────────────────────────────┬─────────────────────────────┘
                             │  Calls service functions
                             ▼
┌──────────────────────────────────────────────────────────┐
│                Layer 3: Service Layer                    │
│            (Business Logic in `backend/services/`)       │
│        Scoring maths, spend ranking & adherence          │
└────────────────────────────┬─────────────────────────────┘
                             │  Calls repository functions
                             ▼
┌──────────────────────────────────────────────────────────┐
│              Layer 4: Repository Layer                   │
│          (Raw SQL in `backend/repositories/`)            │
│       Official mysql-connector-python queries            │
└────────────────────────────┬─────────────────────────────┘
                             │  SQL Queries & Transactions
                             ▼
                    MySQL Database Server
```


- **A layer never skips another:**
  - The UI never writes SQL.
  - The API routes never do mathematical scoring calculations.
  - The Service functions never know about HTTP requests or status codes.
  - The Repository layer is the *only* code that executes database queries.
- **Teachable Functions:** Every core function is written as an explicit verb (`log_test`, `calculate_percentage`, `rank_groups_to_focus`) without confusing multi-level object inheritance.
- **Formula Transparency:** All scoring, deficit, and hour allocation formulas in `backend/services/scoring.py` and `backend/services/spend_ranking.py` include explicit docstring explanations.

---

## 2. Multi-Subject Flexible Data Model

Names (such as student names like `Mukund`) are **not hardcoded** and are dynamically managed as database records.

### Academic Tracks & Subject Structure
For JEE Main:
- **Subjects:**
  1. **Mathematics** (100 marks)
     - `G1`: Algebra (Matrices, Quadratic, Sequences, Complex Numbers)
     - `G2`: Calculus (Limits, Derivatives, Integrals, Differential Equations)
     - `G3`: Coordinate Geometry & Vectors (Circles, Conics, 3D Geometry, Vectors)
  2. **Physics** (100 marks)
     - `G1`: Mechanics (Kinematics, Newton's Laws, Work-Energy, Rotation)
     - `G2`: Electrodynamics (Electrostatics, Current, Magnetism, EMI & AC)
     - `G3`: Modern Physics & Optics (Photoelectric, Atoms, Wave & Ray Optics)
  3. **Chemistry** (100 marks)
     - `G1`: Physical Chemistry (Thermodynamics, Equilibrium, Electrochemistry)
     - `G2`: Inorganic Chemistry (Coordination Compounds, Periodic Trends, p/d-block)
     - `G3`: Organic Chemistry (Hydrocarbons, GOC, Aldehydes, Amines)

- **Test Attempts (`T1`, `T2`, `T3...`):** Each attempt records:
  - Total score and maximum possible marks.
  - Subject-level marks (Maths, Physics, Chem).
  - Group-level marks (G1, G2, G3 per subject) for granular diagnostic ranking.

---

## 3. Local Setup Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- MySQL Server 8.0+ (Local Community Server, XAMPP, or MariaDB)

### Step 1: Create and Activate Virtual Environment
Open PowerShell or your terminal inside the repository folder:

```powershell
# Create virtual environment
python -m venv .venv

# Activate on Windows PowerShell
.\.venv\Scripts\Activate.ps1

# (Or on Command Prompt)
.\.venv\Scripts\activate.bat

# (Or on macOS/Linux)
source .venv/bin/activate
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Configure Database (`.env`)
Copy `.env.example` to `.env` and specify your MySQL credentials:

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=chinni_db
```

> **Note on Offline Development:** If your MySQL server is temporarily offline, the repository layer automatically detects this and falls back to a local storage file (`chinni_offline.db`) so you can run, test, and demo the application without errors. Starting your MySQL service switches Cadence to MySQL automatically.

### Step 4: Seed Initial Data
Run the seeding script to create tables and load demo student profiles, JEE/CBSE tracks, and sample test attempts (`T1`, `T2`, `T3`):

```powershell
# You can pass any student name dynamically
python -m backend.seed.seed_data Mukund
```

---

## 4. How to Run

### 1. Start the FastAPI Backend Server
In your first terminal:
```powershell
python run_backend.py
```
- API Server starts at: `http://127.0.0.1:8000`
- Interactive Swagger UI documentation: `http://127.0.0.1:8000/docs`
- Health check endpoint: `http://127.0.0.1:8000/health`

### 2. Launch the CustomTkinter UI
In a second terminal (with `.venv` activated):
```powershell
python run_app.py
```
- Launches the modern dark-mode desktop interface.
- Includes a live backend connection badge, student & track dropdowns, scorecard hero cards, Log Test form, Trends table, and the interactive Pomodoro Focus Timer.

### 3. Run the Automated Test Suite
To verify the entire repository layer, scoring logic, spend rankings, and API integration:
```powershell
pytest -v
```

---

## 5. Tracing the Core Feature Through All 4 Layers

Use the **"Log a Test"** workflow during your viva to explain the full cycle:

```
[UI Screen] (ui/tests_screen.py)
   │  User fills Test Code (e.g. T4), Date, Maths/Physics/Chem scores, and clicks "Save"
   ▼
[API Client] (ui/api_client.py)
   │  Formats payload as JSON and sends POST /tracks/{track_id}/tests over HTTP
   ▼
[API Route] (backend/api/tests.py)
   │  Validates request shape using Pydantic TestCreate schema
   ▼
[Service & Calculations] (backend/services/scoring.py)
   │  Validates score bounds, calculates percentages & updates test trend delta
   ▼
[Repository Layer] (backend/repositories/test_repo.py)
   │  Executes transactional SQL:
   │  INSERT INTO tests (...)
   │  INSERT INTO test_subject_scores (...)
   │  INSERT INTO test_group_scores (...)
   ▼
[Response Back Up]
   │  Repository returns newly created test record dict -> Route returns 201 Created ->
   │  api_client receives JSON -> Screen displays green success badge and updates history table
```

---

## 6. Q&A 

### Q1: Why did we choose a 4-layer architecture instead of writing SQL directly in Tkinter?
**Answer:** Separation of concerns. If we ever want to build a mobile app, web frontend, or CLI, the backend API, business logic, and database remain unchanged. It also ensures business logic (scoring formulas) can be tested with unit tests independently of the UI.

### Q2: How does the "Spend Ranking" algorithm work?
**Answer:** In `backend/services/spend_ranking.py`, we identify where study time yields the highest score gain. For each subject group (e.g., Calculus or Electrodynamics), we calculate:
$$\text{Deficit} = \text{Max Marks} - \text{Latest Score}$$
$$\text{Opportunity Index} = \text{Deficit} \times \left(\frac{\text{Weight Percentage}}{100}\right)$$
We sort groups by Opportunity Index descending and allocate available study hours proportionally.

### Q3: How are three subjects handled for JEE?
**Answer:** Each track has multiple subject records in the `subjects` table (Mathematics, Physics, Chemistry). Each subject has groups in `subject_groups` (`G1`, `G2`, `G3`). When a test attempt (`T1`, `T2`...) is logged, the `test_subject_scores` table stores subject totals, and `test_group_scores` stores individual group marks.

### Q4: How is MySQL integrated?
**Answer:** We use the official `mysql-connector-python` library without an ORM. Connections are created using `mysql.connector.connect()` with credentials loaded securely from `.env`. Parameterized queries (`%s`) are used to prevent SQL injection.

---

## 7. Project File Structure

```
chinni-app/
├── README.md                      # Complete setup & viva documentation
├── requirements.txt               # Pinned dependencies
├── .env.example                   # Environment variable template
├── .env                           # Local MySQL configuration
├── run_backend.py                 # Starts the FastAPI server on port 8000
├── run_app.py                     # Starts the CustomTkinter UI application
│
├── backend/
│   ├── main.py                    # FastAPI application initialization & middleware
│   ├── api/                       # Layer 2: HTTP routes
│   │   ├── students.py            # /students CRUD
│   │   ├── tracks.py              # /tracks, /subjects, /groups
│   │   ├── tests.py               # /tracks/{id}/tests
│   │   ├── plans.py               # /plans, /focus-sessions
│   │   └── analytics.py           # /scorecard, /focus-rankings, /adherence
│   ├── schemas/                   # Pydantic request/response validation
│   │   ├── student.py
│   │   ├── track.py
│   │   ├── test_result.py
│   │   └── plan.py
│   ├── services/                  # Layer 3: Pure business logic
│   │   ├── scoring.py             # Score formulas, averages, gaps, trend deltas
│   │   ├── spend_ranking.py       # Group & subject weakness ranking
│   │   └── planning.py            # Study hour allocation & adherence
│   ├── repositories/              # Layer 4: Raw SQL with mysql-connector-python
│   │   ├── database.py            # Connection management & schema migrations
│   │   ├── student_repo.py        # Students SQL
│   │   ├── track_repo.py          # Tracks, subjects & groups SQL
│   │   ├── test_repo.py           # Tests, subject & group score SQL
│   │   └── plan_repo.py           # Plans & focus sessions SQL
│   └── seed/
│       └── seed_data.py           # Dynamic seeding for JEE & CBSE tracks
│
├── ui/                            # Layer 1: CustomTkinter GUI
│   ├── api_client.py              # ONLY file making HTTP calls to backend
│   ├── home_screen.py             # Dashboard, student/track switcher, cards
│   ├── tests_screen.py            # Log a Test form with Maths/Phy/Chem breakdown
│   ├── trends_screen.py           # Performance progression & spend ranking view
│   └── focus_timer.py             # Interactive Pomodoro focus timer & adherence
│
└── tests/                         # Automated test suite (16 tests)
    ├── test_repositories.py       # DB & repository CRUD verification
    ├── test_scoring.py            # Scoring service calculations
    ├── test_planning.py           # Spend ranking & hours allocation
    └── test_api.py                # End-to-end API integration tests
```
