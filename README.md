# Deployment Guide

## Quick Start (Local Development)

### Prerequisites
- Python 3.9-3.12 (NOT 3.14 - LangGraph doesn't support it yet)
- Node.js 18+
- OpenAI API Key

### Step 1: Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-api-key-here"

# Initialize database
python -c "from models.database import init_db, seed_data; init_db(); seed_data()"

# Start backend server
uvicorn main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000
API Docs: http://localhost:8000/docs

### Step 2: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:3000

### Step 3: Verify Installation

1. Open http://localhost:3000
2. Login with any credentials (mock auth)
3. Navigate to Dashboard
4. Click "Leads" to see sample data
5. Click "Qualify" on any lead to trigger AI workflow
6. Check http://localhost:8000/docs for API testing

## Production Deployment

### Option 1: Docker Deployment (Recommended)

#### Create Dockerfile for Backend

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Create Dockerfile for Frontend

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

#### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=sqlite:///data/lead_qualification.db
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped
```

#### Deploy with Docker

```bash
# Build and start
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option 2: Cloud Deployment

#### Deploy to Railway/Render (Backend)

1. Push code to GitHub
2. Connect Railway/Render to repository
3. Set environment variables:
   - `OPENAI_API_KEY`
   - `DATABASE_URL` (if using PostgreSQL)
4. Deploy

#### Deploy to Vercel (Frontend)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod
```

### Option 3: AWS Deployment

#### Backend on AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
cd backend
eb init -p python-3.11 lead-qualification-api

# Deploy
eb create lead-qualification-env
```

#### Frontend on AWS S3 + CloudFront

```bash
# Build
cd frontend
npm run build

# Upload to S3
aws s3 sync out/ s3://your-bucket-name --delete

# Invalidate CloudFront
aws cloudfront create-invalidation --distribution-id YOUR_ID --paths "/*"
```

## Environment Variables

### Backend (.env)

```env
# Required
OPENAI_API_KEY=sk-...

# Optional
DATABASE_URL=sqlite:///data/lead_qualification.db
DEBUG=false
LOG_LEVEL=INFO

# For production
CORS_ORIGINS=https://yourdomain.com
MAX_WORKERS=4
```

### Frontend (.env.local)

```env
# Required
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional
NEXT_PUBLIC_APP_NAME=Lead Qualification System
```

## Database Migration (Production)

### SQLite to PostgreSQL

```python
# migration_script.py
import sqlite3
import psycopg2

def migrate_sqlite_to_postgres():
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('lead_qualification.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to PostgreSQL
    pg_conn = psycopg2.connect(
        host="your-host",
        database="your-db",
        user="your-user",
        password="your-password"
    )
    pg_cursor = pg_conn.cursor()
    
    # Migrate each table
    # ... migration logic ...
    
    pg_conn.commit()
    pg_conn.close()
    sqlite_conn.close()
```

## Monitoring & Observability

### Setup LangSmith (Optional)

```python
# Add to backend
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "your-langsmith-key"
os.environ["LANGCHAIN_PROJECT"] = "lead-qualification"
```

### Health Check Endpoint

```bash
# Check if API is healthy
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "database": "connected"}
```

## Scaling Considerations

### Current MVP Limitations
- SQLite (single-file database)
- In-memory checkpointing
- Single worker process
- No queue system

### Production Improvements

1. **Database**: Switch to PostgreSQL
   ```python
   # SQLAlchemy PostgreSQL connection
   DATABASE_URL = "postgresql://user:pass@localhost/dbname"
   ```

2. **Task Queue**: Add Celery + Redis
   ```python
   # For background workflow execution
   from celery import Celery
   
   app = Celery('tasks', broker='redis://localhost:6379/0')
   
   @app.task
   def run_qualification_async(lead_id):
       # Run workflow in background
       pass
   ```

3. **Caching**: Add Redis for lead data
   ```python
   import redis
   
   cache = redis.Redis(host='localhost', port=6379)
   
   # Cache lead data
   cache.setex(f"lead:{lead_id}", 3600, lead_json)
   ```

4. **Load Balancing**: Deploy multiple FastAPI instances
   - Use Gunicorn with Uvicorn workers
   - Add NGINX as reverse proxy

## Security Checklist

- [ ] Use HTTPS in production
- [ ] Store secrets in environment variables
- [ ] Add rate limiting to API
- [ ] Validate all user inputs (Pydantic)
- [ ] Add authentication (JWT/OAuth2)
- [ ] Sanitize database queries (SQL injection prevention)
- [ ] Add CORS restrictions
- [ ] Enable audit logging
- [ ] Regular dependency updates

## Backup Strategy

### SQLite Backup

```bash
# Automated daily backup
0 0 * * * cp /path/to/lead_qualification.db /backups/lead_qualification_$(date +\%Y\%m\%d).db

# Restore
sqlite3 lead_qualification.db ".restore /backups/lead_qualification_20240101.db"
```

### PostgreSQL Backup

```bash
# Backup
pg_dump -h localhost -U user lead_qualification > backup.sql

# Restore
psql -h localhost -U user lead_qualification < backup.sql
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Find and kill process
   lsof -ti:8000 | xargs kill -9
   ```

2. **Module not found**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   ```

3. **CORS errors**
   - Check CORS_ORIGINS environment variable
   - Ensure frontend URL is in allowed origins

4. **OpenAI API errors**
   - Verify OPENAI_API_KEY is set
   - Check API rate limits
   - Enable retry logic (already implemented)

### Debug Mode

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug
uvicorn main:app --reload --log-level debug
```

## Performance Tuning

### Database Optimization
- Add indexes on frequently queried columns
- Use connection pooling
- Implement query caching

### API Optimization
- Enable response compression
- Use async database drivers
- Implement pagination

### LLM Optimization
- Use batch processing
- Implement response caching
- Use cheaper models for simple tasks

## Maintenance

### Regular Tasks
- Daily: Database backups
- Weekly: Dependency updates check
- Monthly: Performance review
- Quarterly: Security audit

### Log Rotation
```bash
# Setup logrotate
/var/log/lead-qualification/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```
