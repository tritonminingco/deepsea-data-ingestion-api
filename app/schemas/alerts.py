from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AlertSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertType(str, Enum):
    ENVIRONMENTAL = "ENVIRONMENTAL"
    OPERATIONAL = "OPERATIONAL"
    COMPLIANCE = "COMPLIANCE"
    SYSTEM = "SYSTEM"
    SAFETY = "SAFETY"


class AlertStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


# Alert Schemas
class AlertBase(BaseModel):
    auv_id: str = Field(..., description="AUV identifier")
    alert_type: AlertType = Field(..., description="Type of alert")
    severity: AlertSeverity = Field(..., description="Alert severity")
    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Alert description")
    message: Optional[str] = Field(None, description="Detailed message")
    source: Optional[str] = Field(None, description="Alert source")
    location: Optional[str] = Field(None, description="Alert location")
    timestamp: datetime = Field(..., description="Alert timestamp")
    alert_data: Optional[str] = Field(None, description="Additional alert data as JSON string")


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    acknowledged_by: Optional[str] = Field(None, description="User who acknowledged")
    resolved_by: Optional[str] = Field(None, description="User who resolved")
    resolution_notes: Optional[str] = Field(None, description="Resolution notes")
    alert_data: Optional[str] = None


class AlertResponse(AlertBase):
    id: int
    status: AlertStatus
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Alert Query Schemas
class AlertQueryParams(BaseModel):
    auv_id: Optional[str] = Field(None, description="Filter by AUV ID")
    alert_type: Optional[AlertType] = Field(None, description="Filter by alert type")
    severity: Optional[AlertSeverity] = Field(None, description="Filter by severity")
    status: Optional[AlertStatus] = Field(None, description="Filter by status")
    start_time: Optional[datetime] = Field(None, description="Start time for query")
    end_time: Optional[datetime] = Field(None, description="End time for query")
    search: Optional[str] = Field(None, description="Search in title and description")
    limit: int = Field(100, ge=1, le=1000, description="Number of records to return")
    offset: int = Field(0, ge=0, description="Number of records to skip")


# Alert Summary Schemas
class AlertSummary(BaseModel):
    total_alerts: int
    active_alerts: int
    acknowledged_alerts: int
    resolved_alerts: int
    critical_alerts: int
    high_severity_alerts: int
    alerts_by_type: dict[str, int]
    alerts_by_severity: dict[str, int]


class AlertFeedResponse(BaseModel):
    alerts: List[AlertResponse]
    summary: AlertSummary
    total_count: int
    has_more: bool


# Bulk Operation Schemas
class BulkAcknowledgeRequest(BaseModel):
    alert_ids: List[int] = Field(..., description="List of alert IDs to acknowledge", example=[3, 5, 9])

    class Config:
        json_schema_extra = {
            "example": {
                "alert_ids": [3, 5, 9]
            }
        }


class BulkResolveRequest(BaseModel):
    alert_ids: List[int] = Field(..., description="List of alert IDs to resolve", example=[3, 5, 9])

    class Config:
        json_schema_extra = {
            "example": {
                "alert_ids": [3, 5, 9]
            }
        }
