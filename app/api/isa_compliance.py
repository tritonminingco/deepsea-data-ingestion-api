from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models.isa_compliance import ISAStandard, ISAZone, ISACompliance, ComplianceStatus, ZoneType
from app.schemas.isa_compliance import (
    ISAStandardCreate, ISAStandardUpdate, ISAStandardResponse,
    ISAZoneCreate, ISAZoneUpdate, ISAZoneResponse,
    ISAComplianceCreate, ISAComplianceUpdate, ISAComplianceResponse,
    ComplianceSummary, ComplianceDashboard
)
from sqlalchemy import and_, or_, func, desc

router = APIRouter(prefix="/isa-compliance", tags=["ISA Compliance"])


# ISA Standards Endpoints
@router.post("/standards/", response_model=ISAStandardResponse)
def create_isa_standard(
    standard: ISAStandardCreate,
    db: Session = Depends(get_db)
):
    """Create a new ISA standard"""
    db_standard = ISAStandard(**standard.dict())
    db.add(db_standard)
    db.commit()
    db.refresh(db_standard)
    return db_standard


@router.get("/standards/", response_model=List[ISAStandardResponse])
def get_isa_standards(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all ISA standards with optional filtering"""
    query = db.query(ISAStandard)
    
    if category:
        query = query.filter(ISAStandard.category == category)
    
    standards = query.offset(skip).limit(limit).all()
    return standards


@router.get("/standards/{standard_id}", response_model=ISAStandardResponse)
def get_isa_standard(standard_id: int, db: Session = Depends(get_db)):
    """Get a specific ISA standard by ID"""
    standard = db.query(ISAStandard).filter(ISAStandard.id == standard_id).first()
    if not standard:
        raise HTTPException(status_code=404, detail="ISA Standard not found")
    return standard


@router.put("/standards/{standard_id}", response_model=ISAStandardResponse)
def update_isa_standard(
    standard_id: int,
    standard_update: ISAStandardUpdate,
    db: Session = Depends(get_db)
):
    """Update an ISA standard"""
    db_standard = db.query(ISAStandard).filter(ISAStandard.id == standard_id).first()
    if not db_standard:
        raise HTTPException(status_code=404, detail="ISA Standard not found")
    
    update_data = standard_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_standard, field, value)
    
    db.commit()
    db.refresh(db_standard)
    return db_standard


@router.delete("/standards/{standard_id}")
def delete_isa_standard(standard_id: int, db: Session = Depends(get_db)):
    """Delete an ISA standard"""
    db_standard = db.query(ISAStandard).filter(ISAStandard.id == standard_id).first()
    if not db_standard:
        raise HTTPException(status_code=404, detail="ISA Standard not found")
    
    db.delete(db_standard)
    db.commit()
    return {"message": "ISA Standard deleted successfully"}


# ISA Zones Endpoints
@router.post("/zones/", response_model=ISAZoneResponse)
def create_isa_zone(
    zone: ISAZoneCreate,
    db: Session = Depends(get_db)
):
    """Create a new ISA zone"""
    db_zone = ISAZone(**zone.dict())
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    return db_zone


@router.get("/zones/", response_model=List[ISAZoneResponse])
def get_isa_zones(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    zone_type: Optional[ZoneType] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all ISA zones with optional filtering"""
    query = db.query(ISAZone)
    
    if zone_type:
        query = query.filter(ISAZone.zone_type == zone_type)
    
    zones = query.offset(skip).limit(limit).all()
    return zones


@router.get("/zones/{zone_id}", response_model=ISAZoneResponse)
def get_isa_zone(zone_id: int, db: Session = Depends(get_db)):
    """Get a specific ISA zone by ID"""
    zone = db.query(ISAZone).filter(ISAZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="ISA Zone not found")
    return zone


@router.put("/zones/{zone_id}", response_model=ISAZoneResponse)
def update_isa_zone(
    zone_id: int,
    zone_update: ISAZoneUpdate,
    db: Session = Depends(get_db)
):
    """Update an ISA zone"""
    db_zone = db.query(ISAZone).filter(ISAZone.id == zone_id).first()
    if not db_zone:
        raise HTTPException(status_code=404, detail="ISA Zone not found")
    
    update_data = zone_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_zone, field, value)
    
    db.commit()
    db.refresh(db_zone)
    return db_zone


@router.delete("/zones/{zone_id}")
def delete_isa_zone(zone_id: int, db: Session = Depends(get_db)):
    """Delete an ISA zone"""
    db_zone = db.query(ISAZone).filter(ISAZone.id == zone_id).first()
    if not db_zone:
        raise HTTPException(status_code=404, detail="ISA Zone not found")
    
    db.delete(db_zone)
    db.commit()
    return {"message": "ISA Zone deleted successfully"}


# ISA Compliance Endpoints
@router.post("/compliance/", response_model=ISAComplianceResponse)
def create_isa_compliance(
    compliance: ISAComplianceCreate,
    db: Session = Depends(get_db)
):
    """Create a new ISA compliance record"""
    db_compliance = ISACompliance(**compliance.dict())
    db.add(db_compliance)
    db.commit()
    db.refresh(db_compliance)
    return db_compliance


@router.get("/compliance/", response_model=List[ISAComplianceResponse])
def get_isa_compliance(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auv_id: Optional[str] = Query(None),
    status: Optional[ComplianceStatus] = Query(None),
    standard_id: Optional[int] = Query(None),
    zone_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get ISA compliance records with filtering"""
    query = db.query(ISACompliance).options(
        joinedload(ISACompliance.standard),
        joinedload(ISACompliance.zone)
    )
    
    if auv_id:
        query = query.filter(ISACompliance.auv_id == auv_id)
    if status:
        query = query.filter(ISACompliance.status == status)
    if standard_id:
        query = query.filter(ISACompliance.standard_id == standard_id)
    if zone_id:
        query = query.filter(ISACompliance.zone_id == zone_id)
    
    compliance_records = query.offset(skip).limit(limit).all()
    return compliance_records


@router.get("/compliance/{compliance_id}", response_model=ISAComplianceResponse)
def get_isa_compliance_record(compliance_id: int, db: Session = Depends(get_db)):
    """Get a specific ISA compliance record by ID"""
    compliance = db.query(ISACompliance).options(
        joinedload(ISACompliance.standard),
        joinedload(ISACompliance.zone)
    ).filter(ISACompliance.id == compliance_id).first()
    
    if not compliance:
        raise HTTPException(status_code=404, detail="ISA Compliance record not found")
    return compliance


@router.put("/compliance/{compliance_id}", response_model=ISAComplianceResponse)
def update_isa_compliance(
    compliance_id: int,
    compliance_update: ISAComplianceUpdate,
    db: Session = Depends(get_db)
):
    """Update an ISA compliance record"""
    db_compliance = db.query(ISACompliance).filter(ISACompliance.id == compliance_id).first()
    if not db_compliance:
        raise HTTPException(status_code=404, detail="ISA Compliance record not found")
    
    update_data = compliance_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_compliance, field, value)
    
    db.commit()
    db.refresh(db_compliance)
    return db_compliance


@router.delete("/compliance/{compliance_id}")
def delete_isa_compliance(compliance_id: int, db: Session = Depends(get_db)):
    """Delete an ISA compliance record"""
    db_compliance = db.query(ISACompliance).filter(ISACompliance.id == compliance_id).first()
    if not db_compliance:
        raise HTTPException(status_code=404, detail="ISA Compliance record not found")
    
    db.delete(db_compliance)
    db.commit()
    return {"message": "ISA Compliance record deleted successfully"}


# Dashboard and Summary Endpoints
@router.get("/dashboard/summary", response_model=ComplianceSummary)
def get_compliance_summary(db: Session = Depends(get_db)):
    """Get compliance summary statistics"""
    # Get total AUV count (unique AUVs)
    total_auv_count = db.query(func.count(func.distinct(ISACompliance.auv_id))).scalar()
    
    # Get compliance counts
    compliant_count = db.query(func.count(ISACompliance.id)).filter(
        ISACompliance.status == ComplianceStatus.COMPLIANT
    ).scalar()
    
    non_compliant_count = db.query(func.count(ISACompliance.id)).filter(
        ISACompliance.status == ComplianceStatus.NON_COMPLIANT
    ).scalar()
    
    pending_count = db.query(func.count(ISACompliance.id)).filter(
        ISACompliance.status == ComplianceStatus.PENDING
    ).scalar()
    
    # Calculate overall compliance rate
    total_records = db.query(func.count(ISACompliance.id)).scalar()
    overall_compliance_rate = (compliant_count / total_records * 100) if total_records > 0 else 0
    
    # Get counts for other entities
    standards_count = db.query(func.count(ISAStandard.id)).scalar()
    zones_count = db.query(func.count(ISAZone.id)).scalar()
    active_violations_count = db.query(func.count(ISACompliance.id)).filter(
        ISACompliance.violations_count > 0
    ).scalar()
    
    return ComplianceSummary(
        total_auv_count=total_auv_count,
        compliant_auv_count=compliant_count,
        non_compliant_auv_count=non_compliant_count,
        pending_assessment_count=pending_count,
        overall_compliance_rate=overall_compliance_rate,
        standards_count=standards_count,
        zones_count=zones_count,
        active_violations_count=active_violations_count
    )


@router.get("/dashboard/", response_model=ComplianceDashboard)
def get_compliance_dashboard(db: Session = Depends(get_db)):
    """Get comprehensive compliance dashboard data"""
    # Get summary
    summary = get_compliance_summary(db)
    
    # Get recent compliance records
    recent_compliance = db.query(ISACompliance).options(
        joinedload(ISACompliance.standard),
        joinedload(ISACompliance.zone)
    ).order_by(desc(ISACompliance.updated_at)).limit(10).all()
    
    # Get upcoming assessments (next 7 days)
    next_week = datetime.utcnow() + timedelta(days=7)
    upcoming_assessments = db.query(ISACompliance).options(
        joinedload(ISACompliance.standard),
        joinedload(ISACompliance.zone)
    ).filter(
        ISACompliance.next_assessment <= next_week
    ).order_by(ISACompliance.next_assessment).limit(10).all()
    
    # Get all standards and zones
    standards = db.query(ISAStandard).all()
    zones = db.query(ISAZone).all()
    
    return ComplianceDashboard(
        summary=summary,
        recent_compliance_records=recent_compliance,
        upcoming_assessments=upcoming_assessments,
        standards=standards,
        zones=zones
    )


# AUV-specific compliance endpoints
@router.get("/auv/{auv_id}/compliance", response_model=List[ISAComplianceResponse])
def get_auv_compliance(
    auv_id: str,
    db: Session = Depends(get_db)
):
    """Get all compliance records for a specific AUV"""
    compliance_records = db.query(ISACompliance).options(
        joinedload(ISACompliance.standard),
        joinedload(ISACompliance.zone)
    ).filter(ISACompliance.auv_id == auv_id).all()
    
    return compliance_records


@router.get("/auv/{auv_id}/compliance/summary")
def get_auv_compliance_summary(auv_id: str, db: Session = Depends(get_db)):
    """Get compliance summary for a specific AUV"""
    total_records = db.query(func.count(ISACompliance.id)).filter(
        ISACompliance.auv_id == auv_id
    ).scalar()
    
    compliant_records = db.query(func.count(ISACompliance.id)).filter(
        and_(
            ISACompliance.auv_id == auv_id,
            ISACompliance.status == ComplianceStatus.COMPLIANT
        )
    ).scalar()
    
    avg_score = db.query(func.avg(ISACompliance.compliance_score)).filter(
        ISACompliance.auv_id == auv_id
    ).scalar() or 0
    
    total_violations = db.query(func.sum(ISACompliance.violations_count)).filter(
        ISACompliance.auv_id == auv_id
    ).scalar() or 0
    
    return {
        "auv_id": auv_id,
        "total_compliance_records": total_records,
        "compliant_records": compliant_records,
        "compliance_rate": (compliant_records / total_records * 100) if total_records > 0 else 0,
        "average_compliance_score": avg_score,
        "total_violations": total_violations
    }
