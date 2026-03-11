from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Medication, Appointment
from schemas import CalendarDay
from treatment.calendar_builder import build_calendar

router = APIRouter()


@router.get("/api/calendar/{user_id}", response_model=List[CalendarDay])
def get_calendar(user_id: int, month: int = None, year: int = None, db: Session = Depends(get_db)):
    """Get treatment calendar for a user."""
    from datetime import date

    if not month:
        month = date.today().month
    if not year:
        year = date.today().year

    medications = db.query(Medication).filter(
        Medication.user_id == user_id, Medication.is_active == True
    ).all()

    appointments = db.query(Appointment).filter(
        Appointment.user_id == user_id
    ).all()

    return build_calendar(medications, appointments, year, month)
