from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from database import get_db
from models import WellbeingScore
from schemas import WellbeingResponse

router = APIRouter()


@router.get("/api/wellbeing/{user_id}", response_model=List[WellbeingResponse])
def get_wellbeing(user_id: int, score_type: str = None, days: int = 30, db: Session = Depends(get_db)):
    """Get wellbeing scores for a user."""
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    query = db.query(WellbeingScore).filter(
        WellbeingScore.user_id == user_id,
        WellbeingScore.recorded_at >= cutoff,
    )
    if score_type:
        query = query.filter(WellbeingScore.score_type == score_type)
    return query.order_by(WellbeingScore.recorded_at).all()
