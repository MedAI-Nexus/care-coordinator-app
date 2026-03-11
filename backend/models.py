from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, default="patient")  # patient or caregiver
    patient_name = Column(String, nullable=True)
    caregiver_name = Column(String, nullable=True)
    diagnosis = Column(String, nullable=True)
    doctor_name = Column(String, nullable=True)
    clinic_name = Column(String, nullable=True)
    onboarding_complete = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class Medication(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    drug_name = Column(String, nullable=False)
    drug_key = Column(String, nullable=True)  # e.g. "tmz", "etoposide"
    dosage = Column(String, nullable=True)
    cycle_type = Column(String, nullable=True)  # e.g. "tmz28", "etoposide28"
    cycle_start_date = Column(String, nullable=True)
    cycle_number = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_date = Column(String, nullable=False)
    appointment_type = Column(String, nullable=True)
    doctor_name = Column(String, nullable=True)
    prep_summary = Column(Text, nullable=True)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    mode = Column(String, nullable=True)  # onboarding, qa, triage, wellbeing, general
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class SymptomReport(Base):
    __tablename__ = "symptom_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    symptom = Column(String, nullable=False)
    severity = Column(String, nullable=True)  # mild, moderate, severe
    cycle_day = Column(Integer, nullable=True)
    reported_at = Column(DateTime, server_default=func.now())


class WellbeingScore(Base):
    __tablename__ = "wellbeing_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score_type = Column(String, nullable=False)  # mood, stress, zarit_burnout
    score = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    recorded_at = Column(DateTime, server_default=func.now())
