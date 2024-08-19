from sqlalchemy import Column, Integer, String, DateTime
from db.database import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    repo_url = Column(String, unique=True, index=True)
    user_id = Column(Integer, index=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
