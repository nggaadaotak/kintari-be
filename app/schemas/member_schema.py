from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class MemberSchema(BaseModel):
    id: Optional[int] = None
    name: str
    email: EmailStr
    phone: Optional[str] = None
    position: Optional[str] = None
    organization: Optional[str] = None
    membership_type: Optional[str] = None
    status: str = "active"
    region: Optional[str] = None
    entry_year: Optional[int] = None
    joined_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class MemberCreateSchema(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    position: Optional[str] = None
    organization: Optional[str] = None
    membership_type: Optional[str] = None
    region: Optional[str] = None
    entry_year: Optional[int] = None
