from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from auth.models import User
from auth.dependencies import get_current_user
from models import Patient, Staff, Vital, Alert
from database import get_db

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total_patients = db.query(Patient).count()
    total_staff = db.query(Staff).count()

    # Latest vital per patient
    latest_vitals_subq = (
        db.query(func.max(Vital.id).label("id"))
        .group_by(Vital.patient_id)
        .subquery()
    )

    latest_vitals = (
        db.query(Vital)
        .join(latest_vitals_subq, Vital.id == latest_vitals_subq.c.id)
        .all()
    )

    critical_today = sum(1 for v in latest_vitals if v.ai_status == "critical")
    warning_today = sum(1 for v in latest_vitals if v.ai_status == "warning")
    normal_today = sum(1 for v in latest_vitals if v.ai_status == "normal")

    recent_vitals = (
        db.query(Vital)
        .order_by(Vital.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "total_patients": total_patients,
        "total_staff": total_staff,
        "critical_count": critical_today,
        "warning_count": warning_today,
        "normal_count": normal_today,
        "recent_vitals": [
            {
                "id": v.id,
                "patient_id": v.patient_id,
                "heart_rate": v.heart_rate,
                "spo2": v.spo2,
                "temperature": v.temperature,
                "ai_status": v.ai_status,
                "created_at": v.created_at.isoformat(),
            }
            for v in recent_vitals
        ],
    }