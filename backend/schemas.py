from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    user_id: int
    message: str


class UserCreate(BaseModel):
    role: str = "patient"
    patient_name: Optional[str] = None
    caregiver_name: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    role: str
    patient_name: Optional[str]
    caregiver_name: Optional[str]
    diagnosis: Optional[str]
    doctor_name: Optional[str]
    clinic_name: Optional[str]
    onboarding_complete: bool

    class Config:
        from_attributes = True


class AppointmentCreate(BaseModel):
    user_id: int
    appointment_date: str
    appointment_type: Optional[str] = None
    doctor_name: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: int
    user_id: int
    appointment_date: str
    appointment_type: Optional[str]
    doctor_name: Optional[str]
    prep_summary: Optional[str]

    class Config:
        from_attributes = True


class MedicationResponse(BaseModel):
    id: int
    user_id: int
    drug_name: str
    drug_key: Optional[str]
    dosage: Optional[str]
    cycle_type: Optional[str]
    cycle_start_date: Optional[str]
    cycle_number: Optional[int]
    is_active: bool

    class Config:
        from_attributes = True


class SymptomResponse(BaseModel):
    id: int
    symptom: str
    severity: Optional[str]
    cycle_day: Optional[int]
    reported_at: Optional[datetime]

    class Config:
        from_attributes = True


class WellbeingResponse(BaseModel):
    id: int
    score_type: str
    score: float
    notes: Optional[str]
    recorded_at: Optional[datetime]

    class Config:
        from_attributes = True


class CalendarDay(BaseModel):
    date: str
    day_type: str  # drug, rest, bloodwork, appointment
    label: Optional[str] = None
    drug_name: Optional[str] = None
