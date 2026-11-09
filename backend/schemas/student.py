from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Student's full name")
    target_score: int = Field(235, ge=0, description="Target score for main track")


class StudentUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    target_score: int = Field(..., ge=0)


class StudentResponse(BaseModel):
    id: int
    name: str
    target_score: int
    created_at: Optional[datetime] = None
