#!/usr/bin/env python3
"""Seed demo data: caregiver Sarah caring for Michael with GBM, mid-TMZ cycle."""

import sys
import os
from datetime import datetime, timedelta, date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from database import init_db, SessionLocal
from models import User, Medication, Appointment, Conversation, SymptomReport, WellbeingScore

def seed():
    init_db()
    db = SessionLocal()

    # Clear existing data
    for model in [WellbeingScore, SymptomReport, Conversation, Appointment, Medication, User]:
        db.query(model).delete()
    db.commit()

    # Create caregiver Sarah
    sarah = User(
        role="caregiver",
        patient_name="Michael",
        caregiver_name="Sarah",
        diagnosis="Glioblastoma (GBM), Grade IV",
        doctor_name="Dr. Patel",
        clinic_name="Sunnybrook Neuro-Oncology",
        onboarding_complete=True,
    )
    db.add(sarah)
    db.commit()
    db.refresh(sarah)
    uid = sarah.id

    # TMZ medication — mid-cycle (started 12 days ago, so on day 13 = rest period)
    cycle_start = (date.today() - timedelta(days=12)).isoformat()
    db.add(Medication(
        user_id=uid,
        drug_name="Temozolomide (TMZ)",
        drug_key="tmz",
        dosage="200mg daily",
        cycle_type="tmz28",
        cycle_start_date=cycle_start,
        cycle_number=4,
        is_active=True,
    ))

    # Dexamethasone (steroid, no cycle)
    db.add(Medication(
        user_id=uid,
        drug_name="Dexamethasone",
        drug_key="dexamethasone",
        dosage="4mg twice daily",
        is_active=True,
    ))

    # Upcoming appointments
    db.add(Appointment(
        user_id=uid,
        appointment_date=(date.today() + timedelta(days=10)).isoformat(),
        appointment_type="Oncologist follow-up",
        doctor_name="Dr. Patel",
    ))
    db.add(Appointment(
        user_id=uid,
        appointment_date=(date.today() + timedelta(days=16)).isoformat(),
        appointment_type="Bloodwork",
        doctor_name="Lab",
    ))
    db.add(Appointment(
        user_id=uid,
        appointment_date=(date.today() + timedelta(days=30)).isoformat(),
        appointment_type="MRI",
        doctor_name="Radiology",
    ))

    # Conversation history (onboarding summary)
    db.add(Conversation(
        user_id=uid, role="user",
        content="Hi, I'm Sarah. I'm caring for my husband Michael who was diagnosed with GBM.",
        mode="onboarding",
    ))
    db.add(Conversation(
        user_id=uid, role="assistant",
        content="Hello Sarah, thank you for reaching out. I'm NeuroNav, and I'm here to support you as you care for Michael through his treatment journey. I'm sorry to hear about his diagnosis — that must be incredibly challenging for both of you.\n\nI've recorded that you're caring for Michael who has been diagnosed with Glioblastoma (GBM). To help you best, could you tell me about his current treatment? Is he on any medications right now?",
        mode="onboarding",
    ))

    # Symptom reports over the past 2 weeks
    symptoms = [
        ("nausea", "moderate", 3, 10),
        ("fatigue", "moderate", 4, 9),
        ("nausea", "mild", 5, 8),
        ("headache", "mild", 7, 6),
        ("nausea", "moderate", 10, 3),
        ("fatigue", "severe", 11, 2),
        ("loss of appetite", "moderate", 12, 1),
    ]
    for symptom, severity, cycle_day, days_ago in symptoms:
        db.add(SymptomReport(
            user_id=uid,
            symptom=symptom,
            severity=severity,
            cycle_day=cycle_day,
            reported_at=datetime.now() - timedelta(days=days_ago),
        ))

    # Wellbeing scores over the past 3 weeks
    wellbeing = [
        ("mood", 6, 21),
        ("stress", 5, 21),
        ("mood", 5, 18),
        ("stress", 6, 18),
        ("zarit_burnout", 4, 16),
        ("mood", 4, 14),
        ("stress", 7, 14),
        ("mood", 5, 10),
        ("stress", 6, 10),
        ("mood", 6, 7),
        ("stress", 5, 7),
        ("zarit_burnout", 5, 7),
        ("mood", 5, 3),
        ("stress", 7, 3),
        ("mood", 4, 1),
        ("stress", 8, 1),
        ("zarit_burnout", 6, 1),
    ]
    for score_type, score, days_ago in wellbeing:
        db.add(WellbeingScore(
            user_id=uid,
            score_type=score_type,
            score=score,
            recorded_at=datetime.now() - timedelta(days=days_ago),
        ))

    db.commit()
    db.close()

    print(f"Demo data seeded successfully!")
    print(f"  User ID: {uid} (Sarah, caregiver for Michael)")
    print(f"  TMZ cycle 4, started {cycle_start} (day 13 today)")
    print(f"  7 symptom reports, 17 wellbeing scores")
    print(f"  3 upcoming appointments")
    print(f"\n  Open the app and set localStorage: neuronav_user_id = \"{uid}\"")


if __name__ == "__main__":
    seed()
