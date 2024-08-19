from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.models.subscription import Subscription
from db.database import get_db

router = APIRouter()

@router.post("/subscriptions/")
def create_subscription(repo_url: str, user_id: int, db: Session = Depends(get_db)):
    db_subscription = Subscription(repo_url=repo_url, user_id=user_id)
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

@router.get("/subscriptions/")
def read_subscriptions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Subscription).offset(skip).limit(limit).all()
