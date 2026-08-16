from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class StaffCreate(BaseModel):
    firstName:  str
    lastName:   str
    department: str
    status:     str
    shift:      str | None = None
    phone:      str | None = None
    username:   str
    password:   str
    role_id:    int


class StaffResponse(BaseModel):
    id:         int
    staffId:    str = Field(validation_alias="staff_id")
    firstName:  str = Field(validation_alias="first_name")
    lastName:   str = Field(validation_alias="last_name")
    department: str
    shift:      str | None = None
    phone:      str | None = None
    status:     str
    username:   str | None = None
    role:       str | None = None

    model_config = ConfigDict(from_attributes=True)


class AlertCreate(BaseModel):
    message:  str
    staff_id: int   # user id of the receiver


class AlertResponse(BaseModel):
    id:           int
    message:      str
    staff_id:     int
    triggered_by: int
    is_read:      bool
    created_at:   datetime

    model_config = ConfigDict(from_attributes=True)

class PatientCreate(BaseModel):
    firstName:   str
    lastName:    str
    dob:         str
    gender:      str
    admissionDate: str
    diagnosis:   str
    doctor:      str
    department:  str
    patientType: str = "inpatient"
    status:      str = "Active"


class PatientResponse(BaseModel):
    id:            int
    patientId:     str = Field(validation_alias="patient_id")
    firstName:     str = Field(validation_alias="first_name")
    lastName:      str = Field(validation_alias="last_name")
    dob:           str
    gender:        str
    admissionDate: str = Field(validation_alias="admission_date")
    diagnosis:     str
    doctor:        str
    department:    str
    patientType:   str = Field(validation_alias="patient_type")
    status:        str
    createdAt:     datetime = Field(validation_alias="created_at")

    model_config = ConfigDict(from_attributes=True)

class VitalCreate(BaseModel):
    patient_id:       int
    heart_rate:       int
    systolic_bp:      int
    diastolic_bp:     int
    spo2:             int
    temperature:      float
    respiratory_rate: int


class VitalResponse(BaseModel):
    id:               int
    patient_id:       int
    heart_rate:       int
    systolic_bp:      int
    diastolic_bp:     int
    spo2:             int
    temperature:      float
    respiratory_rate: int
    ai_status:        str | None
    ai_notes:         str | None
    blockchain_hash:  str | None
    created_at:       datetime

    model_config = ConfigDict(from_attributes=True)