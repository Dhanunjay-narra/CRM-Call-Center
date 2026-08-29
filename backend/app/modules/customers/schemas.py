from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class CustomerCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    company: Optional[str] = "Individual"
    tier: Optional[str] = "STANDARD"

class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    company: str
    tier: str
    lifetime_value: float
    satisfaction_score: float
