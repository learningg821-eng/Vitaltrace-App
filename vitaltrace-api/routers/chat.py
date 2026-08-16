import os
import re
import json
import hashlib
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from groq import Groq

from auth.models import User
from auth.dependencies import get_current_user
from models import Vital, Patient, Staff
from database import get_db
from blockchain import record_vital_on_chain

router = APIRouter(prefix="/chat", tags=["Chat"])


def get_groq_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


def is_update_question(message: str) -> bool:
    keywords = ["update", "change", "set", "modify"]
    message_lower = message.lower()
    return any(k in message_lower for k in keywords)


def is_staff_question(message: str) -> bool:
    keywords = ["staff", "nurse", "doctor", "duty", "shift", "employee", "worker"]
    message_lower = message.lower()
    return any(k in message_lower for k in keywords)


def search_patients(db: Session, message: str):
    patients = db.query(Patient).all()
    message_lower = message.lower()
    words = message_lower.split()

    matched = []
    for patient in patients:
        first = patient.first_name.lower()
        last = patient.last_name.lower()
        full_name = f"{first} {last}"
        pid = str(patient.id)
        patient_id = patient.patient_id.lower()

        if (
            full_name in message_lower or
            patient_id in message_lower or
            pid in words or
            any(w == first or w == last or w in first or w in last for w in words)
        ):
            matched.append(patient)

    return matched


def search_staff(db: Session, message: str):
    staff_list = db.query(Staff).all()
    message_lower = message.lower()

    name_matched = []
    for staff in staff_list:
        full_name = f"{staff.first_name} {staff.last_name}".lower()
        if (
            staff.first_name.lower() in message_lower or
            staff.last_name.lower() in message_lower or
            full_name in message_lower or
            staff.staff_id.lower() in message_lower
        ):
            name_matched.append(staff)

    if name_matched:
        return name_matched

    dept_matched = []
    for staff in staff_list:
        if staff.department.lower() in message_lower:
            dept_matched.append(staff)

    return dept_matched


def parse_update_intent(message: str) -> dict:
    field_map = {
        "heart rate": "heart_rate",
        "hr": "heart_rate",
        "bp": "systolic_bp",
        "blood pressure": "systolic_bp",
        "spo2": "spo2",
        "oxygen": "spo2",
        "temperature": "temperature",
        "temp": "temperature",
        "respiratory rate": "respiratory_rate",
        "rr": "respiratory_rate",
    }

    message_lower = message.lower()
    detected_field = None
    detected_value = None

    for key, field in field_map.items():
        if key in message_lower:
            detected_field = field
            break

    match = re.search(r'\bto\s*(\d+\.?\d*)\b', message_lower)
    if match:
        detected_value = float(match.group(1))

    return {
        "field": detected_field,
        "value": detected_value,
    }


def generate_blockchain_hash(vital_id, patient_id, data, previous_hash=""):
    payload = (
        f"{vital_id}"
        f"{patient_id}"
        f"{json.dumps(data, sort_keys=True)}"
        f"{previous_hash}"
        f"{datetime.utcnow().isoformat()}"
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def build_patient_context(db: Session, patients: list) -> str:
    if not patients:
        return "No matching patients found in the database."

    context = ""
    for patient in patients:
        all_vitals = (
            db.query(Vital)
            .filter(Vital.patient_id == patient.id)
            .order_by(Vital.id.asc())
            .all()
        )

        context += f"Patient: {patient.first_name} {patient.last_name}\n"
        context += f"  ID: {patient.id}\n"
        context += f"  Patient ID: {patient.patient_id}\n"
        context += f"  Diagnosis: {patient.diagnosis}\n"
        context += f"  Department: {patient.department}\n"
        context += f"  Status: {patient.status}\n"

        if all_vitals:
            context += f"  Vital History ({len(all_vitals)} records):\n"
            for i, v in enumerate(all_vitals):
                context += f"    Record {i+1} ({v.created_at}):\n"
                context += f"      Heart Rate: {v.heart_rate} BPM\n"
                context += f"      BP: {v.systolic_bp}/{v.diastolic_bp} mmHg\n"
                context += f"      SpO2: {v.spo2}%\n"
                context += f"      Temperature: {v.temperature}C\n"
                context += f"      Respiratory Rate: {v.respiratory_rate} breaths/min\n"
                context += f"      AI Status: {v.ai_status}\n"
                context += f"      AI Notes: {v.ai_notes}\n"
        else:
            context += f"  Vital History: No vitals recorded\n"

        context += "\n"

    return context


def build_staff_context(staff_list: list) -> str:
    if not staff_list:
        return "No matching staff found in the database."

    context = ""
    for staff in staff_list:
        context += f"Staff: {staff.first_name} {staff.last_name}\n"
        context += f"  Staff ID: {staff.staff_id}\n"
        context += f"  Department: {staff.department}\n"
        context += f"  Shift: {staff.shift}\n"
        context += f"  Phone: {staff.phone}\n"
        context += f"  Status: {staff.status}\n\n"

    return context


def build_general_context(db: Session) -> str:
    patients = db.query(Patient).all()
    total = len(patients)

    critical = (
        db.query(Vital)
        .filter(Vital.ai_status == "critical")
        .count()
    )

    warning = (
        db.query(Vital)
        .filter(Vital.ai_status == "warning")
        .count()
    )

    departments = list(set([p.department for p in patients]))

    context = f"Hospital Summary:\n"
    context += f"  Total Patients: {total}\n"
    context += f"  Critical Vitals Recorded: {critical}\n"
    context += f"  Warning Vitals Recorded: {warning}\n"
    context += f"  Departments: {', '.join(departments)}\n\n"

    return context


@router.post("/")
def chat(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    message = payload.get("message", "")

    if not message:
        return {"reply": "Please ask a question."}

    # Handle greeting
    greetings = ["hi", "hello", "hey", "hii", "helo"]
    if message.lower().strip() in greetings:
        return {"reply": "Hello! I am VitalTrace AI. Ask me about patients, vitals, staff, or alerts."}

    # Handle update intent
    if is_update_question(message):
        matched_patients = search_patients(db, message)

        if not matched_patients:
            return {"reply": "No matching patient found. Please mention the patient name."}

        if len(matched_patients) > 1:
            names = [
                f"{i+1}. {p.first_name} {p.last_name} (ID: {p.id})"
                for i, p in enumerate(matched_patients)
            ]
            return {
                "reply": "Multiple patients found:\n" + "\n".join(names) + "\n\nWhich one do you mean?"
            }

        patient = matched_patients[0]
        intent = parse_update_intent(message)

        if not intent["field"]:
            return {"reply": "Please mention which vital to update. Example: Update John's BP to 130"}

        if not intent["value"]:
            return {"reply": "Please mention the new value. Example: Update John's BP to 130"}

        latest_vital = (
            db.query(Vital)
            .filter(Vital.patient_id == patient.id)
            .order_by(Vital.id.desc())
            .first()
        )

        if not latest_vital:
            return {"reply": f"No vitals found for {patient.first_name} {patient.last_name}."}

        # Create new vital record
        new_vital = Vital(
            patient_id=patient.id,
            heart_rate=latest_vital.heart_rate,
            systolic_bp=latest_vital.systolic_bp,
            diastolic_bp=latest_vital.diastolic_bp,
            spo2=latest_vital.spo2,
            temperature=latest_vital.temperature,
            respiratory_rate=latest_vital.respiratory_rate,
            ai_status=latest_vital.ai_status,
            ai_notes=latest_vital.ai_notes,
        )

        setattr(new_vital, intent["field"], intent["value"])

        db.add(new_vital)
        db.commit()
        db.refresh(new_vital)

        vital_data = {
            "heart_rate": new_vital.heart_rate,
            "systolic_bp": new_vital.systolic_bp,
            "diastolic_bp": new_vital.diastolic_bp,
            "spo2": new_vital.spo2,
            "temperature": new_vital.temperature,
            "respiratory_rate": new_vital.respiratory_rate,
        }

        new_vital.blockchain_hash = generate_blockchain_hash(
            new_vital.id,
            patient.id,
            vital_data,
            latest_vital.blockchain_hash if latest_vital else "",
        )

        db.commit()
        db.refresh(new_vital)

        tx_hash, block_number = record_vital_on_chain(
            new_vital.id,
            patient.id,
            new_vital.blockchain_hash
        )

        if tx_hash:
            new_vital.tx_hash = tx_hash
            new_vital.block_number = block_number
            db.commit()

        return {
            "reply": (
                f"New vital record created for {patient.first_name} {patient.last_name}. "
                f"{intent['field'].replace('_', ' ')} set to {intent['value']}. "
                f"Blockchain recorded. TX: {tx_hash[:16] if tx_hash else 'N/A'}..."
            )
        }

    # Handle staff question
    if is_staff_question(message):
        matched_staff = search_staff(db, message)
        if matched_staff:
            context = build_staff_context(matched_staff)
        else:
            all_staff = db.query(Staff).all()
            context = build_staff_context(all_staff)
    else:
        matched_patients = search_patients(db, message)

        if matched_patients:
            if len(matched_patients) > 1:
                names = [
                    f"{i+1}. {p.first_name} {p.last_name} (ID: {p.id})"
                    for i, p in enumerate(matched_patients)
                ]
                return {
                    "reply": "Multiple patients found:\n" + "\n".join(names) + "\n\nWhich one do you mean?"
                }
            context = build_patient_context(db, matched_patients)
        else:
            context = build_general_context(db)

    client = get_groq_client()

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a hospital assistant AI. "
                    "Answer questions based only on the provided data. "
                    "Be concise and use plain simple sentences. "
                    "No markdown, no bullet symbols, no extra formatting. "
                    "If information is not available, say so clearly.\n\n"
                    + context
                )
            },
            {
                "role": "user",
                "content": message
            }
        ],
        temperature=0.3,
    )

    reply = response.choices[0].message.content.strip()

    return {"reply": reply}