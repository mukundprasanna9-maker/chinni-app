from fastapi import APIRouter, HTTPException, status
from typing import List
from backend.schemas.track import (
    TrackCreate,
    TrackResponse,
    SubjectCreate,
    SubjectResponse,
    GroupCreate,
    GroupResponse,
)
from backend.repositories.student_repo import get_student_by_id
from backend.repositories.track_repo import (
    create_track,
    get_track_by_id,
    get_tracks_by_student,
    create_subject,
    get_subjects_by_track,
    get_subject_by_id,
    create_group,
    get_groups_by_subject,
)

router = APIRouter(tags=["Tracks & Subjects"])


def _hydrate_track(track: dict) -> dict:
    subjects = get_subjects_by_track(track["id"])
    for s in subjects:
        s["groups"] = get_groups_by_subject(s["id"])
    track["subjects"] = subjects
    return track


@router.get("/students/{student_id}/tracks", response_model=List[TrackResponse])
def list_tracks_for_student(student_id: int):
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    tracks = get_tracks_by_student(student_id)
    return [_hydrate_track(t) for t in tracks]


@router.post("/students/{student_id}/tracks", response_model=TrackResponse, status_code=status.HTTP_201_CREATED)
def add_track_for_student(student_id: int, payload: TrackCreate):
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    track = create_track(student_id, payload.name, payload.target_score, payload.max_score)
    return _hydrate_track(track)


@router.get("/tracks/{track_id}", response_model=TrackResponse)
def fetch_track(track_id: int):
    track = get_track_by_id(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return _hydrate_track(track)


@router.post("/tracks/{track_id}/subjects", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def add_subject(track_id: int, payload: SubjectCreate):
    track = get_track_by_id(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    sub = create_subject(track_id, payload.name, payload.code, payload.max_marks, payload.target_marks)
    sub["groups"] = []
    return sub


@router.post("/subjects/{subject_id}/groups", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def add_group(subject_id: int, payload: GroupCreate):
    sub = get_subject_by_id(subject_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subject not found")
    return create_group(
        subject_id=subject_id,
        group_code=payload.group_code,
        name=payload.name,
        description=payload.description or "",
        weight_percentage=payload.weight_percentage or 33.3,
    )
