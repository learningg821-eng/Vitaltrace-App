import os
import json
import hashlib
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from groq import Groq

from auth.models import User, FCMDeviceToken
from auth.dependencies import get_current_user
from models import Vital, Patient, Staff
from schemas import VitalCreate, VitalResponse
from database import get_db
from firebase.firebase_admin import send_fcm_notification
from blockchain import record_vital_on_chain


router = APIRouter(prefix="/vitals", tags=["Vitals"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def get_groq_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_vitals_with_ai(patient: Patient, vital: dict) -> dict:
    client = get_groq_client()

    prompt = f"""
You are a medical AI assistant. Analyze the following patient vitals and return a JSON response.

Patient Info:
- Name: {patient.first_name} {patient.last_name}
- Diagnosis: {patient.diagnosis}
- Department: {patient.department}

Current Vitals:
- Heart Rate: {vital['heart_rate']} BPM
- Blood Pressure: {vital['systolic_bp']}/{vital['diastolic_bp']} mmHg
- SpO2: {vital['spo2']}%
- Temperature: {vital['temperature']}°C
- Respiratory Rate: {vital['respiratory_rate']} breaths/min

Respond ONLY with this JSON format, no extra text:
{{
  "status": "normal" | "warning" | "critical",
  "notes": "brief explanation"
}}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
    )

    text = response.choices[0].message.content.strip()

    return json.loads(text)


def generate_blockchain_hash(
    vital_id: int,
    patient_id: int,
    data: dict,
    previous_hash: str = ""
) -> str:

    payload = (
        f"{vital_id}"
        f"{patient_id}"
        f"{json.dumps(data, sort_keys=True)}"
        f"{previous_hash}"
        f"{datetime.utcnow().isoformat()}"
    )

    return hashlib.sha256(payload.encode()).hexdigest()


@router.post(
    "/",
    response_model=VitalResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_vital(
    payload: VitalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    patient = (
        db.query(Patient)
        .filter(Patient.id == payload.patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    try:
        ai_result = analyze_vitals_with_ai(
            patient,
            payload.model_dump()
        )

        ai_status = (
            ai_result
            .get("status", "normal")
            .lower()
            .strip()
        )

        ai_notes = ai_result.get("notes", "")

        print("🤖 AI STATUS:", ai_status)
        print("📝 AI NOTES:", ai_notes)

    except Exception as e:
        print(f"❌ AI analysis failed: {e}")

        ai_status = "normal"
        ai_notes = "AI analysis unavailable"

    vital = Vital(
        patient_id=payload.patient_id,
        heart_rate=payload.heart_rate,
        systolic_bp=payload.systolic_bp,
        diastolic_bp=payload.diastolic_bp,
        spo2=payload.spo2,
        temperature=payload.temperature,
        respiratory_rate=payload.respiratory_rate,
        ai_status=ai_status,
        ai_notes=ai_notes,
    )

    db.add(vital)
    db.commit()
    db.refresh(vital)

    previous = (
        db.query(Vital)
        .filter(
            Vital.patient_id == payload.patient_id,
            Vital.id != vital.id
        )
        .order_by(Vital.id.desc())
        .first()
    )

    vital.blockchain_hash = generate_blockchain_hash(
        vital.id,
        payload.patient_id,
        payload.model_dump(),
        previous.blockchain_hash if previous else "",
    )

    db.commit()
    db.refresh(vital)

    # Record on blockchain
    tx_hash, block_number = record_vital_on_chain(
        vital.id,
        payload.patient_id,
        vital.blockchain_hash
    )

    if tx_hash:
        vital.tx_hash = tx_hash
        vital.block_number = block_number
        db.commit()
        db.refresh(vital)

    if ai_status in ("critical", "warning"):

        print("🚨 ALERT TRIGGERED:", ai_status)

        staff = (
            db.query(Staff)
            .filter(Staff.department == patient.department)
            .all()
        )

        print("👨‍⚕️ STAFF FOUND:", len(staff))

        user_ids = [
            s.user_id
            for s in staff
            if s.user_id
        ]

        print("👤 USER IDS:", user_ids)

        for user_id in user_ids:

            fcm_tokens = (
                db.query(FCMDeviceToken)
                .filter(
                    FCMDeviceToken.user_id == user_id
                )
                .all()
            )

            print(
                f"📱 FCM TOKENS FOR USER {user_id}:",
                len(fcm_tokens)
            )

            for device in fcm_tokens:

                print("🚨 SENDING FCM...")

                try:

                    response = send_fcm_notification(
                        fcm_token=device.token,
                        title=(
                            f"🚨 {ai_status.upper()} - "
                            f"{patient.first_name} "
                            f"{patient.last_name}"
                        ),
                        body=ai_notes,
                        data={
                            "patient_id": str(patient.id),
                            "vital_id": str(vital.id),
                            "ai_status": ai_status,
                        },
                    )

                    print("✅ FCM SENT:", response)

                except Exception as e:

                    print(
                        "❌ FCM FAILED:",
                        repr(e)
                    )

    return vital


@router.get(
    "/{patient_id}",
    response_model=list[VitalResponse]
)
def get_patient_vitals(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return (
        db.query(Vital)
        .filter(Vital.patient_id == patient_id)
        .order_by(Vital.created_at.desc())
        .all()
    )