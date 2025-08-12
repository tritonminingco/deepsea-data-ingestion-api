from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ComplianceStatus(enum.Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING = "pending"
    UNDER_REVIEW = "under_review"


class ZoneType(enum.Enum):
    OPERATIONAL = "operational"
    RESTRICTED = "restricted"
    PROHIBITED = "prohibited"
    SAFETY = "safety"


class ISAStandard(Base):
    __tablename__ = "isa_standards"
    
    id = Column(Integer, primary_key=True, index=True)
    standard_code = Column(String(50), unique=True, index=True, nullable=False)
    standard_name = Column(String(200), nullable=False)
    description = Column(Text)
    version = Column(String(20), nullable=False)
    effective_date = Column(DateTime, nullable=False)
    category = Column(String(100), nullable=False)  # safety, environmental, operational
    requirements = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    compliance_records = relationship("ISACompliance", back_populates="standard")


class ISAZone(Base):
    __tablename__ = "isa_zones"
    
    id = Column(Integer, primary_key=True, index=True)
    zone_name = Column(String(100), nullable=False)
    zone_type = Column(Enum(ZoneType), nullable=False)
    coordinates = Column(Text)  # JSON string of coordinates
    depth_range_min = Column(Float)
    depth_range_max = Column(Float)
    area_km2 = Column(Float)
    description = Column(Text)
    restrictions = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    compliance_records = relationship("ISACompliance", back_populates="zone")


class ISACompliance(Base):
    __tablename__ = "isa_compliance"
    
    id = Column(Integer, primary_key=True, index=True)
    auv_id = Column(String(50), nullable=False, index=True)
    standard_id = Column(Integer, ForeignKey("isa_standards.id"), nullable=False)
    zone_id = Column(Integer, ForeignKey("isa_zones.id"), nullable=True)
    
    status = Column(Enum(ComplianceStatus), nullable=False, default=ComplianceStatus.PENDING)
    compliance_score = Column(Float, default=0.0)  # 0-100 scale
    last_assessment = Column(DateTime(timezone=True), server_default=func.now())
    next_assessment = Column(DateTime(timezone=True))
    
    # Zone-specific compliance
    zone_entry_time = Column(DateTime(timezone=True))
    zone_exit_time = Column(DateTime(timezone=True))
    zone_duration_minutes = Column(Integer, default=0)
    
    # Reporting
    last_report_date = Column(DateTime(timezone=True))
    next_report_date = Column(DateTime(timezone=True))
    reporting_status = Column(String(50), default="pending")  # pending, submitted, approved, rejected
    
    # Compliance details
    violations_count = Column(Integer, default=0)
    violations_description = Column(Text)
    corrective_actions = Column(Text)
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    standard = relationship("ISAStandard", back_populates="compliance_records")
    zone = relationship("ISAZone", back_populates="compliance_records")
