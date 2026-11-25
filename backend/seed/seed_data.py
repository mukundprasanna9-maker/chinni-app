"""Seed script for Cadence (chinni-app).

Populates the database with:
- Admin account (admin / admin123)
- 3 user accounts with realistic, distinct student profiles, tracks, tests,
  study plans, and focus sessions:
    1. Mukund Prasanna       / 1studyproject
    2. Sarvesh Umesh Kulkarni / 2studyproject
    3. Arya Nandan Srinivas  / 3studyproject
"""

import sys
from backend.repositories.database import init_db
from backend.repositories.user_repo import create_user, ensure_admin_exists, get_user_by_username
from backend.repositories.student_repo import create_student, get_all_students
from backend.repositories.track_repo import (
    create_track,
    create_subject,
    create_group,
    get_tracks_by_student,
)
from backend.repositories.test_repo import create_test
from backend.repositories.plan_repo import create_study_plan, create_focus_session


DEFAULT_ACCOUNTS = [
    {
        "username": "Mukund Prasanna",
        "password": "1studyproject",
        "target_score": 235,
        "tests": [
            ("T1", "2026-09-15", "Diagnostic Test 1 - Baseline attempt", (48.0, 54.0, 60.0), (18, 14, 16, 20, 16, 18, 22, 20, 18)),
            ("T2", "2026-10-10", "Revision Mock 2 - Improved Calculus & Mechanics", (58.0, 64.0, 66.0), (22, 18, 18, 23, 20, 21, 24, 22, 20)),
            ("T3", "2026-11-01", "Sprint Mock 3 - Close to 210 mark", (65.0, 68.0, 72.0), (25, 21, 19, 24, 22, 22, 26, 24, 22)),
        ],
        "plan": ("2026-11-10", 3.5, "Focus on Definite Integrals and Area Under Curve"),
        "focus": (50, "Solved 15 PYQs on Integration"),
    },
    {
        "username": "Sarvesh Umesh Kulkarni",
        "password": "2studyproject",
        "target_score": 250,
        "tests": [
            ("T1", "2026-09-16", "Diagnostic Test 1 - Strong Physics start", (55.0, 66.0, 58.0), (20, 17, 18, 24, 21, 21, 20, 19, 19)),
            ("T2", "2026-10-11", "Revision Mock 2 - Organic Chemistry boost", (60.0, 70.0, 68.0), (22, 19, 19, 25, 22, 23, 23, 21, 24)),
            ("T3", "2026-11-02", "Sprint Mock 3 - Steady upward trend", (68.0, 76.0, 71.0), (24, 22, 22, 27, 24, 25, 24, 23, 24)),
        ],
        "plan": ("2026-11-12", 4.0, "Master Electrodynamics and EMI problem sets"),
        "focus": (60, "Completed 20 Electrostatics numericals"),
    },
    {
        "username": "Arya Nandan Srinivas",
        "password": "3studyproject",
        "target_score": 240,
        "tests": [
            ("T1", "2026-09-17", "Diagnostic Test 1 - High Chemistry accuracy", (52.0, 50.0, 68.0), (19, 16, 17, 18, 15, 17, 24, 22, 22)),
            ("T2", "2026-10-12", "Revision Mock 2 - Algebra & Optics catch-up", (62.0, 58.0, 72.0), (23, 19, 20, 20, 18, 20, 25, 24, 23)),
            ("T3", "2026-11-03", "Sprint Mock 3 - Balanced across all 3 subjects", (70.0, 64.0, 78.0), (26, 22, 22, 22, 20, 22, 27, 26, 25)),
        ],
        "plan": ("2026-11-14", 3.0, "Strengthen Rotation & Ray Optics fundamentals"),
        "focus": (45, "Revised Rotational Dynamics concepts & PYQs"),
    },
]


def create_default_jee_track(student_id: int, target_score: int = 235) -> dict:
    """Create the default JEE Main 2026 track with Maths, Physics, Chemistry and G1/G2/G3 groups."""
    jee_track = create_track(
        student_id=student_id,
        name="JEE Main 2026",
        target_score=target_score,
        max_score=300,
    )

    math = create_subject(jee_track["id"], "Mathematics", "MATH", max_marks=100, target_marks=80)
    phy = create_subject(jee_track["id"], "Physics", "PHY", max_marks=100, target_marks=80)
    chem = create_subject(jee_track["id"], "Chemistry", "CHEM", max_marks=100, target_marks=75)

    m_g1 = create_group(math["id"], "G1", "Algebra", "Quadratic, Sequences, Matrices, Complex", 33.3)
    m_g2 = create_group(math["id"], "G2", "Calculus", "Limits, Derivatives, Integrals, Diff Eq", 33.3)
    m_g3 = create_group(math["id"], "G3", "Coordinate Geometry & Vectors", "Circles, Conics, 3D Geometry, Vectors", 33.4)

    p_g1 = create_group(phy["id"], "G1", "Mechanics", "Kinematics, Newton's Laws, Work-Energy, Rotation", 33.3)
    p_g2 = create_group(phy["id"], "G2", "Electrodynamics", "Electrostatics, Current, Magnetism, EMI & AC", 33.3)
    p_g3 = create_group(phy["id"], "G3", "Modern Physics & Optics", "Photoelectric, Atoms, Wave & Ray Optics", 33.4)

    c_g1 = create_group(chem["id"], "G1", "Physical Chemistry", "Thermodynamics, Equilibrium, Electrochemistry", 33.3)
    c_g2 = create_group(chem["id"], "G2", "Inorganic Chemistry", "Coordination, Periodic Trends, p-block, d-block", 33.3)
    c_g3 = create_group(chem["id"], "G3", "Organic Chemistry", "Hydrocarbons, GOC, Aldehydes, Amines", 33.4)

    return {
        "track": jee_track,
        "subjects": (math, phy, chem),
        "groups": (m_g1, m_g2, m_g3, p_g1, p_g2, p_g3, c_g1, c_g2, c_g3),
    }


def _seed_account(account: dict) -> None:
    """Create a user account (if missing) and populate its student, tracks, tests, and plans."""
    username = account["username"]
    user = get_user_by_username(username)
    if not user:
        user = create_user(username, account["password"], is_admin=False)
        print(f"[Seed] Created user '{username}' (ID: {user['id']})")
    else:
        print(f"[Seed] User '{username}' already exists (ID: {user['id']}).")

    # Check if a student already exists for this user
    existing_students = get_all_students(user_id=user["id"])
    if existing_students:
        student = existing_students[0]
        if get_tracks_by_student(student["id"]):
            print(f"[Seed] Student '{student['name']}' already has seeded tracks. Skipping.")
            return
    else:
        student = create_student(name=username, target_score=account["target_score"], user_id=user["id"])
        print(f"[Seed] Created student '{student['name']}' (ID: {student['id']})")

    student_id = student["id"]

    # 1. JEE Main 2026 Track
    jee_bundle = create_default_jee_track(student_id, target_score=account["target_score"])
    jee_track = jee_bundle["track"]
    math, phy, chem = jee_bundle["subjects"]
    groups = jee_bundle["groups"]

    # 2. CBSE 12th Board Track
    cbse_track = create_track(
        student_id=student_id,
        name="CBSE 12th Board",
        target_score=470,
        max_score=500,
    )
    create_subject(cbse_track["id"], "Mathematics", "MATH-12", 100, 95)
    create_subject(cbse_track["id"], "Physics", "PHY-12", 100, 95)
    create_subject(cbse_track["id"], "Chemistry", "CHEM-12", 100, 95)
    create_subject(cbse_track["id"], "English Core", "ENG-12", 100, 95)
    create_subject(cbse_track["id"], "Computer Science", "CS-12", 100, 90)

    # 3. Sample Tests (T1, T2, T3)
    for code, t_date, notes, (m_s, p_s, c_s), grp_scores in account["tests"]:
        total = m_s + p_s + c_s
        create_test(
            track_id=jee_track["id"],
            test_code=code,
            test_date=t_date,
            total_score=total,
            max_score=300.0,
            notes=notes,
            subject_scores=[
                {"subject_id": math["id"], "score": m_s, "max_score": 100.0, "accuracy_percent": 75.0, "time_spent_minutes": 60},
                {"subject_id": phy["id"], "score": p_s, "max_score": 100.0, "accuracy_percent": 78.0, "time_spent_minutes": 55},
                {"subject_id": chem["id"], "score": c_s, "max_score": 100.0, "accuracy_percent": 82.0, "time_spent_minutes": 50},
            ],
            group_scores=[
                {"group_id": grp["id"], "score": float(score_val), "max_score": float(grp.get("weight_percentage") or 33.3)}
                for grp, score_val in zip(groups, grp_scores)
            ],
        )

    # 4. Sample Study Plan & Focus Session
    plan_date, plan_hrs, plan_notes = account["plan"]
    create_study_plan(
        student_id=student_id,
        group_id=groups[1]["id"],
        subject_id=math["id"],
        target_date=plan_date,
        planned_hours=plan_hrs,
        notes=plan_notes,
    )
    focus_mins, focus_notes = account["focus"]
    create_focus_session(
        student_id=student_id,
        subject_id=math["id"],
        group_id=groups[1]["id"],
        duration_minutes=focus_mins,
        notes=focus_notes,
        adherence_status="COMPLETED",
    )
    print(f"[Seed] Seeded tracks, tests (T1-T3), plan, and focus session for '{username}'.")


def seed_database(student_name: str | None = None, target_score: int = 235):
    """Initializes the DB, ensures admin exists, and seeds the 3 accounts (or a custom one if specified)."""
    print("Initializing database schema...")
    init_db()
    ensure_admin_exists()

    if student_name:
        _seed_account({
            "username": student_name,
            "password": "1studyproject",
            "target_score": target_score,
            "tests": DEFAULT_ACCOUNTS[0]["tests"],
            "plan": DEFAULT_ACCOUNTS[0]["plan"],
            "focus": DEFAULT_ACCOUNTS[0]["focus"],
        })
    else:
        for account in DEFAULT_ACCOUNTS:
            _seed_account(account)

    print("Database seeding completed successfully!")


if __name__ == "__main__":
    name_arg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    seed_database(student_name=name_arg)
