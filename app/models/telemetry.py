from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class AUVData(Base):
    __tablename__ = "auv_data"
    
    id = Column(Integer, primary_key=True, index=True)
    auv_id = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Position and navigation
    latitude = Column(Float)
    longitude = Column(Float)
    depth = Column(Float)
    altitude = Column(Float)
    heading = Column(Float)
    speed = Column(Float)
    
    # System status
    battery_level = Column(Float)
    temperature = Column(Float)
    pressure = Column(Float)
    system_status = Column(String(50))
    
    # Mission data
    mission_id = Column(String(100))
    mission_phase = Column(String(50))
    
    # Additional telemetry
    telemetry_data = Column(JSON)  # Flexible JSON for additional metrics
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TelemetryData(Base):
    __tablename__ = "telemetry_data"
    
    id = Column(Integer, primary_key=True, index=True)
    auv_id = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Environmental readings
    water_temperature = Column(Float)
    salinity = Column(Float)
    ph_level = Column(Float)
    dissolved_oxygen = Column(Float)
    turbidity = Column(Float)
    current_speed = Column(Float)
    current_direction = Column(Float)
    
    # Sensor readings
    sensor_data = Column(JSON)  # Flexible JSON for sensor readings
    
    # Quality metrics
    data_quality_score = Column(Float)
    sensor_status = Column(String(50))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
