from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models import User, Medication
from schemas import UserCreate, UserResponse

router = APIRouter()


@router.post("/api/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(
        role=user.role,
        patient_name=user.patient_name,
        caregiver_name=user.caregiver_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/api/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, updates: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in updates.items():
        if hasattr(user, key):
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


class OnboardingMedication(BaseModel):
    user_id: int
    drug_name: str
    drug_key: Optional[str] = None
    dosage: Optional[str] = None
    cycle_type: Optional[str] = None
    cycle_start_date: Optional[str] = None


@router.post("/api/onboarding/medication")
def save_onboarding_medication(med: OnboardingMedication, db: Session = Depends(get_db)):
    db_med = Medication(
        user_id=med.user_id,
        drug_name=med.drug_name,
        drug_key=med.drug_key,
        dosage=med.dosage,
        cycle_type=med.cycle_type,
        cycle_start_date=med.cycle_start_date,
        is_active=True,
    )
    db.add(db_med)
    db.commit()
    return {"status": "ok"}
