from fastapi import APIRouter, HTTPException, status
from typing import List
from backend.schemas.test_result import TestCreate, TestResponse
from backend.repositories.track_repo import get_track_by_id
from backend.repositories.test_repo import (
    create_test,
    get_test_by_id,
    get_tests_by_track,
    delete_test,
)

router = APIRouter(tags=["Tests"])


@router.get("/tracks/{track_id}/tests", response_model=List[TestResponse])
def list_tests_for_track(track_id: int):
    track = get_track_by_id(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    tests = get_tests_by_track(track_id)
    # Populate full details
    return [get_test_by_id(t["id"]) for t in tests]


@router.post("/tracks/{track_id}/tests", response_model=TestResponse, status_code=status.HTTP_201_CREATED)
def log_test(track_id: int, payload: TestCreate):
    track = get_track_by_id(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    subject_payloads = [s.model_dump() for s in payload.subject_scores]
    group_payloads = [g.model_dump() for g in payload.group_scores]

    test_record = create_test(
        track_id=track_id,
        test_code=payload.test_code,
        test_date=payload.test_date,
        total_score=payload.total_score,
        max_score=payload.max_score,
        notes=payload.notes or "",
        subject_scores=subject_payloads,
        group_scores=group_payloads,
    )
    return test_record


@router.get("/tests/{test_id}", response_model=TestResponse)
def fetch_test(test_id: int):
    test_record = get_test_by_id(test_id)
    if not test_record:
        raise HTTPException(status_code=404, detail="Test not found")
    return test_record


@router.delete("/tests/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_test(test_id: int):
    success = delete_test(test_id)
    if not success:
        raise HTTPException(status_code=404, detail="Test not found")
