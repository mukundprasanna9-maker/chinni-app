import pytest
from backend.repositories.database import init_db
from backend.repositories.student_repo import (
    create_student,
    get_student_by_id,
    get_all_students,
    update_student,
)
from backend.repositories.track_repo import (
    create_track,
    get_tracks_by_student,
    create_subject,
    get_subjects_by_track,
    create_group,
    get_groups_by_subject,
)
from backend.repositories.test_repo import (
    create_test,
    get_test_by_id,
    get_tests_by_track,
    get_all_group_scores_for_track,
)
from backend.repositories.plan_repo import (
    create_study_plan,
    get_study_plans,
    create_focus_session,
    get_focus_sessions,
)


@pytest.fixture(autouse=True)
def setup_database():
    init_db()


def test_student_crud():
    student = create_student(name="TestStudent", target_score=240)
    assert student is not None
    assert student["name"] == "TestStudent"
    assert student["target_score"] == 240

    fetched = get_student_by_id(student["id"])
    assert fetched is not None
    assert fetched["name"] == "TestStudent"

    updated = update_student(student["id"], name="UpdatedStudent", target_score=250)
    assert updated["name"] == "UpdatedStudent"
    assert updated["target_score"] == 250

    all_students = get_all_students()
    assert any(s["id"] == student["id"] for s in all_students)


def test_track_subjects_and_groups():
    student = create_student(name="TrackTester", target_score=220)
    track = create_track(student["id"], "JEE Advanced", target_score=220, max_score=360)
    assert track["name"] == "JEE Advanced"

    sub_math = create_subject(track["id"], "Mathematics", "MATH", max_marks=120)
    sub_phy = create_subject(track["id"], "Physics", "PHY", max_marks=120)
    sub_chem = create_subject(track["id"], "Chemistry", "CHEM", max_marks=120)

    subjects = get_subjects_by_track(track["id"])
    assert len(subjects) == 3
    codes = [s["code"] for s in subjects]
    assert "MATH" in codes and "PHY" in codes and "CHEM" in codes

    g1 = create_group(sub_math["id"], "G1", "Algebra", "Vectors & Matrices", 33.3)
    g2 = create_group(sub_math["id"], "G2", "Calculus", "Differentiation & Integration", 33.3)
    g3 = create_group(sub_math["id"], "G3", "Coordinate", "Conics & 3D", 33.4)

    groups = get_groups_by_subject(sub_math["id"])
    assert len(groups) == 3
    assert [g["group_code"] for g in groups] == ["G1", "G2", "G3"]


def test_test_logging_slice():
    student = create_student(name="TestLogger", target_score=235)
    track = create_track(student["id"], "JEE Main Track", target_score=235, max_score=300)
    sub_math = create_subject(track["id"], "Mathematics", "MATH", max_marks=100)
    sub_phy = create_subject(track["id"], "Physics", "PHY", max_marks=100)
    sub_chem = create_subject(track["id"], "Chemistry", "CHEM", max_marks=100)

    g_math_1 = create_group(sub_math["id"], "G1", "Algebra", "", 33.3)
    g_phy_1 = create_group(sub_phy["id"], "G1", "Mechanics", "", 33.3)
    g_chem_1 = create_group(sub_chem["id"], "G1", "Physical Chem", "", 33.3)

    test_record = create_test(
        track_id=track["id"],
        test_code="T1",
        test_date="2026-11-05",
        total_score=195.0,
        max_score=300.0,
        notes="Full length mock 1",
        subject_scores=[
            {"subject_id": sub_math["id"], "score": 60.0, "max_score": 100.0, "accuracy_percent": 75.0, "time_spent_minutes": 60},
            {"subject_id": sub_phy["id"], "score": 65.0, "max_score": 100.0, "accuracy_percent": 80.0, "time_spent_minutes": 60},
            {"subject_id": sub_chem["id"], "score": 70.0, "max_score": 100.0, "accuracy_percent": 85.0, "time_spent_minutes": 60},
        ],
        group_scores=[
            {"group_id": g_math_1["id"], "score": 20.0, "max_score": 33.3},
            {"group_id": g_phy_1["id"], "score": 22.0, "max_score": 33.3},
            {"group_id": g_chem_1["id"], "score": 24.0, "max_score": 33.3},
        ],
    )

    assert test_record["id"] is not None
    assert test_record["total_score"] == 195.0
    assert len(test_record["subject_scores"]) == 3
    assert len(test_record["group_scores"]) == 3

    track_tests = get_tests_by_track(track["id"])
    assert len(track_tests) >= 1

    group_history = get_all_group_scores_for_track(track["id"])
    assert len(group_history) >= 3


def test_plans_and_focus_sessions():
    student = create_student(name="PlanUser", target_score=235)
    plan = create_study_plan(
        student_id=student["id"],
        group_id=None,
        subject_id=None,
        target_date="2026-11-12",
        planned_hours=4.0,
        notes="Solve 30 problems",
    )
    assert plan["planned_hours"] == 4.0
    plans = get_study_plans(student["id"])
    assert len(plans) >= 1

    session = create_focus_session(
        student_id=student["id"],
        subject_id=None,
        group_id=None,
        duration_minutes=45,
        notes="Sprint 1 done",
    )
    assert session["duration_minutes"] == 45
    sessions = get_focus_sessions(student["id"])
    assert len(sessions) >= 1
