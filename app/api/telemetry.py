from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import json
import asyncio
from app.database import get_db
from app.models.telemetry import AUVData, TelemetryData
from app.schemas.telemetry import (
    AUVDataCreate, AUVDataResponse,
    TelemetryDataCreate, TelemetryDataResponse,
    RealTimeTelemetry, TelemetryQueryParams, TelemetryAggregationParams, TelemetryAggregationResponse
)
from sqlalchemy import and_, func, desc
import redis
from app.config import settings

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])

# Redis connection for real-time data
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


# Real-time Telemetry Endpoints
@router.post("/realtime/auv-data", response_model=AUVDataResponse)
def create_auv_data(
    auv_data: AUVDataCreate,
    db: Session = Depends(get_db)
):
    """Ingest real-time AUV telemetry data"""
    db_auv_data = AUVData(**auv_data.dict())
    db.add(db_auv_data)
    db.commit()
    db.refresh(db_auv_data)
    
    # Publish to Redis for real-time subscribers
    # Convert datetime to ISO format for JSON serialization
    data_dict = auv_data.dict()
    data_dict['timestamp'] = auv_data.timestamp.isoformat()
    
    realtime_data = {
        "type": "auv_data",
        "auv_id": auv_data.auv_id,
        "timestamp": auv_data.timestamp.isoformat(),
        "data": data_dict
    }
    redis_client.publish(f"telemetry:auv:{auv_data.auv_id}", json.dumps(realtime_data))
    
    return db_auv_data


@router.post("/realtime/environmental", response_model=TelemetryDataResponse)
def create_environmental_data(
    env_data: TelemetryDataCreate,
    db: Session = Depends(get_db)
):
    """Ingest real-time environmental telemetry data"""
    db_env_data = TelemetryData(**env_data.dict())
    db.add(db_env_data)
    db.commit()
    db.refresh(db_env_data)
    
    # Publish to Redis for real-time subscribers
    # Convert datetime to ISO format for JSON serialization
    data_dict = env_data.dict()
    data_dict['timestamp'] = env_data.timestamp.isoformat()
    
    realtime_data = {
        "type": "environmental",
        "auv_id": env_data.auv_id,
        "timestamp": env_data.timestamp.isoformat(),
        "data": data_dict
    }
    redis_client.publish(f"telemetry:environmental:{env_data.auv_id}", json.dumps(realtime_data))
    
    return db_env_data


# WebSocket endpoint for real-time telemetry
@router.websocket("/ws/{auv_id}")
async def websocket_endpoint(websocket: WebSocket, auv_id: str):
    """WebSocket endpoint for real-time telemetry subscription"""
    await websocket.accept()
    
    # Subscribe to Redis channels for this AUV
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(f"telemetry:auv:{auv_id}", f"telemetry:environmental:{auv_id}")
    
    try:
        while True:
            # Check for messages from Redis
            message = await pubsub.get_message(timeout=1)
            if message and message['type'] == 'message':
                await websocket.send_text(message['data'])
            
            # Check for client messages (subscription control)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                # Handle subscription control messages if needed
                pass
            except asyncio.TimeoutError:
                pass
            
    except WebSocketDisconnect:
        await pubsub.unsubscribe(f"telemetry:auv:{auv_id}", f"telemetry:environmental:{auv_id}")
        await pubsub.close()


# Historical Data Endpoints
@router.get("/historical/auv-data", response_model=List[AUVDataResponse])
def get_auv_historical_data(
    auv_id: Optional[str] = Query(None, description="Filter by AUV ID", example="AUV-001"),
    start_time: Optional[str] = Query(None, description="Start time for query (ISO format: YYYY-MM-DDTHH:MM:SS)", example="2025-08-10T00:00:00"),
    end_time: Optional[str] = Query(None, description="End time for query (ISO format: YYYY-MM-DDTHH:MM:SS)", example="2025-08-15T23:59:59"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return", example=100),
    offset: int = Query(0, ge=0, description="Number of records to skip", example=0),
    db: Session = Depends(get_db)
):
    """Get historical AUV telemetry data with filtering and pagination"""
    query = db.query(AUVData)
    
    if auv_id:
        query = query.filter(AUVData.auv_id == auv_id)
    if start_time:
        try:
            start_datetime = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            query = query.filter(AUVData.timestamp >= start_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_time format. Use ISO format: YYYY-MM-DDTHH:MM:SS")
    if end_time:
        try:
            end_datetime = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            query = query.filter(AUVData.timestamp <= end_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_time format. Use ISO format: YYYY-MM-DDTHH:MM:SS")
    
    auv_data = query.order_by(desc(AUVData.timestamp)).offset(offset).limit(limit).all()
    return auv_data


@router.get("/historical/environmental", response_model=List[TelemetryDataResponse])
def get_environmental_historical_data(
    auv_id: Optional[str] = Query(None, description="Filter by AUV ID", example="AUV-001"),
    start_time: Optional[str] = Query(None, description="Start time for query (ISO format: YYYY-MM-DDTHH:MM:SS)", example="2025-08-10T00:00:00"),
    end_time: Optional[str] = Query(None, description="End time for query (ISO format: YYYY-MM-DDTHH:MM:SS)", example="2025-08-15T23:59:59"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return", example=100),
    offset: int = Query(0, ge=0, description="Number of records to skip", example=0),
    db: Session = Depends(get_db)
):
    """Get historical environmental telemetry data with filtering and pagination"""
    query = db.query(TelemetryData)
    
    if auv_id:
        query = query.filter(TelemetryData.auv_id == auv_id)
    if start_time:
        try:
            start_datetime = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            query = query.filter(TelemetryData.timestamp >= start_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_time format. Use ISO format: YYYY-MM-DDTHH:MM:SS")
    if end_time:
        try:
            end_datetime = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            query = query.filter(TelemetryData.timestamp <= end_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_time format. Use ISO format: YYYY-MM-DDTHH:MM:SS")
    
    env_data = query.order_by(desc(TelemetryData.timestamp)).offset(offset).limit(limit).all()
    return env_data


# Aggregation Endpoints
@router.post("/aggregation/auv-data", response_model=List[TelemetryAggregationResponse])
def get_auv_data_aggregation(
    params: TelemetryAggregationParams,
    db: Session = Depends(get_db)
):
    """Get aggregated AUV telemetry data"""
    query = db.query(AUVData)
    
    if params.auv_id:
        query = query.filter(AUVData.auv_id == params.auv_id)
    
    query = query.filter(
        and_(
            AUVData.timestamp >= params.start_time,
            AUVData.timestamp <= params.end_time
        )
    )
    
    # Group by time intervals
    if params.interval == "1m":
        time_group = func.date_trunc('minute', AUVData.timestamp)
    elif params.interval == "5m":
        time_group = func.date_trunc('minute', AUVData.timestamp - timedelta(minutes=AUVData.timestamp.minute % 5))
    elif params.interval == "15m":
        time_group = func.date_trunc('minute', AUVData.timestamp - timedelta(minutes=AUVData.timestamp.minute % 15))
    elif params.interval == "1h":
        time_group = func.date_trunc('hour', AUVData.timestamp)
    elif params.interval == "1d":
        time_group = func.date_trunc('day', AUVData.timestamp)
    else:
        time_group = func.date_trunc('hour', AUVData.timestamp)
    
    # Build aggregation query
    select_fields = [time_group.label('interval_start')]
    select_fields.append(AUVData.auv_id)
    
    for metric in params.metrics:
        if hasattr(AUVData, metric):
            select_fields.extend([
                func.min(getattr(AUVData, metric)).label(f'{metric}_min'),
                func.max(getattr(AUVData, metric)).label(f'{metric}_max'),
                func.avg(getattr(AUVData, metric)).label(f'{metric}_avg'),
                func.count(getattr(AUVData, metric)).label(f'{metric}_count')
            ])
    
    query = query.with_entities(*select_fields).group_by(time_group, AUVData.auv_id)
    
    results = query.all()
    
    # Format results
    formatted_results = []
    for result in results:
        metrics = {}
        for metric in params.metrics:
            if hasattr(AUVData, metric):
                metrics[metric] = {
                    'min': getattr(result, f'{metric}_min'),
                    'max': getattr(result, f'{metric}_max'),
                    'avg': getattr(result, f'{metric}_avg'),
                    'count': getattr(result, f'{metric}_count')
                }
        
        # Calculate interval_end based on interval type
        interval_start = result.interval_start
        if params.interval == "1m":
            interval_end = interval_start + timedelta(minutes=1)
        elif params.interval == "5m":
            interval_end = interval_start + timedelta(minutes=5)
        elif params.interval == "15m":
            interval_end = interval_start + timedelta(minutes=15)
        elif params.interval == "1h":
            interval_end = interval_start + timedelta(hours=1)
        elif params.interval == "1d":
            interval_end = interval_start + timedelta(days=1)
        else:
            interval_end = interval_start + timedelta(hours=1)
        
        formatted_results.append(TelemetryAggregationResponse(
            interval_start=interval_start,
            interval_end=interval_end,
            auv_id=result.auv_id,
            metrics=metrics
        ))
    
    return formatted_results


@router.post("/aggregation/environmental", response_model=List[TelemetryAggregationResponse])
def get_environmental_aggregation(
    params: TelemetryAggregationParams,
    db: Session = Depends(get_db)
):
    """Get aggregated environmental telemetry data"""
    query = db.query(TelemetryData)
    
    if params.auv_id:
        query = query.filter(TelemetryData.auv_id == params.auv_id)
    
    query = query.filter(
        and_(
            TelemetryData.timestamp >= params.start_time,
            TelemetryData.timestamp <= params.end_time
        )
    )
    
    # Group by time intervals
    if params.interval == "1m":
        time_group = func.date_trunc('minute', TelemetryData.timestamp)
    elif params.interval == "5m":
        time_group = func.date_trunc('minute', TelemetryData.timestamp - timedelta(minutes=TelemetryData.timestamp.minute % 5))
    elif params.interval == "15m":
        time_group = func.date_trunc('minute', TelemetryData.timestamp - timedelta(minutes=TelemetryData.timestamp.minute % 15))
    elif params.interval == "1h":
        time_group = func.date_trunc('hour', TelemetryData.timestamp)
    elif params.interval == "1d":
        time_group = func.date_trunc('day', TelemetryData.timestamp)
    else:
        time_group = func.date_trunc('hour', TelemetryData.timestamp)
    
    # Build aggregation query
    select_fields = [time_group.label('interval_start')]
    select_fields.append(TelemetryData.auv_id)
    
    for metric in params.metrics:
        if hasattr(TelemetryData, metric):
            select_fields.extend([
                func.min(getattr(TelemetryData, metric)).label(f'{metric}_min'),
                func.max(getattr(TelemetryData, metric)).label(f'{metric}_max'),
                func.avg(getattr(TelemetryData, metric)).label(f'{metric}_avg'),
                func.count(getattr(TelemetryData, metric)).label(f'{metric}_count')
            ])
    
    query = query.with_entities(*select_fields).group_by(time_group, TelemetryData.auv_id)
    
    results = query.all()
    
    # Format results
    formatted_results = []
    for result in results:
        metrics = {}
        for metric in params.metrics:
            if hasattr(TelemetryData, metric):
                metrics[metric] = {
                    'min': getattr(result, f'{metric}_min'),
                    'max': getattr(result, f'{metric}_max'),
                    'avg': getattr(result, f'{metric}_avg'),
                    'count': getattr(result, f'{metric}_count')
                }
        
        # Calculate interval_end based on interval type
        interval_start = result.interval_start
        if params.interval == "1m":
            interval_end = interval_start + timedelta(minutes=1)
        elif params.interval == "5m":
            interval_end = interval_start + timedelta(minutes=5)
        elif params.interval == "15m":
            interval_end = interval_start + timedelta(minutes=15)
        elif params.interval == "1h":
            interval_end = interval_start + timedelta(hours=1)
        elif params.interval == "1d":
            interval_end = interval_start + timedelta(days=1)
        else:
            interval_end = interval_start + timedelta(hours=1)
        
        formatted_results.append(TelemetryAggregationResponse(
            interval_start=interval_start,
            interval_end=interval_end,
            auv_id=result.auv_id,
            metrics=metrics
        ))
    
    return formatted_results


# AUV-specific endpoints
@router.get("/auv/{auv_id}/latest", response_model=Dict[str, Any])
def get_auv_latest_data(auv_id: str, db: Session = Depends(get_db)):
    """Get latest telemetry data for a specific AUV"""
    # Get latest AUV data
    latest_auv = db.query(AUVData).filter(
        AUVData.auv_id == auv_id
    ).order_by(desc(AUVData.timestamp)).first()
    
    # Get latest environmental data
    latest_env = db.query(TelemetryData).filter(
        TelemetryData.auv_id == auv_id
    ).order_by(desc(TelemetryData.timestamp)).first()
    
    # Convert database objects to dictionaries and handle datetime serialization
    auv_data_dict = None
    if latest_auv:
        auv_data_dict = {
            "id": latest_auv.id,
            "auv_id": latest_auv.auv_id,
            "timestamp": latest_auv.timestamp.isoformat(),
            "latitude": latest_auv.latitude,
            "longitude": latest_auv.longitude,
            "depth": latest_auv.depth,
            "altitude": latest_auv.altitude,
            "heading": latest_auv.heading,
            "speed": latest_auv.speed,
            "battery_level": latest_auv.battery_level,
            "temperature": latest_auv.temperature,
            "pressure": latest_auv.pressure,
            "system_status": latest_auv.system_status,
            "mission_id": latest_auv.mission_id,
            "mission_phase": latest_auv.mission_phase,
            "telemetry_data": latest_auv.telemetry_data
        }
    
    env_data_dict = None
    if latest_env:
        env_data_dict = {
            "id": latest_env.id,
            "auv_id": latest_env.auv_id,
            "timestamp": latest_env.timestamp.isoformat(),
            "water_temperature": latest_env.water_temperature,
            "salinity": latest_env.salinity,
            "ph_level": latest_env.ph_level,
            "dissolved_oxygen": latest_env.dissolved_oxygen,
            "turbidity": latest_env.turbidity,
            "current_speed": latest_env.current_speed,
            "current_direction": latest_env.current_direction,
            "sensor_data": latest_env.sensor_data,
            "data_quality_score": latest_env.data_quality_score,
            "sensor_status": latest_env.sensor_status
        }
    
    return {
        "auv_id": auv_id,
        "auv_data": auv_data_dict,
        "environmental_data": env_data_dict,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/auv/{auv_id}/status")
def get_auv_status(auv_id: str, db: Session = Depends(get_db)):
    """Get current status of a specific AUV"""
    latest_data = db.query(AUVData).filter(
        AUVData.auv_id == auv_id
    ).order_by(desc(AUVData.timestamp)).first()
    
    if not latest_data:
        raise HTTPException(status_code=404, detail="AUV data not found")
    
    # Calculate time since last update (use timezone-aware datetime)
    time_since_update = datetime.now(timezone.utc) - latest_data.timestamp
    
    # Determine status based on last update time
    if time_since_update.total_seconds() < 300:  # 5 minutes
        status = "active"
    elif time_since_update.total_seconds() < 3600:  # 1 hour
        status = "warning"
    else:
        status = "inactive"
    
    return {
        "auv_id": auv_id,
        "status": status,
        "last_update": latest_data.timestamp.isoformat(),
        "time_since_update_seconds": time_since_update.total_seconds(),
        "battery_level": latest_data.battery_level,
        "system_status": latest_data.system_status,
        "position": {
            "latitude": latest_data.latitude,
            "longitude": latest_data.longitude,
            "depth": latest_data.depth
        }
    }


# Data Quality Endpoints
@router.get("/quality/auv/{auv_id}")
def get_auv_data_quality(auv_id: str, db: Session = Depends(get_db)):
    """Get data quality metrics for a specific AUV"""
    # Get data from last 24 hours
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    
    auv_data_count = db.query(func.count(AUVData.id)).filter(
        and_(
            AUVData.auv_id == auv_id,
            AUVData.timestamp >= yesterday
        )
    ).scalar()
    
    env_data_count = db.query(func.count(TelemetryData.id)).filter(
        and_(
            TelemetryData.auv_id == auv_id,
            TelemetryData.timestamp >= yesterday
        )
    ).scalar()
    
    # Calculate expected data points (assuming 1-minute intervals)
    expected_points = 24 * 60  # 24 hours * 60 minutes
    
    auv_completeness = (auv_data_count / expected_points * 100) if expected_points > 0 else 0
    env_completeness = (env_data_count / expected_points * 100) if expected_points > 0 else 0
    
    return {
        "auv_id": auv_id,
        "time_period": "last_24_hours",
        "auv_data": {
            "total_records": auv_data_count,
            "expected_records": expected_points,
            "completeness_percentage": auv_completeness
        },
        "environmental_data": {
            "total_records": env_data_count,
            "expected_records": expected_points,
            "completeness_percentage": env_completeness
        },
        "overall_quality_score": (auv_completeness + env_completeness) / 2
    }
