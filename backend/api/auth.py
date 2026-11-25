"""Authentication API routes for Cadence."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from backend.repositories.user_repo import authenticate_user, create_user, update_user_credentials
from backend.repositories.student_repo import create_student
from backend.seed.seed_data import create_track_from_template

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1)


class SignupRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=4)
    track_template: Optional[str] = "JEE Main 2026"


class AccountUpdateRequest(BaseModel):
    user_id: int
    current_password: str = Field(..., min_length=1)
    new_username: Optional[str] = Field(None, min_length=1, max_length=100)
    new_password: Optional[str] = Field(None, min_length=4)


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
    # Create an initial student profile and chosen starting track for the new user
    tpl = payload.track_template or "JEE Main 2026"
    default_target = 85 if ("8" in tpl) else 235
    student = create_student(name=payload.username, target_score=default_target, user_id=user["id"])
    create_track_from_template(student["id"], template=tpl)
    return user


@router.put("/account", response_model=UserResponse)
def update_account(payload: AccountUpdateRequest):
    if not payload.new_username and not payload.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide a new username or a new password to update.",
        )
    updated, err = update_user_credentials(
        user_id=payload.user_id,
        current_password=payload.current_password,
        new_username=payload.new_username,
        new_password=payload.new_password,
    )
    if err == "NOT_FOUND":
        raise HTTPException(status_code=404, detail="User not found")
    if err == "INVALID_PASSWORD":
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    if err == "USERNAME_TAKEN":
        raise HTTPException(status_code=409, detail="That username is already taken")
    return updated
