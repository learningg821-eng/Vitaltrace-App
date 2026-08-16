from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.models import User
from auth.dependencies import get_current_user
from models import Vital, Patient
from database import get_db

router = APIRouter(prefix="/ledger", tags=["Ledger"])


@router.get("/")
def get_ledger(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vitals = (
        db.query(Vital)
        .order_by(Vital.id.asc())
        .all()
    )

    ledger = []
    for i, v in enumerate(vitals):
        patient = db.query(Patient).filter(Patient.id == v.patient_id).first()
        ledger.append({
            "block": i + 1,
            "patient_name": f"{patient.first_name} {patient.last_name}" if patient else "Unknown",
            "patient_id": v.patient_id,
            "heart_rate": v.heart_rate,
            "systolic_bp": v.systolic_bp,
            "diastolic_bp": v.diastolic_bp,
            "spo2": v.spo2,
            "temperature": v.temperature,
            "respiratory_rate": v.respiratory_rate,
            "ai_status": v.ai_status,
            "ai_notes": v.ai_notes,
            "tx_hash": v.tx_hash,
            "block_number": v.block_number,
            "blockchain_hash": v.blockchain_hash,
            "previous_hash": vitals[i - 1].blockchain_hash if i > 0 else "0" * 64,
            "created_at": v.created_at.isoformat(),
        })

    return ledger