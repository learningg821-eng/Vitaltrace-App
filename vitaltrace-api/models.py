from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from database import Base


class Staff(Base):
    __tablename__ = "staff"

    id         = Column(Integer, primary_key=True, index=True)
    staff_id   = Column(String, unique=True, index=True)
    first_name = Column(String, nullable=False)
    last_name  = Column(String, nullable=False)
    department = Column(String, nullable=False)
    shift      = Column(String)
    phone      = Column(String)
    status     = Column(String, nullable=False)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=True)


class Alert(Base):
    __tablename__ = "alerts"

    id           = Column(Integer, primary_key=True, index=True)
    message      = Column(String, nullable=False)
    staff_id     = Column(Integer, ForeignKey("users.id"), nullable=False)   # receiver
    triggered_by = Column(Integer, ForeignKey("users.id"), nullable=False)   # sender
    is_read      = Column(Boolean, default=False)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

class Patient(Base):
    __tablename__ = "patients"

    id               = Column(Integer, primary_key=True, index=True)
    patient_id       = Column(String, unique=True, index=True)
    first_name       = Column(String, nullable=False)
    last_name        = Column(String, nullable=False)
    dob              = Column(String, nullable=False)
    gender           = Column(String, nullable=False)
    admission_date   = Column(String, nullable=False)
    diagnosis        = Column(String, nullable=False)
    doctor           = Column(String, nullable=False)
    department       = Column(String, nullable=False)
    patient_type     = Column(String, nullable=False, default="inpatient")
    status           = Column(String, nullable=False, default="Active")
    created_at       = Column(DateTime(timezone=True), server_default=func.now())

class Vital(Base):
    __tablename__ = "vitals"

    id                = Column(Integer, primary_key=True, index=True)
    patient_id        = Column(Integer, ForeignKey("patients.id"), nullable=False)
    heart_rate        = Column(Integer, nullable=False)
    systolic_bp       = Column(Integer, nullable=False)
    diastolic_bp      = Column(Integer, nullable=False)
    spo2              = Column(Integer, nullable=False)
    temperature       = Column(Float, nullable=False)
    respiratory_rate  = Column(Integer, nullable=False)
    ai_status         = Column(String, nullable=True)   # normal / warning / critical
    ai_notes          = Column(String, nullable=True)
    blockchain_hash   = Column(String, nullable=True)
    tx_hash      = Column(String, nullable=True)
    block_number = Column(Integer, nullable=True)
    created_at        = Column(DateTime(timezone=True), server_default=func.now())