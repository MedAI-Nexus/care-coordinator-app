from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime, timedelta

from database import get_db
from models import Appointment, User, Medication, SymptomReport, WellbeingScore, Conversation
from schemas import AppointmentCreate, AppointmentResponse

router = APIRouter()


@router.get("/api/appointments/{user_id}", response_model=List[AppointmentResponse])
def get_appointments(user_id: int, db: Session = Depends(get_db)):
    """Get upcoming appointments for a user."""
    return db.query(Appointment).filter(
        Appointment.user_id == user_id,
        Appointment.appointment_date >= date.today().isoformat(),
    ).order_by(Appointment.appointment_date).all()


@router.post("/api/appointments", response_model=AppointmentResponse)
def create_appointment(apt: AppointmentCreate, db: Session = Depends(get_db)):
    db_apt = Appointment(
        user_id=apt.user_id,
        appointment_date=apt.appointment_date,
        appointment_type=apt.appointment_type,
        doctor_name=apt.doctor_name,
    )
    db.add(db_apt)
    db.commit()
    db.refresh(db_apt)
    return db_apt


@router.get("/api/appointments/{user_id}/{appointment_id}/prep")
def get_appointment_prep(user_id: int, appointment_id: int, db: Session = Depends(get_db)):
    """Auto-generate and return appointment prep summary."""
    apt = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.user_id == user_id,
    ).first()
    if not apt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Always regenerate fresh from current data
    user = db.query(User).filter(User.id == user_id).first()
    thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()

    meds = db.query(Medication).filter(
        Medication.user_id == user_id, Medication.is_active == True
    ).all()

    symptoms = db.query(SymptomReport).filter(
        SymptomReport.user_id == user_id,
        SymptomReport.reported_at >= thirty_days_ago,
    ).order_by(SymptomReport.reported_at.desc()).all()

    scores = db.query(WellbeingScore).filter(
        WellbeingScore.user_id == user_id,
        WellbeingScore.recorded_at >= thirty_days_ago,
    ).order_by(WellbeingScore.recorded_at.desc()).all()

    # Extract key concerns from recent conversations
    recent_convos = db.query(Conversation).filter(
        Conversation.user_id == user_id,
        Conversation.role == "user",
        Conversation.created_at >= thirty_days_ago,
    ).order_by(Conversation.created_at.desc()).limit(20).all()

    # Build summary
    parts = [
        f"## Appointment Preparation Summary",
        f"**Date:** {apt.appointment_date}",
        f"**Type:** {apt.appointment_type or 'General'}",
        f"**Doctor:** {apt.doctor_name or (user.doctor_name if user else 'Not specified')}",
        f"**Patient:** {user.patient_name if user else 'Unknown'}",
        "",
    ]

    # Medications
    if meds:
        parts.append("### Current Medications")
        for m in meds:
            line = f"- **{m.drug_name}**"
            if m.dosage:
                line += f" — {m.dosage}"
            if m.cycle_type and m.cycle_start_date:
                try:
                    start = datetime.strptime(m.cycle_start_date, "%Y-%m-%d").date()
                    cycle_day = (date.today() - start).days % 28 + 1
                    line += f" (cycle day {cycle_day}, cycle #{m.cycle_number or '?'})"
                except (ValueError, TypeError):
                    pass
            parts.append(line)
        parts.append("")

    # Symptoms
    symptom_counts = {}
    if symptoms:
        parts.append("### Symptoms Reported (Last 30 Days)")
        # Group by symptom for pattern detection
        symptom_counts = {}
        for s in symptoms:
            key = s.symptom.lower()
            if key not in symptom_counts:
                symptom_counts[key] = {"count": 0, "severities": [], "cycle_days": []}
            symptom_counts[key]["count"] += 1
            symptom_counts[key]["severities"].append(s.severity)
            if s.cycle_day:
                symptom_counts[key]["cycle_days"].append(s.cycle_day)

        for symptom, info in symptom_counts.items():
            worst = "severe" if "severe" in info["severities"] else (
                "moderate" if "moderate" in info["severities"] else "mild"
            )
            line = f"- **{symptom.title()}** — reported {info['count']}x, worst severity: {worst}"
            if info["cycle_days"]:
                line += f" (on cycle days: {', '.join(str(d) for d in info['cycle_days'])})"
            parts.append(line)

        # Flag patterns
        for symptom, info in symptom_counts.items():
            if info["count"] >= 3:
                parts.append(f"  - ⚠️ **Pattern detected:** {symptom.title()} reported {info['count']} times — discuss with doctor")
        parts.append("")

    # Wellbeing
    if scores:
        parts.append("### Wellbeing Summary (Last 30 Days)")
        for score_type in ["mood", "stress", "zarit_burnout"]:
            type_scores = [s for s in scores if s.score_type == score_type]
            if type_scores:
                values = [s.score for s in type_scores]
                avg = sum(values) / len(values)
                latest = type_scores[0].score
                trend = "↑ improving" if len(values) > 1 and values[0] > values[-1] else (
                    "↓ declining" if len(values) > 1 and values[0] < values[-1] else "→ stable"
                )
                label = score_type.replace("_", " ").title()
                if score_type == "stress":
                    trend = "↑ increasing" if len(values) > 1 and values[0] > values[-1] else (
                        "↓ decreasing" if len(values) > 1 and values[0] < values[-1] else "→ stable"
                    )
                parts.append(f"- **{label}:** current {latest}/10, avg {avg:.1f}/10 ({trend})")
        parts.append("")

    # Key concerns from conversations
    if recent_convos:
        parts.append("### Recent Topics Discussed")
        topics = set()
        for c in recent_convos[:10]:
            content = c.content.lower()
            if any(w in content for w in ["fever", "temperature", "hot"]):
                topics.add("Fever concerns")
            if any(w in content for w in ["nausea", "vomit", "sick"]):
                topics.add("Nausea/vomiting")
            if any(w in content for w in ["tired", "fatigue", "exhausted", "energy"]):
                topics.add("Fatigue")
            if any(w in content for w in ["headache", "head pain"]):
                topics.add("Headaches")
            if any(w in content for w in ["sleep", "insomnia"]):
                topics.add("Sleep issues")
            if any(w in content for w in ["anxious", "anxiety", "worried", "stress"]):
                topics.add("Anxiety/stress")
            if any(w in content for w in ["seizure"]):
                topics.add("Seizure concerns")
            if any(w in content for w in ["appetite", "eating", "food"]):
                topics.add("Appetite/diet")
        if topics:
            for t in sorted(topics):
                parts.append(f"- {t}")
        else:
            parts.append("- General check-in conversations")
        parts.append("")

    # Suggested questions
    parts.append("### Suggested Questions for the Doctor")
    parts.append("- How is the treatment progressing? Any changes to the plan?")
    if any(s.severity == "severe" for s in symptoms):
        parts.append("- Are the severe symptoms I've been experiencing expected, or should we adjust medication?")
    if symptom_counts:
        most_frequent = max(symptom_counts.items(), key=lambda x: x[1]["count"])
        if most_frequent[1]["count"] >= 2:
            parts.append(f"- {most_frequent[0].title()} has been recurring — is there anything we can do about it?")
    parts.append("- Are there any upcoming scans or tests I should prepare for?")
    parts.append("- Are there any clinical trials or new treatments to consider?")
    if any(s.score_type == "zarit_burnout" for s in scores):
        parts.append("- What caregiver support resources are available through the clinic?")

    summary = "\n".join(parts)

    # Save to appointment
    apt.prep_summary = summary
    db.commit()

    return {"prep_summary": summary}
