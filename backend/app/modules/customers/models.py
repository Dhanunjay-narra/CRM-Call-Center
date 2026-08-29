from sqlalchemy import Column, String, DateTime, Float, Integer
from datetime import datetime, timezone
from app.core.database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    company = Column(String, default="Individual")
    tier = Column(String, default="STANDARD")  # VIP, ENTERPRISE, STANDARD
    lifetime_value = Column(Float, default=0.0)
    satisfaction_score = Column(Float, default=5.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
