#!/usr/bin/env python3
"""
Sample data population script for DeepSea Data Ingestion API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.isa_compliance import ISAStandard, ISAZone, ISACompliance, ComplianceStatus, ZoneType
from app.models.telemetry import AUVData, TelemetryData
from app.models.alerts import Alert, AlertSeverity, AlertType, AlertStatus

def create_sample_data():
    """Create sample data for the DeepSea API"""
    db = SessionLocal()
    
    try:
        # Create ISA Standards
        print("Creating ISA Standards...")
        standards = [
            ISAStandard(
                standard_code="ISA-001",
                standard_name="AUV Safety Standards",
                description="Comprehensive safety standards for autonomous underwater vehicles",
                version="2.1",
                effective_date=datetime(2023, 1, 1),
                category="safety",
                requirements="All AUVs must have emergency surfacing capability and collision avoidance systems"
            ),
            ISAStandard(
                standard_code="ISA-002",
                standard_name="Environmental Protection Standards",
                description="Standards for environmental protection during AUV operations",
                version="1.5",
                effective_date=datetime(2023, 3, 15),
                category="environmental",
                requirements="AUVs must not disturb marine life and must avoid sensitive habitats"
            ),
            ISAStandard(
                standard_code="ISA-003",
                standard_name="Operational Standards",
                description="Operational standards for AUV missions and data collection",
                version="1.8",
                effective_date=datetime(2023, 6, 1),
                category="operational",
                requirements="All missions must have backup communication systems and data redundancy"
            )
        ]
        
        for standard in standards:
            db.add(standard)
        db.commit()
        
        # Create ISA Zones
        print("Creating ISA Zones...")
        zones = [
            ISAZone(
                zone_name="Pacific Research Zone",
                zone_type=ZoneType.OPERATIONAL,
                coordinates='{"type": "Polygon", "coordinates": [[[-122.5, 37.5], [-122.0, 37.5], [-122.0, 38.0], [-122.5, 38.0], [-122.5, 37.5]]]}',
                depth_range_min=0,
                depth_range_max=1000,
                area_km2=2500.0,
                description="Designated research zone in the Pacific Ocean",
                restrictions="Speed limit 5 knots, no fishing activities"
            ),
            ISAZone(
                zone_name="Marine Sanctuary",
                zone_type=ZoneType.RESTRICTED,
                coordinates='{"type": "Polygon", "coordinates": [[[-123.0, 36.0], [-122.5, 36.0], [-122.5, 36.5], [-123.0, 36.5], [-123.0, 36.0]]]}',
                depth_range_min=0,
                depth_range_max=500,
                area_km2=1200.0,
                description="Protected marine sanctuary area",
                restrictions="No AUV operations without special permit"
            ),
            ISAZone(
                zone_name="Deep Sea Exploration Zone",
                zone_type=ZoneType.OPERATIONAL,
                coordinates='{"type": "Polygon", "coordinates": [[[-124.0, 35.0], [-123.5, 35.0], [-123.5, 35.5], [-124.0, 35.5], [-124.0, 35.0]]]}',
                depth_range_min=1000,
                depth_range_max=4000,
                area_km2=5000.0,
                description="Deep sea exploration and research zone",
                restrictions="Advanced safety protocols required"
            )
        ]
        
        for zone in zones:
            db.add(zone)
        db.commit()
        
        # Create sample AUVs and their data
        auv_ids = ["AUV-001", "AUV-002", "AUV-003", "AUV-004", "AUV-005"]
        
        # Create ISA Compliance records
        print("Creating ISA Compliance records...")
        for auv_id in auv_ids:
            for standard in standards:
                compliance = ISACompliance(
                    auv_id=auv_id,
                    standard_id=standard.id,
                    zone_id=random.choice(zones).id if random.random() > 0.3 else None,
                    status=random.choice(list(ComplianceStatus)),
                    compliance_score=random.uniform(75.0, 100.0),
                    last_assessment=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                    next_assessment=datetime.utcnow() + timedelta(days=random.randint(30, 90)),
                    zone_entry_time=datetime.utcnow() - timedelta(hours=random.randint(1, 24)) if random.random() > 0.5 else None,
                    zone_exit_time=datetime.utcnow() - timedelta(hours=random.randint(1, 12)) if random.random() > 0.5 else None,
                    zone_duration_minutes=random.randint(30, 480),
                    violations_count=random.randint(0, 3),
                    violations_description="Minor protocol deviation" if random.random() > 0.7 else None,
                    corrective_actions="Updated operational procedures" if random.random() > 0.8 else None,
                    notes="Regular compliance check completed"
                )
                db.add(compliance)
        
        # Create telemetry data
        print("Creating telemetry data...")
        for auv_id in auv_ids:
            # Create AUV data for the last 24 hours
            for i in range(24):
                timestamp = datetime.utcnow() - timedelta(hours=i)
                auv_data = AUVData(
                    auv_id=auv_id,
                    timestamp=timestamp,
                    latitude=37.5 + random.uniform(-0.1, 0.1),
                    longitude=-122.5 + random.uniform(-0.1, 0.1),
                    depth=random.uniform(10, 200),
                    altitude=random.uniform(5, 50),
                    heading=random.uniform(0, 360),
                    speed=random.uniform(1, 8),
                    battery_level=random.uniform(20, 95),
                    temperature=random.uniform(15, 25),
                    pressure=random.uniform(1, 20),
                    system_status=random.choice(["operational", "maintenance", "warning"]),
                    mission_id=f"MISSION-{auv_id}-{timestamp.strftime('%Y%m%d')}",
                    mission_phase=random.choice(["survey", "data_collection", "transit", "docking"])
                )
                db.add(auv_data)
                
                # Create environmental data
                env_data = TelemetryData(
                    auv_id=auv_id,
                    timestamp=timestamp,
                    water_temperature=random.uniform(12, 18),
                    salinity=random.uniform(33, 35),
                    ph_level=random.uniform(7.8, 8.2),
                    dissolved_oxygen=random.uniform(6, 9),
                    turbidity=random.uniform(0.1, 2.0),
                    current_speed=random.uniform(0.1, 1.5),
                    current_direction=random.uniform(0, 360),
                    data_quality_score=random.uniform(85, 100),
                    sensor_status="operational"
                )
                db.add(env_data)
        
        # Create alerts
        print("Creating alerts...")
        alert_titles = [
            "Low Battery Warning",
            "Environmental Anomaly Detected",
            "Communication Loss",
            "Depth Limit Exceeded",
            "Sensor Calibration Required",
            "Zone Boundary Approach",
            "System Temperature High",
            "Data Quality Degradation"
        ]
        
        for auv_id in auv_ids:
            for i in range(random.randint(2, 5)):
                alert = Alert(
                    auv_id=auv_id,
                    alert_type=random.choice(list(AlertType)),
                    severity=random.choice(list(AlertSeverity)),
                    status=random.choice(list(AlertStatus)),
                    title=random.choice(alert_titles),
                    description=f"Alert for {auv_id}: {random.choice(alert_titles)}",
                    message=f"Detailed message for {auv_id} alert",
                    source=random.choice(["sensor", "system", "manual"]),
                    location=f"Lat: {37.5 + random.uniform(-0.1, 0.1)}, Lon: {-122.5 + random.uniform(-0.1, 0.1)}",
                    timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 72)),
                    acknowledged_by="operator" if random.random() > 0.5 else None,
                    acknowledged_at=datetime.utcnow() - timedelta(hours=random.randint(1, 24)) if random.random() > 0.5 else None,
                    resolved_by="technician" if random.random() > 0.7 else None,
                    resolved_at=datetime.utcnow() - timedelta(hours=random.randint(1, 12)) if random.random() > 0.7 else None
                )
                db.add(alert)
        
        db.commit()
        print("Sample data created successfully!")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
