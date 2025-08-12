#!/usr/bin/env python3
"""
Simple API test script for DeepSea Data Ingestion API
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get("http://localhost:8000/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_isa_compliance():
    """Test ISA compliance endpoints"""
    print("\nTesting ISA compliance endpoints...")
    
    # Test standards endpoint
    response = requests.get(f"{BASE_URL}/isa-compliance/standards/")
    print(f"Standards endpoint: {response.status_code}")
    if response.status_code == 200:
        standards = response.json()
        print(f"Found {len(standards)} standards")
    
    # Test zones endpoint
    response = requests.get(f"{BASE_URL}/isa-compliance/zones/")
    print(f"Zones endpoint: {response.status_code}")
    if response.status_code == 200:
        zones = response.json()
        print(f"Found {len(zones)} zones")
    
    # Test compliance endpoint
    response = requests.get(f"{BASE_URL}/isa-compliance/compliance/")
    print(f"Compliance endpoint: {response.status_code}")
    if response.status_code == 200:
        compliance = response.json()
        print(f"Found {len(compliance)} compliance records")
    
    # Test dashboard
    response = requests.get(f"{BASE_URL}/isa-compliance/dashboard/summary")
    print(f"Dashboard summary: {response.status_code}")
    if response.status_code == 200:
        summary = response.json()
        print(f"Dashboard: {summary}")
    
    return True

def test_telemetry():
    """Test telemetry endpoints"""
    print("\nTesting telemetry endpoints...")
    
    # Test historical AUV data
    response = requests.get(f"{BASE_URL}/telemetry/historical/auv-data?limit=5")
    print(f"Historical AUV data: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} AUV data records")
    
    # Test historical environmental data
    response = requests.get(f"{BASE_URL}/telemetry/historical/environmental?limit=5")
    print(f"Historical environmental data: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} environmental data records")
    
    # Test AUV status
    response = requests.get(f"{BASE_URL}/telemetry/auv/AUV-001/status")
    print(f"AUV status: {response.status_code}")
    if response.status_code == 200:
        status = response.json()
        print(f"AUV status: {status}")
    
    return True

def test_alerts():
    """Test alerts endpoints"""
    print("\nTesting alerts endpoints...")
    
    # Test alerts endpoint
    response = requests.get(f"{BASE_URL}/alerts/?limit=5")
    print(f"Alerts endpoint: {response.status_code}")
    if response.status_code == 200:
        alerts = response.json()
        print(f"Found {len(alerts)} alerts")
    
    # Test alert summary
    response = requests.get(f"{BASE_URL}/alerts/summary/")
    print(f"Alert summary: {response.status_code}")
    if response.status_code == 200:
        summary = response.json()
        print(f"Alert summary: {summary}")
    
    # Test alert feed
    response = requests.get(f"{BASE_URL}/alerts/feed/?limit=3")
    print(f"Alert feed: {response.status_code}")
    if response.status_code == 200:
        feed = response.json()
        print(f"Alert feed: {feed['total_count']} total alerts")
    
    return True

def test_real_time_ingestion():
    """Test real-time data ingestion"""
    print("\nTesting real-time data ingestion...")
    
    # Test AUV data ingestion
    auv_data = {
        "auv_id": "TEST-AUV-001",
        "timestamp": datetime.utcnow().isoformat(),
        "latitude": 37.7749,
        "longitude": -122.4194,
        "depth": 150.5,
        "battery_level": 85.2,
        "system_status": "operational",
        "mission_id": "TEST-MISSION-001",
        "mission_phase": "testing"
    }
    
    response = requests.post(f"{BASE_URL}/telemetry/realtime/auv-data", json=auv_data)
    print(f"AUV data ingestion: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Ingested AUV data: {result['id']}")
    
    # Test environmental data ingestion
    env_data = {
        "auv_id": "TEST-AUV-001",
        "timestamp": datetime.utcnow().isoformat(),
        "water_temperature": 15.2,
        "salinity": 34.1,
        "ph_level": 8.1,
        "dissolved_oxygen": 7.8,
        "data_quality_score": 92.5
    }
    
    response = requests.post(f"{BASE_URL}/telemetry/realtime/environmental", json=env_data)
    print(f"Environmental data ingestion: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Ingested environmental data: {result['id']}")
    
    return True

def test_alert_creation():
    """Test alert creation"""
    print("\nTesting alert creation...")
    
    alert_data = {
        "auv_id": "TEST-AUV-001",
        "alert_type": "operational",
        "severity": "medium",
        "title": "Test Alert",
        "description": "This is a test alert for API testing",
        "message": "Test alert message with details",
        "source": "test",
        "location": "Test location",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    response = requests.post(f"{BASE_URL}/alerts/", json=alert_data)
    print(f"Alert creation: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Created alert: {result['id']}")
        return result['id']
    
    return None

def main():
    """Run all tests"""
    print("=" * 50)
    print("DeepSea Data Ingestion API Test")
    print("=" * 50)
    
    try:
        # Test health
        if not test_health():
            print("Health check failed!")
            return
        
        # Test ISA compliance
        test_isa_compliance()
        
        # Test telemetry
        test_telemetry()
        
        # Test alerts
        test_alerts()
        
        # Test real-time ingestion
        test_real_time_ingestion()
        
        # Test alert creation
        alert_id = test_alert_creation()
        
        print("\n" + "=" * 50)
        print("API Test Completed Successfully!")
        print("=" * 50)
        print("You can now:")
        print("- View API documentation at: http://localhost:8000/docs")
        print("- Access the dashboard at: http://localhost:8000/api/v1/isa-compliance/dashboard/")
        print("- Test WebSocket connections for real-time data")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Please ensure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    main()
