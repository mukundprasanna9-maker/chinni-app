import sys
from backend.repositories.database import init_db
from backend.repositories.student_repo import create_student, get_all_students
from backend.repositories.track_repo import (
    create_track,
    create_subject,
    create_group,
)
from backend.repositories.test_repo import create_test
from backend.repositories.plan_repo import create_study_plan, create_focus_session


def seed_database(student_name: str = "Mukund", target_score: int = 235):
    """Populates the database with initial flexible tracks, subjects, groups, and tests."""
    print("Initializing database schema...")
    init_db()

    # Check if student already exists
    existing = [s for s in get_all_students() if s["name"].lower() == student_name.lower()]
    if existing:
        print(f"Student '{student_name}' already exists with ID {existing[0]['id']}. Using existing.")
        student = existing[0]
    else:
        student = create_student(name=student_name, target_score=target_score)
        print(f"Created student '{student['name']}' with ID {student['id']}")

    student_id = student["id"]

    # 1. Create JEE Main Track
    jee_track = create_track(
        student_id=student_id,
        name="JEE Main 2026",
        target_score=target_score,
        max_score=300,
    )
    print(f"Created track '{jee_track['name']}' (ID: {jee_track['id']})")

    # JEE Subjects: Maths, Physics, Chemistry
    math = create_subject(jee_track["id"], "Mathematics", "MATH", max_marks=100, target_marks=80)
    phy = create_subject(jee_track["id"], "Physics", "PHY", max_marks=100, target_marks=80)
    chem = create_subject(jee_track["id"], "Chemistry", "CHEM", max_marks=100, target_marks=75)

    # Maths Groups: G1, G2, G3
    m_g1 = create_group(math["id"], "G1", "Algebra", "Quadratic, Sequences, Matrices, Complex", 33.3)
    m_g2 = create_group(math["id"], "G2", "Calculus", "Limits, Derivatives, Integrals, Diff Eq", 33.3)
    m_g3 = create_group(math["id"], "G3", "Coordinate Geometry & Vectors", "Circles, Conics, 3D Geometry, Vectors", 33.4)

    # Physics Groups: G1, G2, G3
    p_g1 = create_group(phy["id"], "G1", "Mechanics", "Kinematics, Newton's Laws, Work-Energy, Rotation", 33.3)
    p_g2 = create_group(phy["id"], "G2", "Electrodynamics", "Electrostatics, Current, Magnetism, EMI & AC", 33.3)
    p_g3 = create_group(phy["id"], "G3", "Modern Physics & Optics", "Photoelectric, Atoms, Wave & Ray Optics", 33.4)

    # Chemistry Groups: G1, G2, G3
    c_g1 = create_group(chem["id"], "G1", "Physical Chemistry", "Thermodynamics, Equilibrium, Electrochemistry", 33.3)
    c_g2 = create_group(chem["id"], "G2", "Inorganic Chemistry", "Coordination, Periodic Trends, p-block, d-block", 33.3)
    c_g3 = create_group(chem["id"], "G3", "Organic Chemistry", "Hydrocarbons, GOC, Aldehydes, Amines", 33.4)

    # 2. Create CBSE 12th Board Track
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
    print(f"Created track '{cbse_track['name']}' (ID: {cbse_track['id']})")

    # 3. Add Sample Tests (T1, T2, T3) for JEE Track
    # T1
    create_test(
        track_id=jee_track["id"],
        test_code="T1",
        test_date="2026-09-15",
        total_score=162.0,
        max_score=300.0,
        notes="Diagnostic Test 1 - Baseline attempt",
        subject_scores=[
            {"subject_id": math["id"], "score": 48.0, "max_score": 100.0, "accuracy_percent": 68.0, "time_spent_minutes": 65},
            {"subject_id": phy["id"], "score": 54.0, "max_score": 100.0, "accuracy_percent": 72.0, "time_spent_minutes": 55},
            {"subject_id": chem["id"], "score": 60.0, "max_score": 100.0, "accuracy_percent": 80.0, "time_spent_minutes": 45},
        ],
        group_scores=[
            {"group_id": m_g1["id"], "score": 18.0, "max_score": 33.3},
            {"group_id": m_g2["id"], "score": 14.0, "max_score": 33.3},
            {"group_id": m_g3["id"], "score": 16.0, "max_score": 33.4},
            {"group_id": p_g1["id"], "score": 20.0, "max_score": 33.3},
            {"group_id": p_g2["id"], "score": 16.0, "max_score": 33.3},
            {"group_id": p_g3["id"], "score": 18.0, "max_score": 33.4},
            {"group_id": c_g1["id"], "score": 22.0, "max_score": 33.3},
            {"group_id": c_g2["id"], "score": 20.0, "max_score": 33.3},
            {"group_id": c_g3["id"], "score": 18.0, "max_score": 33.4},
        ],
    )

    # T2
    create_test(
        track_id=jee_track["id"],
        test_code="T2",
        test_date="2026-10-10",
        total_score=188.0,
        max_score=300.0,
        notes="Revision Mock 2 - Improved Calculus & Mechanics",
        subject_scores=[
            {"subject_id": math["id"], "score": 58.0, "max_score": 100.0, "accuracy_percent": 74.0, "time_spent_minutes": 60},
            {"subject_id": phy["id"], "score": 64.0, "max_score": 100.0, "accuracy_percent": 78.0, "time_spent_minutes": 55},
            {"subject_id": chem["id"], "score": 66.0, "max_score": 100.0, "accuracy_percent": 84.0, "time_spent_minutes": 50},
        ],
        group_scores=[
            {"group_id": m_g1["id"], "score": 22.0, "max_score": 33.3},
            {"group_id": m_g2["id"], "score": 18.0, "max_score": 33.3},
            {"group_id": m_g3["id"], "score": 18.0, "max_score": 33.4},
            {"group_id": p_g1["id"], "score": 23.0, "max_score": 33.3},
            {"group_id": p_g2["id"], "score": 20.0, "max_score": 33.3},
            {"group_id": p_g3["id"], "score": 21.0, "max_score": 33.4},
            {"group_id": c_g1["id"], "score": 24.0, "max_score": 33.3},
            {"group_id": c_g2["id"], "score": 22.0, "max_score": 33.3},
            {"group_id": c_g3["id"], "score": 20.0, "max_score": 33.4},
        ],
    )

    # T3
    create_test(
        track_id=jee_track["id"],
        test_code="T3",
        test_date="2026-11-01",
        total_score=205.0,
        max_score=300.0,
        notes="Sprint Mock 3 - Close to 210 mark",
        subject_scores=[
            {"subject_id": math["id"], "score": 65.0, "max_score": 100.0, "accuracy_percent": 80.0, "time_spent_minutes": 60},
            {"subject_id": phy["id"], "score": 68.0, "max_score": 100.0, "accuracy_percent": 82.0, "time_spent_minutes": 55},
            {"subject_id": chem["id"], "score": 72.0, "max_score": 100.0, "accuracy_percent": 88.0, "time_spent_minutes": 48},
        ],
        group_scores=[
            {"group_id": m_g1["id"], "score": 25.0, "max_score": 33.3},
            {"group_id": m_g2["id"], "score": 21.0, "max_score": 33.3},
            {"group_id": m_g3["id"], "score": 19.0, "max_score": 33.4},
            {"group_id": p_g1["id"], "score": 24.0, "max_score": 33.3},
            {"group_id": p_g2["id"], "score": 22.0, "max_score": 33.3},
            {"group_id": p_g3["id"], "score": 22.0, "max_score": 33.4},
            {"group_id": c_g1["id"], "score": 26.0, "max_score": 33.3},
            {"group_id": c_g2["id"], "score": 24.0, "max_score": 33.3},
            {"group_id": c_g3["id"], "score": 22.0, "max_score": 33.4},
        ],
    )
    print("Created sample test runs T1, T2, T3 with subject and group scores.")

    # 4. Add Sample Study Plans & Focus Sessions
    create_study_plan(
        student_id=student_id,
        group_id=m_g2["id"],
        subject_id=math["id"],
        target_date="2026-11-10",
        planned_hours=3.5,
        notes="Focus on Definite Integrals and Area Under Curve",
    )
    create_focus_session(
        student_id=student_id,
        subject_id=math["id"],
        group_id=m_g2["id"],
        duration_minutes=50,
        notes="Solved 15 PYQs on Integration",
        adherence_status="COMPLETED",
    )
    print("Sample study plan and focus session created.")
    print("Database seeding completed successfully!")


if __name__ == "__main__":
    name_arg = sys.argv[1] if len(sys.argv) > 1 else "Mukund"
    seed_database(student_name=name_arg)
