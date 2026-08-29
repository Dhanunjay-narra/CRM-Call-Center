from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid
from app.core.database import get_db
from app.modules.customers.models import Customer
from app.modules.customers.schemas import CustomerCreate, CustomerResponse

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(payload: CustomerCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Customer).where(Customer.phone == payload.phone))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Customer with this phone number already exists")
    
    cust = Customer(
        id=str(uuid.uuid4()),
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone=payload.phone,
        company=payload.company or "Individual",
        tier=payload.tier or "STANDARD"
    )
    db.add(cust)
    await db.commit()
    await db.refresh(cust)
    return cust

@router.get("", response_model=list[CustomerResponse])
async def list_customers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Customer))
    return result.scalars().all()

@router.get("/by-phone/{phone}", response_model=CustomerResponse)
async def get_customer_by_phone(phone: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Customer).where(Customer.phone == phone))
    cust = result.scalars().first()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")
    return cust
