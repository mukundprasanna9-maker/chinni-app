import pytest
from starlette.testclient import TestClient
from backend.main import app
from backend.repositories.database import init_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["app"] == "chinni-app"


def test_student_endpoints():
    # Create student
    res = client.post("/students", json={"name": "Alice Verma", "target_score": 240})
    assert res.status_code == 201
    student = res.json()
    assert student["name"] == "Alice Verma"
    assert student["target_score"] == 240

    # Fetch student
    res = client.get(f"/students/{student['id']}")
    assert res.status_code == 200
    assert res.json()["id"] == student["id"]

    # Update student
    res = client.put(f"/students/{student['id']}", json={"name": "Alice V.", "target_score": 245})
    assert res.status_code == 200
    assert res.json()["name"] == "Alice V."
    assert res.json()["target_score"] == 245


def test_full_track_subject_group_and_test_flow():
    # 1. Create Student
    s_res = client.post("/students", json={"name": "Bob Sharma", "target_score": 235})
    student = s_res.json()
    student_id = student["id"]

    # 2. Create JEE Track
    t_res = client.post(
        f"/students/{student_id}/tracks",
        json={"name": "JEE Main Mock Series", "target_score": 235, "max_score": 300},
    )
    assert t_res.status_code == 201
    track = t_res.json()
    track_id = track["id"]

    # 3. Create 3 Subjects (Maths, Physics, Chemistry)
    sub_m = client.post(f"/tracks/{track_id}/subjects", json={"name": "Mathematics", "code": "MATH", "max_marks": 100, "target_marks": 80}).json()
    sub_p = client.post(f"/tracks/{track_id}/subjects", json={"name": "Physics", "code": "PHY", "max_marks": 100, "target_marks": 80}).json()
    sub_c = client.post(f"/tracks/{track_id}/subjects", json={"name": "Chemistry", "code": "CHEM", "max_marks": 100, "target_marks": 75}).json()

    # 4. Create Groups (G1, G2, G3) for Maths
    g_m1 = client.post(f"/subjects/{sub_m['id']}/groups", json={"group_code": "G1", "name": "Algebra", "weight_percentage": 33.3}).json()
    g_m2 = client.post(f"/subjects/{sub_m['id']}/groups", json={"group_code": "G2", "name": "Calculus", "weight_percentage": 33.3}).json()
    g_m3 = client.post(f"/subjects/{sub_m['id']}/groups", json={"group_code": "G3", "name": "Coordinate Geometry", "weight_percentage": 33.4}).json()

    # 5. Log Test T1 with Subject and Group Breakdowns
    test_payload = {
        "test_code": "T1",
        "test_date": "2026-11-06",
        "total_score": 185.0,
        "max_score": 300.0,
        "notes": "End-to-End API Test attempt",
        "subject_scores": [
            {"subject_id": sub_m["id"], "score": 55.0, "max_score": 100.0, "accuracy_percent": 70.0, "time_spent_minutes": 60},
            {"subject_id": sub_p["id"], "score": 62.0, "max_score": 100.0, "accuracy_percent": 75.0, "time_spent_minutes": 60},
            {"subject_id": sub_c["id"], "score": 68.0, "max_score": 100.0, "accuracy_percent": 82.0, "time_spent_minutes": 60},
        ],
        "group_scores": [
            {"group_id": g_m1["id"], "score": 20.0, "max_score": 33.3},
            {"group_id": g_m2["id"], "score": 16.0, "max_score": 33.3},
            {"group_id": g_m3["id"], "score": 19.0, "max_score": 33.4},
        ],
    }

    t_res = client.post(f"/tracks/{track_id}/tests", json=test_payload)
    assert t_res.status_code == 201
    created_test = t_res.json()
    assert created_test["total_score"] == 185.0
    assert len(created_test["subject_scores"]) == 3
    assert len(created_test["group_scores"]) == 3

    # 6. Verify Scorecard Endpoint
    sc_res = client.get(f"/tracks/{track_id}/scorecard")
    assert sc_res.status_code == 200
    scorecard = sc_res.json()
    assert scorecard["test_count"] == 1
    assert scorecard["latest_score"] == 185.0
    assert scorecard["gap_to_target"] == 50.0

    # 7. Verify Focus Rankings Endpoint
    rk_res = client.get(f"/tracks/{track_id}/focus-rankings")
    assert rk_res.status_code == 200
    rankings = rk_res.json()
    assert len(rankings["ranked_groups"]) >= 3
    assert len(rankings["recommended_allocations"]) >= 1


def test_plans_and_focus_api():
    # Create student
    s_res = client.post("/students", json={"name": "Charlie", "target_score": 210})
    student_id = s_res.json()["id"]

    # Create plan
    plan_res = client.post(
        f"/students/{student_id}/plans",
        json={"target_date": "2026-11-15", "planned_hours": 5.0, "notes": "Complete Mechanics Chapter"},
    )
    assert plan_res.status_code == 201
    plan = plan_res.json()
    assert plan["planned_hours"] == 5.0

    # Update plan actual hours
    up_res = client.put(f"/plans/{plan['id']}", json={"actual_hours": 4.5, "status": "COMPLETED"})
    assert up_res.status_code == 200
    assert up_res.json()["actual_hours"] == 4.5

    # Check adherence endpoint
    adh_res = client.get(f"/students/{student_id}/adherence")
    assert adh_res.status_code == 200
    assert adh_res.json()["overall_adherence_percent"] == 90.0
    assert adh_res.json()["status"] == "ON TRACK"

    # Add focus session
    fs_res = client.post(
        f"/students/{student_id}/focus-sessions",
        json={"duration_minutes": 50, "notes": "Pomodoro Block 1", "adherence_status": "COMPLETED"},
    )
    assert fs_res.status_code == 201
    assert fs_res.json()["duration_minutes"] == 50
