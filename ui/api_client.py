"""API Client for Cadence UI.

Teaching rule:
This is the ONLY file in the UI layer that makes HTTP calls.
No screen or widget directly touches network or SQL.
"""

import os
import requests
from typing import List, Dict, Any, Optional

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# ── Auth state (set after login/signup) ──────────────────────────────
_current_user: Optional[Dict[str, Any]] = None


def set_current_user(user: Optional[Dict[str, Any]]) -> None:
    global _current_user
    _current_user = user


def get_current_user() -> Optional[Dict[str, Any]]:
    return _current_user


def is_admin() -> bool:
    return bool(_current_user and _current_user.get("is_admin"))


def current_user_id() -> Optional[int]:
    return _current_user["id"] if _current_user else None


# ── Auth API calls ───────────────────────────────────────────────────
def login(username: str, password: str) -> Dict[str, Any]:
    user = _post("/auth/login", {"username": username, "password": password})
    set_current_user(user)
    return user


def signup(username: str, password: str, track_template: str = "JEE Main 2026") -> Dict[str, Any]:
    user = _post("/auth/signup", {
        "username": username,
        "password": password,
        "track_template": track_template,
    })
    set_current_user(user)
    return user


def update_account(
    user_id: int,
    current_password: str,
    new_username: Optional[str] = None,
    new_password: Optional[str] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "user_id": user_id,
        "current_password": current_password,
    }
    if new_username:
        payload["new_username"] = new_username
    if new_password:
        payload["new_password"] = new_password
    user = _put("/auth/account", payload)
    set_current_user(user)
    return user


def logout() -> None:
    set_current_user(None)


def _get(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
    url = f"{API_BASE_URL}{endpoint}"
    resp = requests.get(url, params=params, timeout=5)
    resp.raise_for_status()
    return resp.json()


def _post(endpoint: str, payload: Dict[str, Any]) -> Any:
    url = f"{API_BASE_URL}{endpoint}"
    resp = requests.post(url, json=payload, timeout=5)
    resp.raise_for_status()
    return resp.json()


def _put(endpoint: str, payload: Dict[str, Any]) -> Any:
    url = f"{API_BASE_URL}{endpoint}"
    resp = requests.put(url, json=payload, timeout=5)
    resp.raise_for_status()
    return resp.json()


def _delete(endpoint: str) -> None:
    url = f"{API_BASE_URL}{endpoint}"
    resp = requests.delete(url, timeout=5)
    resp.raise_for_status()


def check_backend_health() -> bool:
    try:
        data = _get("/health")
        return data.get("status") == "healthy"
    except Exception:
        return False


# Student Operations
def get_students() -> List[Dict[str, Any]]:
    # Admin sees all students; regular users see only their own
    if is_admin():
        return _get("/students")
    uid = current_user_id()
    if uid is not None:
        return _get("/students", params={"user_id": uid})
    return _get("/students")


def get_student(student_id: int) -> Dict[str, Any]:
    return _get(f"/students/{student_id}")


def create_student(name: str, target_score: int = 235) -> Dict[str, Any]:
    uid = current_user_id()
    endpoint = f"/students?user_id={uid}" if uid is not None else "/students"
    return _post(endpoint, {"name": name, "target_score": target_score})


# Track Operations
def get_student_tracks(student_id: int) -> List[Dict[str, Any]]:
    return _get(f"/students/{student_id}/tracks")


def get_track(track_id: int) -> Dict[str, Any]:
    return _get(f"/tracks/{track_id}")


def create_track(
    student_id: int,
    name: str,
    target_score: int,
    max_score: int,
    exam_mode: str = "MULTI_SUBJECT",
    template: Optional[str] = None,
    custom_subjects: Optional[List[str]] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "name": name,
        "target_score": target_score,
        "max_score": max_score,
        "exam_mode": exam_mode,
    }
    if template:
        payload["template"] = template
    if custom_subjects is not None:
        payload["custom_subjects"] = custom_subjects
    return _post(f"/students/{student_id}/tracks", payload)


def update_track(
    track_id: int,
    target_score: int,
    name: Optional[str] = None,
    max_score: Optional[int] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"target_score": target_score}
    if name:
        payload["name"] = name
    if max_score is not None:
        payload["max_score"] = max_score
    return _put(f"/tracks/{track_id}", payload)


def delete_track(track_id: int) -> None:
    _delete(f"/tracks/{track_id}")


# Test Operations (The Log-a-Test slice)
def get_track_tests(track_id: int) -> List[Dict[str, Any]]:
    return _get(f"/tracks/{track_id}/tests")


def log_test(track_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    return _post(f"/tracks/{track_id}/tests", payload)


# Analytics Operations
def get_track_scorecard(track_id: int) -> Dict[str, Any]:
    return _get(f"/tracks/{track_id}/scorecard")


def get_focus_rankings(track_id: int, available_hours: float = 20.0) -> Dict[str, Any]:
    return _get(f"/tracks/{track_id}/focus-rankings", params={"available_hours": available_hours})


# Study Plans & Focus Sessions
def get_student_plans(student_id: int) -> List[Dict[str, Any]]:
    return _get(f"/students/{student_id}/plans")


def create_study_plan(student_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    return _post(f"/students/{student_id}/plans", payload)


def get_student_adherence(student_id: int) -> Dict[str, Any]:
    return _get(f"/students/{student_id}/adherence")


def get_focus_sessions(student_id: int) -> List[Dict[str, Any]]:
    return _get(f"/students/{student_id}/focus-sessions")


def log_focus_session(student_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    return _post(f"/students/{student_id}/focus-sessions", payload)
