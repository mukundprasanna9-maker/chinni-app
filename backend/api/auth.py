"""Authentication API routes for Cadence."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from backend.repositories.user_repo import authenticate_user, create_user
from backend.repositories.student_repo import create_student
from backend.seed.seed_data import create_default_jee_track

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1)


class SignupRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=4)


class UserResponse(BaseModel):
    id: int
    username: str
    is_admin: bool


@router.post("/login", response_model=UserResponse)
def login(payload: LoginRequest):
    user = authenticate_user(payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    return user


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest):
    user = create_user(payload.username, payload.password, is_admin=False)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{payload.username}' is already taken",
        )
    # Create an initial student profile and default track for the new user
    student = create_student(name=payload.username, target_score=235, user_id=user["id"])
    create_default_jee_track(student["id"], target_score=235)
    return user
