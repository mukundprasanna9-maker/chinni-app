"""API Client for Cadence UI.

Teaching rule:
This is the ONLY file in the UI layer that makes HTTP calls.
No screen or widget directly touches network or SQL.
"""

import os
import requests
from typing import List, Dict, Any, Optional

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


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


def check_backend_health() -> bool:
    try:
        data = _get("/health")
        return data.get("status") == "healthy"
    except Exception:
        return False


# Student Operations
def get_students() -> List[Dict[str, Any]]:
    return _get("/students")


def get_student(student_id: int) -> Dict[str, Any]:
    return _get(f"/students/{student_id}")


def create_student(name: str, target_score: int = 235) -> Dict[str, Any]:
    return _post("/students", {"name": name, "target_score": target_score})


# Track Operations
def get_student_tracks(student_id: int) -> List[Dict[str, Any]]:
    return _get(f"/students/{student_id}/tracks")


def get_track(track_id: int) -> Dict[str, Any]:
    return _get(f"/tracks/{track_id}")


def create_track(student_id: int, name: str, target_score: int, max_score: int) -> Dict[str, Any]:
    return _post(
        f"/students/{student_id}/tracks",
        {"name": name, "target_score": target_score, "max_score": max_score},
    )


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
