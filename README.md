# DeepSea Data Ingestion API

A comprehensive FastAPI-based data ingestion and management system for Autonomous Underwater Vehicle (AUV) operations, featuring real-time telemetry, ISA compliance tracking, and alert management.

## Features

### 🎯 ISA Compliance Data API (Top Priority)
- **ISA Standards Management**: CRUD operations for ISA standards with versioning and categorization
- **Zone Management**: Define and manage operational, restricted, and prohibited zones
- **Compliance Tracking**: Real-time compliance monitoring with scoring and violation tracking
- **Dashboard**: Comprehensive compliance dashboard with summary statistics
- **Reporting**: Automated compliance reporting and assessment scheduling

### 📡 Real-Time Telemetry API
- **WebSocket Support**: Real-time data streaming via WebSocket connections
- **AUV Data Ingestion**: Position, navigation, system status, and mission data
- **Environmental Data**: Water quality, salinity, pH, dissolved oxygen, and current data
- **Redis Integration**: Pub/sub messaging for real-time data distribution
- **Data Quality Monitoring**: Quality scoring and sensor status tracking

### 📊 Historical Data API
- **Time-Range Queries**: Flexible historical data retrieval with filtering
- **Pagination**: Efficient handling of large datasets
- **Aggregation**: Time-based data aggregation (1m, 5m, 15m, 1h, 1d intervals)
- **Multi-metric Support**: Aggregate multiple telemetry metrics simultaneously

### 🚨 Alert Feed Service
- **Multi-type Alerts**: Environmental, operational, compliance, system, and safety alerts
- **Severity Levels**: Low, medium, high, and critical alert classification
- **Status Management**: Active, acknowledged, resolved, and dismissed states
- **Real-time Notifications**: Redis-based real-time alert distribution
- **Bulk Operations**: Bulk acknowledge and resolve functionality
- **Analytics**: Alert trends and pattern analysis

## Tech Stack

- **Backend**: FastAPI (Python 3.8+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Real-time**: Redis for pub/sub messaging
- **Migrations**: Alembic for database schema management
- **Documentation**: Auto-generated OpenAPI/Swagger docs
- **Validation**: Pydantic for data validation and serialization

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Docker (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Data-ingestion
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=postgresql://user:password@localhost/deepsea_db
   REDIS_URL=redis://localhost:6379
   SECRET_KEY=your-secret-key-here
   ```

5. **Database Setup**
   ```bash
   # Create database
   createdb deepsea_db
   
   # Run migrations
   alembic upgrade head
   
   # Populate sample data
   python scripts/sample_data.py
   ```

6. **Start the API**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access Documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### ISA Compliance API

#### Standards Management
```http
POST   /api/v1/isa-compliance/standards/          # Create standard
GET    /api/v1/isa-compliance/standards/          # List standards
GET    /api/v1/isa-compliance/standards/{id}      # Get standard
PUT    /api/v1/isa-compliance/standards/{id}      # Update standard
DELETE /api/v1/isa-compliance/standards/{id}      # Delete standard
```

#### Zones Management
```http
POST   /api/v1/isa-compliance/zones/              # Create zone
GET    /api/v1/isa-compliance/zones/              # List zones
GET    /api/v1/isa-compliance/zones/{id}          # Get zone
PUT    /api/v1/isa-compliance/zones/{id}          # Update zone
DELETE /api/v1/isa-compliance/zones/{id}          # Delete zone
```

#### Compliance Tracking
```http
POST   /api/v1/isa-compliance/compliance/         # Create compliance record
GET    /api/v1/isa-compliance/compliance/         # List compliance records
GET    /api/v1/isa-compliance/compliance/{id}     # Get compliance record
PUT    /api/v1/isa-compliance/compliance/{id}     # Update compliance record
DELETE /api/v1/isa-compliance/compliance/{id}     # Delete compliance record
```

#### Dashboard
```http
GET    /api/v1/isa-compliance/dashboard/summary   # Compliance summary
GET    /api/v1/isa-compliance/dashboard/          # Full dashboard
GET    /api/v1/isa-compliance/auv/{auv_id}/compliance  # AUV compliance
```

### Telemetry API

#### Real-time Data
```http
POST   /api/v1/telemetry/realtime/auv-data        # Ingest AUV data
POST   /api/v1/telemetry/realtime/environmental   # Ingest environmental data
WS     /api/v1/telemetry/ws/{auv_id}              # WebSocket connection
```

#### Historical Data
```http
GET    /api/v1/telemetry/historical/auv-data      # Historical AUV data
GET    /api/v1/telemetry/historical/environmental # Historical environmental data
POST   /api/v1/telemetry/aggregation/auv-data     # AUV data aggregation
POST   /api/v1/telemetry/aggregation/environmental # Environmental aggregation
```

#### AUV Status
```http
GET    /api/v1/telemetry/auv/{auv_id}/latest      # Latest AUV data
GET    /api/v1/telemetry/auv/{auv_id}/status      # AUV status
GET    /api/v1/telemetry/quality/auv/{auv_id}     # Data quality metrics
```

### Alerts API

#### Alert Management
```http
POST   /api/v1/alerts/                            # Create alert
GET    /api/v1/alerts/                            # List alerts
GET    /api/v1/alerts/{id}                        # Get alert
PUT    /api/v1/alerts/{id}                        # Update alert
DELETE /api/v1/alerts/{id}                        # Delete alert
```

#### Alert Feed
```http
GET    /api/v1/alerts/feed/                       # Alert feed with summary
GET    /api/v1/alerts/summary/                    # Alert summary
GET    /api/v1/alerts/auv/{auv_id}/               # AUV alerts
GET    /api/v1/alerts/auv/{auv_id}/active         # Active AUV alerts
```

#### Alert Actions
```http
POST   /api/v1/alerts/{id}/acknowledge            # Acknowledge alert
POST   /api/v1/alerts/{id}/resolve                # Resolve alert
POST   /api/v1/alerts/bulk/acknowledge            # Bulk acknowledge
POST   /api/v1/alerts/bulk/resolve                # Bulk resolve
```

#### Analytics
```http
GET    /api/v1/alerts/analytics/trends            # Alert trends
```

## Usage Examples

### Creating ISA Compliance Data

```python
import requests
import json

# Create ISA Standard
standard_data = {
    "standard_code": "ISA-004",
    "standard_name": "Data Security Standards",
    "description": "Standards for secure data transmission and storage",
    "version": "1.0",
    "effective_date": "2024-01-01T00:00:00Z",
    "category": "security",
    "requirements": "All data must be encrypted in transit and at rest"
}

response = requests.post(
    "http://localhost:8000/api/v1/isa-compliance/standards/",
    json=standard_data
)
print(response.json())

# Create Compliance Record
compliance_data = {
    "auv_id": "AUV-001",
    "standard_id": 1,
    "zone_id": 1,
    "status": "compliant",
    "compliance_score": 95.5,
    "violations_count": 0
}

response = requests.post(
    "http://localhost:8000/api/v1/isa-compliance/compliance/",
    json=compliance_data
)
print(response.json())
```

### Real-time Telemetry Ingestion

```python
import requests
import json
from datetime import datetime

# Ingest AUV Data
auv_data = {
    "auv_id": "AUV-001",
    "timestamp": datetime.utcnow().isoformat(),
    "latitude": 37.7749,
    "longitude": -122.4194,
    "depth": 150.5,
    "battery_level": 85.2,
    "system_status": "operational",
    "mission_id": "MISSION-2024-001",
    "mission_phase": "data_collection"
}

response = requests.post(
    "http://localhost:8000/api/v1/telemetry/realtime/auv-data",
    json=auv_data
)
print(response.json())

# Ingest Environmental Data
env_data = {
    "auv_id": "AUV-001",
    "timestamp": datetime.utcnow().isoformat(),
    "water_temperature": 15.2,
    "salinity": 34.1,
    "ph_level": 8.1,
    "dissolved_oxygen": 7.8,
    "data_quality_score": 92.5
}

response = requests.post(
    "http://localhost:8000/api/v1/telemetry/realtime/environmental",
    json=env_data
)
print(response.json())
```

### WebSocket Real-time Subscription

```javascript
// JavaScript WebSocket client
const ws = new WebSocket('ws://localhost:8000/api/v1/telemetry/ws/AUV-001');

ws.onopen = function(event) {
    console.log('Connected to real-time telemetry feed');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received telemetry data:', data);
    
    // Handle different data types
    if (data.type === 'auv_data') {
        updateAUVDisplay(data.data);
    } else if (data.type === 'environmental') {
        updateEnvironmentalDisplay(data.data);
    }
};

ws.onclose = function(event) {
    console.log('Disconnected from telemetry feed');
};
```

### Alert Management

```python
import requests

# Create Alert
alert_data = {
    "auv_id": "AUV-001",
    "alert_type": "operational",
    "severity": "high",
    "title": "Low Battery Warning",
    "description": "Battery level below 20%",
    "message": "AUV-001 battery level is at 18%. Consider returning to base.",
    "source": "system",
    "location": "Lat: 37.7749, Lon: -122.4194",
    "timestamp": "2024-01-01T12:00:00Z"
}

response = requests.post(
    "http://localhost:8000/api/v1/alerts/",
    json=alert_data
)
print(response.json())

# Acknowledge Alert
response = requests.post(
    f"http://localhost:8000/api/v1/alerts/{alert_id}/acknowledge",
    params={"acknowledged_by": "operator"}
)
print(response.json())
```

## Database Schema

### ISA Compliance Tables

- **isa_standards**: ISA standards with versioning and categorization
- **isa_zones**: Operational zones with coordinates and restrictions
- **isa_compliance**: Compliance records linking AUVs to standards and zones

### Telemetry Tables

- **auv_data**: AUV position, navigation, and system data
- **telemetry_data**: Environmental sensor readings

### Alert Tables

- **alerts**: Alert records with status tracking and resolution

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:password@localhost/deepsea_db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `SECRET_KEY` | Application secret key | `your-secret-key-here` |
| `API_V1_STR` | API version prefix | `/api/v1` |
| `ISA_ZONE_TIMEOUT_MINUTES` | Zone timeout duration | `30` |
| `ISA_REPORTING_INTERVAL_HOURS` | Reporting interval | `24` |

### Database Configuration

The system uses PostgreSQL with the following recommended settings:

```sql
-- Recommended PostgreSQL settings
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Code Quality

```bash
# Install development dependencies
pip install black flake8 mypy

# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations

1. **Security**: Configure proper CORS settings and authentication
2. **Performance**: Use connection pooling and caching
3. **Monitoring**: Implement health checks and logging
4. **Backup**: Regular database backups and data retention policies
5. **Scaling**: Consider horizontal scaling with load balancers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the API documentation at `/docs`

## Roadmap

- [ ] Authentication and authorization
- [ ] Advanced analytics and reporting
- [ ] Machine learning integration for anomaly detection
- [ ] Mobile application support
- [ ] Integration with external marine monitoring systems
- [ ] Advanced visualization and dashboard features
