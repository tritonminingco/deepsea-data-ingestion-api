#!/usr/bin/env python3
"""
Startup script for DeepSea Data Ingestion API
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import redis
        print("✓ All Python dependencies are installed")
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    return True

def check_database():
    """Check if database is accessible"""
    print("Checking database connection...")
    
    try:
        from app.database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("Please ensure PostgreSQL is running and DATABASE_URL is correct")
        return False

def check_redis():
    """Check if Redis is accessible"""
    print("Checking Redis connection...")
    
    try:
        from app.config import settings
        import redis
        r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        r.ping()
        print("✓ Redis connection successful")
        return True
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        print("Please ensure Redis is running and REDIS_URL is correct")
        return False

def run_migrations():
    """Run database migrations"""
    print("Running database migrations...")
    
    try:
        result = subprocess.run(["alembic", "upgrade", "head"], 
                              capture_output=True, text=True, check=True)
        print("✓ Database migrations completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Migration failed: {e.stderr}")
        return False

def create_sample_data():
    """Create sample data if database is empty"""
    print("Checking for sample data...")
    
    try:
        from app.database import SessionLocal
        from app.models.isa_compliance import ISAStandard
        
        db = SessionLocal()
        count = db.query(ISAStandard).count()
        db.close()
        
        if count == 0:
            print("Creating sample data...")
            subprocess.run([sys.executable, "scripts/sample_data.py"], check=True)
            print("✓ Sample data created")
        else:
            print("✓ Sample data already exists")
        return True
    except Exception as e:
        print(f"✗ Sample data creation failed: {e}")
        return False

def start_server():
    """Start the FastAPI server"""
    print("Starting DeepSea Data Ingestion API...")
    print("API will be available at: http://localhost:8000")
    print("Documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([
            "uvicorn", "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\nServer stopped")

def wait_for_services():
    """Wait for external services to be ready"""
    print("Waiting for services to be ready...")
    
    # Wait for database
    max_attempts = 30
    for attempt in range(max_attempts):
        if check_database():
            break
        print(f"Waiting for database... ({attempt + 1}/{max_attempts})")
        time.sleep(2)
    else:
        print("Database not available after maximum attempts")
        return False
    
    # Wait for Redis
    for attempt in range(max_attempts):
        if check_redis():
            break
        print(f"Waiting for Redis... ({attempt + 1}/{max_attempts})")
        time.sleep(2)
    else:
        print("Redis not available after maximum attempts")
        return False
    
    return True

def main():
    """Main startup function"""
    print("=" * 50)
    print("DeepSea Data Ingestion API Startup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app").exists():
        print("✗ Please run this script from the Data-ingestion directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Wait for services
    if not wait_for_services():
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        sys.exit(1)
    
    # Create sample data
    if not create_sample_data():
        sys.exit(1)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
