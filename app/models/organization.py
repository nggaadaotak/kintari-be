from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from datetime import datetime
from app.core.database import Base


class OrganizationInfo(Base):
    __tablename__ = "organization_info"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    founded_date = Column(String)
    ideology = Column(String)
    legal_basis = Column(Text)
    objectives = Column(Text)
    summary = Column(Text)
    full_text = Column(Text)
    extracted_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MembershipType(Base):
    __tablename__ = "membership_types"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer)
    type_name = Column(String, index=True)
    description = Column(Text)
    rights = Column(Text)
    obligations = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class OrgStructure(Base):
    __tablename__ = "organization_structure"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer)
    level = Column(String)
    name = Column(String)
    parent_id = Column(Integer, nullable=True)
    leader_name = Column(String, nullable=True)
    role = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Legacy Document model removed - use UniversalDocument instead
