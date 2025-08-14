from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ComplianceStatus(str, Enum):
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"


class ZoneType(str, Enum):
    OPERATIONAL = "OPERATIONAL"
    RESTRICTED = "RESTRICTED"
    PROHIBITED = "PROHIBITED"
    SAFETY = "SAFETY"


# ISA Standard Schemas
class ISAStandardBase(BaseModel):
    standard_code: str = Field(..., description="Unique standard code")
    standard_name: str = Field(..., description="Standard name")
    description: Optional[str] = Field(None, description="Standard description")
    version: str = Field(..., description="Standard version")
    effective_date: datetime = Field(..., description="Effective date")
    category: str = Field(..., description="Category: safety, environmental, operational")
    requirements: Optional[str] = Field(None, description="Standard requirements")


class ISAStandardCreate(ISAStandardBase):
    pass


class ISAStandardUpdate(BaseModel):
    standard_name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    effective_date: Optional[datetime] = None
    category: Optional[str] = None
    requirements: Optional[str] = None


class ISAStandardResponse(ISAStandardBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ISA Zone Schemas
class ISAZoneBase(BaseModel):
    zone_name: str = Field(..., description="Zone name")
    zone_type: ZoneType = Field(..., description="Zone type")
    coordinates: Optional[str] = Field(None, description="JSON string of coordinates")
    depth_range_min: Optional[float] = Field(None, description="Minimum depth")
    depth_range_max: Optional[float] = Field(None, description="Maximum depth")
    area_km2: Optional[float] = Field(None, description="Area in square kilometers")
    description: Optional[str] = Field(None, description="Zone description")
    restrictions: Optional[str] = Field(None, description="Zone restrictions")


class ISAZoneCreate(ISAZoneBase):
    pass


class ISAZoneUpdate(BaseModel):
    zone_name: Optional[str] = None
    zone_type: Optional[ZoneType] = None
    coordinates: Optional[str] = None
    depth_range_min: Optional[float] = None
    depth_range_max: Optional[float] = None
    area_km2: Optional[float] = None
    description: Optional[str] = None
    restrictions: Optional[str] = None


class ISAZoneResponse(ISAZoneBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ISA Compliance Schemas
class ISAComplianceBase(BaseModel):
    auv_id: str = Field(..., description="AUV identifier")
    standard_id: int = Field(..., description="ISA Standard ID")
    zone_id: Optional[int] = Field(None, description="ISA Zone ID")
    status: ComplianceStatus = Field(ComplianceStatus.PENDING, description="Compliance status")
    compliance_score: float = Field(0.0, ge=0.0, le=100.0, description="Compliance score (0-100)")
    zone_entry_time: Optional[datetime] = Field(None, description="Zone entry time")
    zone_exit_time: Optional[datetime] = Field(None, description="Zone exit time")
    zone_duration_minutes: int = Field(0, description="Duration in zone (minutes)")
    violations_count: int = Field(0, description="Number of violations")
    violations_description: Optional[str] = Field(None, description="Violations description")
    corrective_actions: Optional[str] = Field(None, description="Corrective actions")
    notes: Optional[str] = Field(None, description="Additional notes")


class ISAComplianceCreate(ISAComplianceBase):
    pass


class ISAComplianceUpdate(BaseModel):
    status: Optional[ComplianceStatus] = None
    compliance_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    zone_entry_time: Optional[datetime] = None
    zone_exit_time: Optional[datetime] = None
    zone_duration_minutes: Optional[int] = None
    violations_count: Optional[int] = None
    violations_description: Optional[str] = None
    corrective_actions: Optional[str] = None
    notes: Optional[str] = None


class ISAComplianceResponse(ISAComplianceBase):
    id: int
    last_assessment: datetime
    next_assessment: Optional[datetime] = None
    last_report_date: Optional[datetime] = None
    next_report_date: Optional[datetime] = None
    reporting_status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Include related data
    standard: Optional[ISAStandardResponse] = None
    zone: Optional[ISAZoneResponse] = None

    class Config:
        from_attributes = True


# Summary and Dashboard Schemas
class ComplianceSummary(BaseModel):
    total_auv_count: int
    compliant_auv_count: int
    non_compliant_auv_count: int
    pending_assessment_count: int
    overall_compliance_rate: float
    standards_count: int
    zones_count: int
    active_violations_count: int


class ComplianceDashboard(BaseModel):
    summary: ComplianceSummary
    recent_compliance_records: List[ISAComplianceResponse]
    upcoming_assessments: List[ISAComplianceResponse]
    standards: List[ISAStandardResponse]
    zones: List[ISAZoneResponse]
