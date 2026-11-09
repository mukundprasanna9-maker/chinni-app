from fastapi import APIRouter, HTTPException, status
from typing import List
from backend.schemas.plan import (
    StudyPlanCreate,
    StudyPlanUpdate,
    StudyPlanResponse,
    FocusSessionCreate,
    FocusSessionResponse,
)
from backend.repositories.student_repo import get_student_by_id
from backend.repositories.plan_repo import (
    create_study_plan,
    get_study_plans,
    get_study_plan_by_id,
    update_plan_actual_hours,
    create_focus_session,
    get_focus_sessions,
)

router = APIRouter(tags=["Study Plans & Focus Sessions"])


@router.get("/students/{student_id}/plans", response_model=List[StudyPlanResponse])
def list_plans_for_student(student_id: int):
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return get_study_plans(student_id)


@router.post("/students/{student_id}/plans", response_model=StudyPlanResponse, status_code=status.HTTP_201_CREATED)
def add_plan(student_id: int, payload: StudyPlanCreate):
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return create_study_plan(
        student_id=student_id,
        group_id=payload.group_id,
        subject_id=payload.subject_id,
        target_date=payload.target_date,
        planned_hours=payload.planned_hours,
        notes=payload.notes or "",
    )


@router.put("/plans/{plan_id}", response_model=StudyPlanResponse)
def update_plan(plan_id: int, payload: StudyPlanUpdate):
    plan = update_plan_actual_hours(plan_id, payload.actual_hours, payload.status or "COMPLETED")
    if not plan:
        raise HTTPException(status_code=404, detail="Study plan not found")
    return plan


@router.get("/students/{student_id}/focus-sessions", response_model=List[FocusSessionResponse])
def list_focus_sessions(student_id: int):
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return get_focus_sessions(student_id)


@router.post("/students/{student_id}/focus-sessions", response_model=FocusSessionResponse, status_code=status.HTTP_201_CREATED)
def add_focus_session(student_id: int, payload: FocusSessionCreate):
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return create_focus_session(
        student_id=student_id,
        subject_id=payload.subject_id,
        group_id=payload.group_id,
        duration_minutes=payload.duration_minutes,
        notes=payload.notes or "",
        adherence_status=payload.adherence_status or "COMPLETED",
    )
