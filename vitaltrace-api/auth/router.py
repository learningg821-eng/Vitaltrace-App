from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from auth.models import User
from auth.schemas import LoginRequest, TokenResponse
from auth.jwt import create_token
from auth.dependencies import get_current_user
from database import get_db


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

pwd_ctx = CryptContext(schemes=["bcrypt"])


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.username == payload.username)
        .first()
    )

    if not user or not pwd_ctx.verify(
        payload.password,
        user.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    return TokenResponse(
        access_token=create_token(
            user.id,
            user.role.name,
        )
    )


@router.get("/me")
def me(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role.name,
        "permissions": [
            p.action
            for p in current_user.role.permissions
        ],
    }