from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SubjectScoreInput(BaseModel):
    subject_id: int
    score: float = Field(..., ge=0)
    max_score: float = Field(100.0, gt=0)
    accuracy_percent: Optional[float] = 0.0
    time_spent_minutes: Optional[int] = 0


class GroupScoreInput(BaseModel):
    group_id: int
    score: float = Field(..., ge=0)
    max_score: float = Field(33.3, gt=0)


class TestCreate(BaseModel):
    test_code: str = Field(..., max_length=50, description="Test identifier, e.g. T1, T2, Mock Test 1")
    test_date: str = Field(..., description="Date of test in YYYY-MM-DD")
    total_score: float = Field(..., ge=0)
    max_score: float = Field(300.0, gt=0)
    notes: Optional[str] = ""
    subject_scores: List[SubjectScoreInput] = []
    group_scores: List[GroupScoreInput] = []


class SubjectScoreResponse(BaseModel):
    id: Optional[int] = None
    subject_id: int
    subject_name: Optional[str] = ""
    subject_code: Optional[str] = ""
    score: float
    max_score: float
    accuracy_percent: Optional[float] = 0.0
    time_spent_minutes: Optional[int] = 0


class GroupScoreResponse(BaseModel):
    id: Optional[int] = None
    group_id: int
    group_code: Optional[str] = ""
    group_name: Optional[str] = ""
    subject_name: Optional[str] = ""
    subject_code: Optional[str] = ""
    score: float
    max_score: float


class TestResponse(BaseModel):
    id: int
    track_id: int
    test_code: str
    test_type: Optional[str] = "FULL"
    test_date: str
    total_score: float
    max_score: float
    notes: Optional[str] = ""
    created_at: Optional[datetime] = None
    subject_scores: Optional[List[SubjectScoreResponse]] = []
    group_scores: Optional[List[GroupScoreResponse]] = []
