from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


# AUV Data Schemas
class AUVDataBase(BaseModel):
    auv_id: str = Field(..., description="AUV identifier")
    timestamp: datetime = Field(..., description="Data timestamp")
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")
    depth: Optional[float] = Field(None, description="Depth in meters")
    altitude: Optional[float] = Field(None, description="Altitude in meters")
    heading: Optional[float] = Field(None, description="Heading in degrees")
    speed: Optional[float] = Field(None, description="Speed in knots")
    battery_level: Optional[float] = Field(None, ge=0.0, le=100.0, description="Battery level percentage")
    temperature: Optional[float] = Field(None, description="System temperature in Celsius")
    pressure: Optional[float] = Field(None, description="Pressure in bar")
    system_status: Optional[str] = Field(None, description="System status")
    mission_id: Optional[str] = Field(None, description="Mission identifier")
    mission_phase: Optional[str] = Field(None, description="Current mission phase")
    telemetry_data: Optional[Dict[str, Any]] = Field(None, description="Additional telemetry data")


class AUVDataCreate(AUVDataBase):
    pass


class AUVDataResponse(AUVDataBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Telemetry Data Schemas
class TelemetryDataBase(BaseModel):
    auv_id: str = Field(..., description="AUV identifier")
    timestamp: datetime = Field(..., description="Data timestamp")
    water_temperature: Optional[float] = Field(None, description="Water temperature in Celsius")
    salinity: Optional[float] = Field(None, description="Salinity in PSU")
    ph_level: Optional[float] = Field(None, description="pH level")
    dissolved_oxygen: Optional[float] = Field(None, description="Dissolved oxygen in mg/L")
    turbidity: Optional[float] = Field(None, description="Turbidity in NTU")
    current_speed: Optional[float] = Field(None, description="Current speed in m/s")
    current_direction: Optional[float] = Field(None, description="Current direction in degrees")
    sensor_data: Optional[Dict[str, Any]] = Field(None, description="Additional sensor data")
    data_quality_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Data quality score")
    sensor_status: Optional[str] = Field(None, description="Sensor status")


class TelemetryDataCreate(TelemetryDataBase):
    pass


class TelemetryDataResponse(TelemetryDataBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Real-time Telemetry Schemas
class RealTimeTelemetry(BaseModel):
    auv_id: str
    timestamp: datetime
    position: Optional[Dict[str, float]] = Field(None, description="Position data")
    environmental: Optional[Dict[str, float]] = Field(None, description="Environmental readings")
    system: Optional[Dict[str, Any]] = Field(None, description="System status")
    mission: Optional[Dict[str, Any]] = Field(None, description="Mission data")


# Historical Data Query Schemas
class TelemetryQueryParams(BaseModel):
    auv_id: Optional[str] = Field(None, description="Filter by AUV ID")
    start_time: Optional[datetime] = Field(None, description="Start time for query")
    end_time: Optional[datetime] = Field(None, description="End time for query")
    data_type: Optional[str] = Field(None, description="Type of data: auv, environmental, both")
    limit: int = Field(100, ge=1, le=1000, description="Number of records to return")
    offset: int = Field(0, ge=0, description="Number of records to skip")


class TelemetryAggregationParams(BaseModel):
    auv_id: Optional[str] = Field(None, description="Filter by AUV ID")
    start_time: datetime = Field(..., description="Start time for aggregation")
    end_time: datetime = Field(..., description="End time for aggregation")
    interval: str = Field("1h", description="Aggregation interval: 1m, 5m, 15m, 1h, 1d")
    metrics: list[str] = Field(..., description="Metrics to aggregate")


class TelemetryAggregationResponse(BaseModel):
    interval_start: datetime
    interval_end: datetime
    auv_id: str
    metrics: Dict[str, Dict[str, float]]  # metric_name -> {min, max, avg, count}
