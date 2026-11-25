from fastapi import APIRouter, HTTPException, status
from typing import List
from backend.schemas.track import (
    TrackCreate,
    TrackUpdate,
    TrackResponse,
    SubjectCreate,
    SubjectResponse,
    GroupCreate,
    GroupResponse,
    ChapterCreate,
    ChapterResponse,
)
from backend.repositories.student_repo import get_student_by_id
from backend.repositories.track_repo import (
    create_track,
    get_track_by_id,
    get_tracks_by_student,
    update_track,
    delete_track,
    create_subject,
    get_subjects_by_track,
    get_subject_by_id,
    create_group,
    get_groups_by_subject,
    create_chapter,
    get_chapters_by_subject,
)
from backend.seed.seed_data import create_track_from_template

router = APIRouter(tags=["Tracks & Subjects"])


def _hydrate_track(track: dict) -> dict:
    subjects = get_subjects_by_track(track["id"])
    for s in subjects:
        s["groups"] = get_groups_by_subject(s["id"])
        s["chapters"] = get_chapters_by_subject(s["id"])
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
    if payload.template or payload.custom_subjects is not None:
        bundle = create_track_from_template(
            student_id=student_id,
            template=payload.template or "Custom",
            name=payload.name,
            target_score=payload.target_score,
            max_score=payload.max_score,
            exam_mode=payload.exam_mode,
            custom_subjects=payload.custom_subjects,
        )
        return _hydrate_track(bundle["track"])
    track = create_track(
        student_id,
        payload.name,
        payload.target_score,
        payload.max_score,
        exam_mode=payload.exam_mode or "MULTI_SUBJECT",
    )
    return _hydrate_track(track)


@router.get("/tracks/{track_id}", response_model=TrackResponse)
def fetch_track(track_id: int):
    track = get_track_by_id(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return _hydrate_track(track)


@router.put("/tracks/{track_id}", response_model=TrackResponse)
def modify_track(track_id: int, payload: TrackUpdate):
    updated = update_track(
        track_id,
        target_score=payload.target_score,
        name=payload.name,
        max_score=payload.max_score,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Track not found")
    return _hydrate_track(updated)


@router.delete("/tracks/{track_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_track(track_id: int):
    success = delete_track(track_id)
    if not success:
        raise HTTPException(status_code=404, detail="Track not found")


@router.post("/tracks/{track_id}/subjects", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def add_subject(track_id: int, payload: SubjectCreate):
    track = get_track_by_id(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    sub = create_subject(track_id, payload.name, payload.code, payload.max_marks, payload.target_marks)
    sub["groups"] = []
    sub["chapters"] = []
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


@router.post("/subjects/{subject_id}/chapters", response_model=ChapterResponse, status_code=status.HTTP_201_CREATED)
def add_chapter(subject_id: int, payload: ChapterCreate):
    sub = get_subject_by_id(subject_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subject not found")
    return create_chapter(
        subject_id=subject_id,
        chapter_code=payload.chapter_code,
        name=payload.name,
        topics=payload.topics or "",
        unit=payload.unit or "",
    )
