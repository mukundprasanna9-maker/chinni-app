from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from backend.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from backend.repositories.student_repo import (
    create_student,
    get_student_by_id,
    get_all_students,
    update_student,
    delete_student,
)

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("", response_model=List[StudentResponse])
def list_students(user_id: Optional[int] = Query(None, description="Filter by user_id. Omit to list all (admin).")):
    return get_all_students(user_id=user_id)


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def add_student(payload: StudentCreate, user_id: Optional[int] = Query(None)):
    return create_student(payload.name, payload.target_score, user_id=user_id)


@router.get("/{student_id}", response_model=StudentResponse)
def fetch_student(student_id: int):
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
    return student


@router.put("/{student_id}", response_model=StudentResponse)
def modify_student(student_id: int, payload: StudentUpdate):
    student = update_student(student_id, payload.name, payload.target_score)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
    return student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_student(student_id: int):
    success = delete_student(student_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
