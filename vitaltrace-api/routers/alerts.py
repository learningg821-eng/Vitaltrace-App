from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.models import User, FCMDeviceToken
from auth.dependencies import require_permission, get_current_user
from models import Alert
from schemas import AlertCreate, AlertResponse
from database import get_db
from firebase.firebase_admin import send_fcm_notification

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.post(
    "/",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission("alert:send")],
)
async def send_alert(
    payload: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    receiver = db.query(User).filter(User.id == payload.staff_id).first()
    if not receiver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff user not found")

    alert = Alert(
        message=payload.message,
        staff_id=payload.staff_id,
        triggered_by=current_user.id,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    fcm_tokens = (
        db.query(FCMDeviceToken)
        .filter(FCMDeviceToken.user_id == payload.staff_id)
        .all()
    )

    for device in fcm_tokens:
        try:
            send_fcm_notification(
                fcm_token=device.token,
                title="🚨 Emergency Alert",
                body=alert.message,
                data={
                    "alert_id": str(alert.id),
                    "staff_id": str(alert.staff_id),
                },
            )
        except Exception as e:
            print(f"FCM failed for token {device.token}: {e}")

    return alert


@router.get("/me", response_model=list[AlertResponse])
def get_my_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Alert)
        .filter(Alert.staff_id == current_user.id, Alert.is_read == False)
        .order_by(Alert.created_at.desc())
        .all()
    )


@router.put("/{alert_id}/dismiss", response_model=AlertResponse)
def dismiss_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id, Alert.staff_id == current_user.id)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    alert.is_read = True
    db.commit()
    db.refresh(alert)
    return alert