from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class GroupCreate(BaseModel):
    group_code: str = Field(..., max_length=20, description="Group identifier, e.g. G1, G2, G3")
    name: str = Field(..., max_length=150, description="Group topic or domain name")
    description: Optional[str] = ""
    weight_percentage: Optional[float] = 33.3


class GroupResponse(BaseModel):
    id: int
    subject_id: int
    group_code: str
    name: str
    description: Optional[str] = ""
    weight_percentage: Optional[float] = 0.0


class SubjectCreate(BaseModel):
    name: str = Field(..., max_length=100, description="Subject name, e.g. Mathematics, Physics, Chemistry")
    code: str = Field(..., max_length=20, description="Subject short code, e.g. MATH, PHY, CHEM")
    max_marks: int = Field(100, gt=0)
    target_marks: Optional[int] = 0


class SubjectResponse(BaseModel):
    id: int
    track_id: int
    name: str
    code: str
    max_marks: int
    target_marks: int
    groups: Optional[List[GroupResponse]] = []


class TrackCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Track name, e.g. JEE Main 2026")
    target_score: int = Field(..., gt=0)
    max_score: int = Field(..., gt=0)


class TrackResponse(BaseModel):
    id: int
    student_id: int
    name: str
    target_score: int
    max_score: int
    created_at: Optional[datetime] = None
    subjects: Optional[List[SubjectResponse]] = []
