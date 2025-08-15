from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum


class AlertSeverity(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertType(enum.Enum):
    ENVIRONMENTAL = "ENVIRONMENTAL"
    OPERATIONAL = "OPERATIONAL"
    COMPLIANCE = "COMPLIANCE"
    SYSTEM = "SYSTEM"
    SAFETY = "SAFETY"


class AlertStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    auv_id = Column(String(50), nullable=False, index=True)
    
    # Alert details
    alert_type = Column(Enum(AlertType), nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False)
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE)
    
    # Content
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    message = Column(Text)
    
    # Metadata
    source = Column(String(100))  # sensor, system, manual, etc.
    location = Column(String(200))  # coordinates or zone
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Resolution
    acknowledged_by = Column(String(100))
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_by = Column(String(100))
    resolved_at = Column(DateTime(timezone=True))
    resolution_notes = Column(Text)
    
    # Additional data
    alert_data = Column(Text)  # JSON string for additional data
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
