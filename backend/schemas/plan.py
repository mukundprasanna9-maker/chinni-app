from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StudyPlanCreate(BaseModel):
    group_id: Optional[int] = None
    subject_id: Optional[int] = None
    target_date: str = Field(..., description="Target date in YYYY-MM-DD")
    planned_hours: float = Field(..., gt=0)
    notes: Optional[str] = ""


class StudyPlanUpdate(BaseModel):
    actual_hours: float = Field(..., ge=0)
    status: Optional[str] = "COMPLETED"


class StudyPlanResponse(BaseModel):
    id: int
    student_id: int
    group_id: Optional[int] = None
    subject_id: Optional[int] = None
    target_date: str
    planned_hours: float
    actual_hours: float
    notes: Optional[str] = ""
    status: str
    created_at: Optional[datetime] = None
    subject_name: Optional[str] = None
    group_name: Optional[str] = None
    group_code: Optional[str] = None


class FocusSessionCreate(BaseModel):
    subject_id: Optional[int] = None
    group_id: Optional[int] = None
    duration_minutes: int = Field(..., gt=0)
    notes: Optional[str] = ""
    adherence_status: Optional[str] = "COMPLETED"


class FocusSessionResponse(BaseModel):
    id: int
    student_id: int
    subject_id: Optional[int] = None
    group_id: Optional[int] = None
    duration_minutes: int
    adherence_status: str
    notes: Optional[str] = ""
    completed_at: Optional[datetime] = None
    subject_name: Optional[str] = None
    group_name: Optional[str] = None
    group_code: Optional[str] = None
