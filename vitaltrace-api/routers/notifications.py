from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from auth.models import User, FCMDeviceToken
from auth.dependencies import get_current_user


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


class FCMTokenRequest(BaseModel):
    fcm_token: str


@router.post("/register")
def register_fcm_token(
    payload: FCMTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing_token = (
        db.query(FCMDeviceToken)
        .filter(FCMDeviceToken.token == payload.fcm_token)
        .first()
    )

    if existing_token:
        # Token already belongs to this user
        if existing_token.user_id != current_user.id:
            existing_token.user_id = current_user.id
            db.commit()

        return {
            "message": "FCM token already registered",
        }

    device_token = FCMDeviceToken(
        user_id=current_user.id,
        token=payload.fcm_token,
    )

    db.add(device_token)
    db.commit()
    db.refresh(device_token)

    return {
        "message": "FCM token registered successfully",
        "id": device_token.id,
    }