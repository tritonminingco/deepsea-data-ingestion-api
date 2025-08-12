from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models.alerts import Alert, AlertSeverity, AlertType, AlertStatus
from app.schemas.alerts import (
    AlertCreate, AlertUpdate, AlertResponse,
    AlertQueryParams, AlertSummary, AlertFeedResponse
)
from sqlalchemy import and_, or_, func, desc, text
import redis
from app.config import settings

router = APIRouter(prefix="/alerts", tags=["Alerts"])

# Redis connection for real-time alerts
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


# Alert CRUD Endpoints
@router.post("/", response_model=AlertResponse)
def create_alert(
    alert: AlertCreate,
    db: Session = Depends(get_db)
):
    """Create a new alert"""
    db_alert = Alert(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    # Publish to Redis for real-time subscribers
    alert_data = {
        "type": "new_alert",
        "alert_id": db_alert.id,
        "auv_id": db_alert.auv_id,
        "severity": db_alert.severity.value,
        "alert_type": db_alert.alert_type.value,
        "title": db_alert.title,
        "timestamp": db_alert.timestamp.isoformat()
    }
    redis_client.publish("alerts:new", str(alert_data))
    
    return db_alert


@router.get("/", response_model=List[AlertResponse])
def get_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auv_id: Optional[str] = Query(None),
    alert_type: Optional[AlertType] = Query(None),
    severity: Optional[AlertSeverity] = Query(None),
    status: Optional[AlertStatus] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get alerts with filtering and pagination"""
    query = db.query(Alert)
    
    if auv_id:
        query = query.filter(Alert.auv_id == auv_id)
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    if severity:
        query = query.filter(Alert.severity == severity)
    if status:
        query = query.filter(Alert.status == status)
    if start_time:
        query = query.filter(Alert.timestamp >= start_time)
    if end_time:
        query = query.filter(Alert.timestamp <= end_time)
    if search:
        search_filter = or_(
            Alert.title.ilike(f"%{search}%"),
            Alert.description.ilike(f"%{search}%"),
            Alert.message.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    alerts = query.order_by(desc(Alert.timestamp)).offset(skip).limit(limit).all()
    return alerts


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Get a specific alert by ID"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.put("/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    db: Session = Depends(get_db)
):
    """Update an alert"""
    db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    update_data = alert_update.dict(exclude_unset=True)
    
    # Handle status changes
    if 'status' in update_data:
        if update_data['status'] == AlertStatus.ACKNOWLEDGED and not db_alert.acknowledged_at:
            update_data['acknowledged_at'] = datetime.utcnow()
        elif update_data['status'] == AlertStatus.RESOLVED and not db_alert.resolved_at:
            update_data['resolved_at'] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_alert, field, value)
    
    db.commit()
    db.refresh(db_alert)
    
    # Publish status change to Redis
    status_data = {
        "type": "alert_status_change",
        "alert_id": db_alert.id,
        "auv_id": db_alert.auv_id,
        "old_status": db_alert.status.value,
        "new_status": update_data.get('status', db_alert.status.value)
    }
    redis_client.publish("alerts:status_change", str(status_data))
    
    return db_alert


@router.delete("/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """Delete an alert"""
    db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db.delete(db_alert)
    db.commit()
    return {"message": "Alert deleted successfully"}


# Alert Feed and Summary Endpoints
@router.get("/feed/", response_model=AlertFeedResponse)
def get_alert_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    auv_id: Optional[str] = Query(None),
    alert_type: Optional[AlertType] = Query(None),
    severity: Optional[AlertSeverity] = Query(None),
    status: Optional[AlertStatus] = Query(None),
    db: Session = Depends(get_db)
):
    """Get alert feed with summary statistics"""
    # Build query for alerts
    query = db.query(Alert)
    
    if auv_id:
        query = query.filter(Alert.auv_id == auv_id)
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    if severity:
        query = query.filter(Alert.severity == severity)
    if status:
        query = query.filter(Alert.status == status)
    
    # Get total count for pagination
    total_count = query.count()
    
    # Get alerts
    alerts = query.order_by(desc(Alert.timestamp)).offset(skip).limit(limit).all()
    
    # Calculate summary statistics
    summary = get_alert_summary(db, auv_id, alert_type, severity, status)
    
    return AlertFeedResponse(
        alerts=alerts,
        summary=summary,
        total_count=total_count,
        has_more=(skip + limit) < total_count
    )


@router.get("/summary/", response_model=AlertSummary)
def get_alert_summary_endpoint(
    auv_id: Optional[str] = Query(None),
    alert_type: Optional[AlertType] = Query(None),
    severity: Optional[AlertSeverity] = Query(None),
    status: Optional[AlertStatus] = Query(None),
    db: Session = Depends(get_db)
):
    """Get alert summary statistics"""
    return get_alert_summary(db, auv_id, alert_type, severity, status)


def get_alert_summary(
    db: Session,
    auv_id: Optional[str] = None,
    alert_type: Optional[AlertType] = None,
    severity: Optional[AlertSeverity] = None,
    status: Optional[AlertStatus] = None
) -> AlertSummary:
    """Helper function to calculate alert summary statistics"""
    base_query = db.query(Alert)
    
    # Apply filters
    if auv_id:
        base_query = base_query.filter(Alert.auv_id == auv_id)
    if alert_type:
        base_query = base_query.filter(Alert.alert_type == alert_type)
    if severity:
        base_query = base_query.filter(Alert.severity == severity)
    if status:
        base_query = base_query.filter(Alert.status == status)
    
    # Get total alerts
    total_alerts = base_query.count()
    
    # Get status counts
    active_alerts = base_query.filter(Alert.status == AlertStatus.ACTIVE).count()
    acknowledged_alerts = base_query.filter(Alert.status == AlertStatus.ACKNOWLEDGED).count()
    resolved_alerts = base_query.filter(Alert.status == AlertStatus.RESOLVED).count()
    
    # Get severity counts
    critical_alerts = base_query.filter(Alert.severity == AlertSeverity.CRITICAL).count()
    high_severity_alerts = base_query.filter(Alert.severity == AlertSeverity.HIGH).count()
    
    # Get alerts by type
    alerts_by_type = {}
    for alert_type_enum in AlertType:
        count = base_query.filter(Alert.alert_type == alert_type_enum).count()
        alerts_by_type[alert_type_enum.value] = count
    
    # Get alerts by severity
    alerts_by_severity = {}
    for severity_enum in AlertSeverity:
        count = base_query.filter(Alert.severity == severity_enum).count()
        alerts_by_severity[severity_enum.value] = count
    
    return AlertSummary(
        total_alerts=total_alerts,
        active_alerts=active_alerts,
        acknowledged_alerts=acknowledged_alerts,
        resolved_alerts=resolved_alerts,
        critical_alerts=critical_alerts,
        high_severity_alerts=high_severity_alerts,
        alerts_by_type=alerts_by_type,
        alerts_by_severity=alerts_by_severity
    )


# AUV-specific Alert Endpoints
@router.get("/auv/{auv_id}/", response_model=List[AlertResponse])
def get_auv_alerts(
    auv_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    alert_type: Optional[AlertType] = Query(None),
    severity: Optional[AlertSeverity] = Query(None),
    status: Optional[AlertStatus] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all alerts for a specific AUV"""
    query = db.query(Alert).filter(Alert.auv_id == auv_id)
    
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    if severity:
        query = query.filter(Alert.severity == severity)
    if status:
        query = query.filter(Alert.status == status)
    
    alerts = query.order_by(desc(Alert.timestamp)).offset(skip).limit(limit).all()
    return alerts


@router.get("/auv/{auv_id}/summary", response_model=AlertSummary)
def get_auv_alert_summary(auv_id: str, db: Session = Depends(get_db)):
    """Get alert summary for a specific AUV"""
    return get_alert_summary(db, auv_id=auv_id)


@router.get("/auv/{auv_id}/active", response_model=List[AlertResponse])
def get_auv_active_alerts(auv_id: str, db: Session = Depends(get_db)):
    """Get active alerts for a specific AUV"""
    alerts = db.query(Alert).filter(
        and_(
            Alert.auv_id == auv_id,
            Alert.status == AlertStatus.ACTIVE
        )
    ).order_by(desc(Alert.timestamp)).all()
    return alerts


# Alert Management Endpoints
@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(
    alert_id: int,
    acknowledged_by: str = Query(..., description="User acknowledging the alert"),
    db: Session = Depends(get_db)
):
    """Acknowledge an alert"""
    db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if db_alert.status == AlertStatus.ACKNOWLEDGED:
        raise HTTPException(status_code=400, detail="Alert already acknowledged")
    
    db_alert.status = AlertStatus.ACKNOWLEDGED
    db_alert.acknowledged_by = acknowledged_by
    db_alert.acknowledged_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_alert)
    
    # Publish to Redis
    status_data = {
        "type": "alert_acknowledged",
        "alert_id": db_alert.id,
        "auv_id": db_alert.auv_id,
        "acknowledged_by": acknowledged_by
    }
    redis_client.publish("alerts:acknowledged", str(status_data))
    
    return db_alert


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(
    alert_id: int,
    resolved_by: str = Query(..., description="User resolving the alert"),
    resolution_notes: Optional[str] = Query(None, description="Resolution notes"),
    db: Session = Depends(get_db)
):
    """Resolve an alert"""
    db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if db_alert.status == AlertStatus.RESOLVED:
        raise HTTPException(status_code=400, detail="Alert already resolved")
    
    db_alert.status = AlertStatus.RESOLVED
    db_alert.resolved_by = resolved_by
    db_alert.resolved_at = datetime.utcnow()
    if resolution_notes:
        db_alert.resolution_notes = resolution_notes
    
    db.commit()
    db.refresh(db_alert)
    
    # Publish to Redis
    status_data = {
        "type": "alert_resolved",
        "alert_id": db_alert.id,
        "auv_id": db_alert.auv_id,
        "resolved_by": resolved_by
    }
    redis_client.publish("alerts:resolved", str(status_data))
    
    return db_alert


# Bulk Operations
@router.post("/bulk/acknowledge")
def bulk_acknowledge_alerts(
    alert_ids: List[int],
    acknowledged_by: str = Query(..., description="User acknowledging the alerts"),
    db: Session = Depends(get_db)
):
    """Bulk acknowledge multiple alerts"""
    alerts = db.query(Alert).filter(Alert.id.in_(alert_ids)).all()
    
    if not alerts:
        raise HTTPException(status_code=404, detail="No alerts found")
    
    acknowledged_count = 0
    for alert in alerts:
        if alert.status != AlertStatus.ACKNOWLEDGED:
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.utcnow()
            acknowledged_count += 1
    
    db.commit()
    
    return {
        "message": f"Successfully acknowledged {acknowledged_count} alerts",
        "acknowledged_count": acknowledged_count,
        "total_alerts": len(alerts)
    }


@router.post("/bulk/resolve")
def bulk_resolve_alerts(
    alert_ids: List[int],
    resolved_by: str = Query(..., description="User resolving the alerts"),
    resolution_notes: Optional[str] = Query(None, description="Resolution notes"),
    db: Session = Depends(get_db)
):
    """Bulk resolve multiple alerts"""
    alerts = db.query(Alert).filter(Alert.id.in_(alert_ids)).all()
    
    if not alerts:
        raise HTTPException(status_code=404, detail="No alerts found")
    
    resolved_count = 0
    for alert in alerts:
        if alert.status != AlertStatus.RESOLVED:
            alert.status = AlertStatus.RESOLVED
            alert.resolved_by = resolved_by
            alert.resolved_at = datetime.utcnow()
            if resolution_notes:
                alert.resolution_notes = resolution_notes
            resolved_count += 1
    
    db.commit()
    
    return {
        "message": f"Successfully resolved {resolved_count} alerts",
        "resolved_count": resolved_count,
        "total_alerts": len(alerts)
    }


# Analytics Endpoints
@router.get("/analytics/trends")
def get_alert_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    auv_id: Optional[str] = Query(None),
    alert_type: Optional[AlertType] = Query(None),
    db: Session = Depends(get_db)
):
    """Get alert trends over time"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(
        func.date_trunc('day', Alert.timestamp).label('date'),
        func.count(Alert.id).label('count'),
        Alert.severity,
        Alert.alert_type
    ).filter(Alert.timestamp >= start_date)
    
    if auv_id:
        query = query.filter(Alert.auv_id == auv_id)
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    
    results = query.group_by(
        func.date_trunc('day', Alert.timestamp),
        Alert.severity,
        Alert.alert_type
    ).order_by(func.date_trunc('day', Alert.timestamp)).all()
    
    # Format results
    trends = {}
    for result in results:
        date_str = result.date.strftime('%Y-%m-%d')
        if date_str not in trends:
            trends[date_str] = {
                'date': date_str,
                'total_alerts': 0,
                'by_severity': {},
                'by_type': {}
            }
        
        trends[date_str]['total_alerts'] += result.count
        
        # By severity
        severity_key = result.severity.value
        if severity_key not in trends[date_str]['by_severity']:
            trends[date_str]['by_severity'][severity_key] = 0
        trends[date_str]['by_severity'][severity_key] += result.count
        
        # By type
        type_key = result.alert_type.value
        if type_key not in trends[date_str]['by_type']:
            trends[date_str]['by_type'][type_key] = 0
        trends[date_str]['by_type'][type_key] += result.count
    
    return {
        "period_days": days,
        "start_date": start_date.isoformat(),
        "end_date": datetime.utcnow().isoformat(),
        "trends": list(trends.values())
    }
