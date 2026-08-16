from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user, require_permission
from models import Patient
from schemas import PatientCreate, PatientResponse
from database import get_db

router = APIRouter(prefix="/patients", tags=["Patients"])


def generate_patient_id(db: Session) -> str:
    count = db.query(Patient).count()
    return f"PT-{str(count + 1).zfill(4)}"


@router.post(
    "/",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission("patient:create")],
)
def create_patient(
    payload: PatientCreate,
    db: Session = Depends(get_db),
):
    patient = Patient(
        patient_id     = generate_patient_id(db),
        first_name     = payload.firstName,
        last_name      = payload.lastName,
        dob            = payload.dob,
        gender         = payload.gender,
        admission_date = payload.admissionDate,
        diagnosis      = payload.diagnosis,
        doctor         = payload.doctor,
        department     = payload.department,
        patient_type   = payload.patientType,
        status         = payload.status,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/", response_model=list[PatientResponse])
def get_patients(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return db.query(Patient).order_by(Patient.created_at.desc()).all()


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: str,
    payload: PatientCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    patient.first_name     = payload.firstName
    patient.last_name      = payload.lastName
    patient.dob            = payload.dob
    patient.gender         = payload.gender
    patient.admission_date = payload.admissionDate
    patient.diagnosis      = payload.diagnosis
    patient.doctor         = payload.doctor
    patient.department     = payload.department
    patient.patient_type   = payload.patientType
    patient.status         = payload.status

    db.commit()
    db.refresh(patient)
    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    dependencies=[require_permission("patient:delete")],
):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    db.delete(patient)
    db.commit()