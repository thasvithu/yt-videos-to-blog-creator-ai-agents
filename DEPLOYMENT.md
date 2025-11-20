# 🚀 Deployment Guide

## Deployment Options

This application can be deployed to various platforms. Below are recommended approaches for different use cases.

---

## Option 1: Google Cloud Run (Recommended for Resume)

**Pros**: Serverless, auto-scaling, free tier available, easy setup
**Cons**: Requires cloud setup

### Prerequisites
- Google Cloud account
- gcloud CLI installed
- Docker Hub account

### Steps

1. **Build and push Docker images**

```bash
# Backend
cd backend
docker build -t gcr.io/YOUR_PROJECT_ID/ytblog-backend:latest .
docker push gcr.io/YOUR_PROJECT_ID/ytblog-backend:latest

# Frontend (optional - can use Vercel instead)
cd ../frontend
docker build -t gcr.io/YOUR_PROJECT_ID/ytblog-frontend:latest .
docker push gcr.io/YOUR_PROJECT_ID/ytblog-frontend:latest
```

2. **Deploy PostgreSQL**

```bash
# Create Cloud SQL instance
gcloud sql instances create ytblog-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create ytblog --instance=ytblog-db
```

3. **Deploy Redis**

```bash
# Create Memorystore Redis instance
gcloud redis instances create ytblog-redis \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_7_0
```

4. **Deploy Backend API**

```bash
gcloud run deploy ytblog-api \
  --image gcr.io/YOUR_PROJECT_ID/ytblog-backend:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "OPENAI_API_KEY=sk-xxx,DATABASE_URL=postgresql://...,REDIS_URL=redis://..."
```

5. **Deploy Frontend** (Alternative: Use Vercel)

```bash
gcloud run deploy ytblog-frontend \
  --image gcr.io/YOUR_PROJECT_ID/ytblog-frontend:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated
```

---

## Option 2: Vercel (Frontend) + Render (Backend)

**Pros**: Free tiers, easy setup, automatic deployments
**Cons**: Separate services to manage

### Frontend (Vercel)

1. **Connect GitHub repository**
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Set root directory to `frontend/`

2. **Configure build settings**
   ```
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

3. **Set environment variable**
   ```
   VITE_API_URL=https://your-backend.onrender.com
   ```

### Backend (Render)

1. **Create Web Service**
   - Go to [render.com](https://render.com)
   - New → Web Service
   - Connect GitHub repository

2. **Configure service**
   ```
   Name: ytblog-backend
   Root Directory: backend/
   Environment: Docker
   ```

3. **Add PostgreSQL database**
   - New → PostgreSQL
   - Copy connection string

4. **Add Redis**
   - New → Redis
   - Copy connection string

5. **Set environment variables**
   ```
   OPENAI_API_KEY=sk-xxx
   DATABASE_URL=postgresql://...
   REDIS_URL=redis://...
   YOUTUBE_API_KEY=xxx
   SENDGRID_API_KEY=xxx
   ```

6. **Deploy Celery worker**
   - New → Background Worker
   - Start Command: `celery -A app.workers.celery_app worker --loglevel=info`

---

## Option 3: AWS ECS (Production)

**Pros**: Full control, scalable, production-grade
**Cons**: More complex setup, costs

### Prerequisites
- AWS account
- AWS CLI configured
- ECR repository created

### Steps

1. **Push images to ECR**

```bash
# Authenticate
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag ytblog-backend YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/ytblog-backend:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/ytblog-backend:latest
```

2. **Create RDS PostgreSQL instance**

```bash
aws rds create-db-instance \
  --db-instance-identifier ytblog-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YOUR_PASSWORD \
  --allocated-storage 20
```

3. **Create ElastiCache Redis**

```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id ytblog-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

4. **Create ECS task definition**

```json
{
  "family": "ytblog",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/ytblog-backend:latest",
      "portMappings": [{"containerPort": 8000}],
      "environment": [
        {"name": "OPENAI_API_KEY", "value": "sk-xxx"},
        {"name": "DATABASE_URL", "value": "postgresql://..."},
        {"name": "REDIS_URL", "value": "redis://..."}
      ]
    }
  ]
}
```

5. **Create ECS service with ALB**

```bash
aws ecs create-service \
  --cluster ytblog-cluster \
  --service-name ytblog-api \
  --task-definition ytblog \
  --desired-count 2 \
  --load-balancer targetGroupArn=arn:aws:...,containerName=backend,containerPort=8000
```

---

## Option 4: DigitalOcean App Platform

**Pros**: Simple, affordable, managed
**Cons**: Less control than AWS

### Steps

1. **Create App**
   - Go to [DigitalOcean](https://www.digitalocean.com)
   - Apps → Create App
   - Connect GitHub repository

2. **Configure services**
   ```
   Backend:
     - Type: Web Service
     - Dockerfile: backend/Dockerfile
     - HTTP Port: 8000
   
   Worker:
     - Type: Worker
     - Dockerfile: backend/Dockerfile
     - Run Command: celery -A app.workers.celery_app worker
   
   Frontend:
     - Type: Static Site
     - Build Command: npm run build
     - Output Directory: dist
   ```

3. **Add databases**
   - PostgreSQL database
   - Redis database

4. **Set environment variables**

---

## Environment Variables for Production

### Required
```bash
# Backend
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DATABASE_URL=postgresql://user:password@host:5432/dbname
REDIS_URL=redis://host:6379/0

# Optional
YOUTUBE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
SENDGRID_API_KEY=SG.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Frontend
VITE_API_URL=https://api.yourdomain.com
```

---

## Database Migration in Production

```bash
# Connect to production backend container
# Run migrations
alembic upgrade head

# Or include in startup script
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

---

## Health Checks & Monitoring

### Health Check Endpoint
```
GET /api/v1/health
```

### Uptime Monitoring
Use services like:
- **UptimeRobot**: Free tier, 50 monitors
- **Pingdom**: Professional monitoring
- **Google Cloud Monitoring**: Built-in for GCP

### Application Monitoring
- **Sentry**: Error tracking
- **LogRocket**: Session replay
- **Datadog**: Full-stack monitoring

---

## SSL/HTTPS Setup

### Using Let's Encrypt (Free)

```bash
# Install certbot
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Configure nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
    }
}
```

### Using Cloud Provider
Most cloud platforms (Vercel, Render, Cloud Run) provide automatic HTTPS.

---

## Scaling Considerations

### Horizontal Scaling
```yaml
# docker-compose.yml
celery_worker:
  deploy:
    replicas: 3  # Multiple workers
```

### Database Optimization
```sql
-- Add indexes
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_blog_posts_job_id ON blog_posts(job_id);

-- Enable pgvector indexing
CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops);
```

### Caching
```python
# Add Redis caching for frequent queries
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="ytblog-cache")
```

---

## Cost Estimation

### Free Tier Deployment (Vercel + Render)
- Frontend (Vercel): **$0/month**
- Backend (Render): **$0/month** (512MB RAM)
- PostgreSQL (Render): **$0/month** (shared)
- Redis (Render): **$0/month** (25MB)
- **Total: $0/month** (with limitations)

### Production Deployment (AWS)
- EC2 t3.small (API): **~$15/month**
- RDS t3.micro (PostgreSQL): **~$15/month**
- ElastiCache t3.micro (Redis): **~$15/month**
- ALB: **~$20/month**
- **Total: ~$65/month**

### Serverless Deployment (Google Cloud Run)
- Cloud Run: **Pay per request** (~$0-5/month for low traffic)
- Cloud SQL: **~$10/month** (micro instance)
- Memorystore Redis: **~$30/month** (basic)
- **Total: ~$40-45/month**

---

## Backup & Disaster Recovery

### Database Backups

```bash
# Automated daily backups
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Upload to S3
aws s3 cp backup_$(date +%Y%m%d).sql s3://your-backup-bucket/
```

### Docker Image Versioning

```bash
# Tag with version
docker tag ytblog-backend:latest ytblog-backend:v1.0.0
docker push ytblog-backend:v1.0.0
```

---

## Checklist Before Going Live

- [ ] All environment variables set
- [ ] Database migrations run
- [ ] SSL/HTTPS configured
- [ ] Health checks passing
- [ ] Monitoring setup
- [ ] Backups configured
- [ ] Error tracking (Sentry) installed
- [ ] Rate limiting configured
- [ ] CORS origins restricted
- [ ] API keys secured (not in code)
- [ ] Load testing completed
- [ ] Documentation updated

---

## Support & Resources

- **Documentation**: See [RESUME.md](RESUME.md) for architecture
- **Quick Start**: See [QUICKSTART.md](QUICKSTART.md) for local setup
- **API Docs**: `/docs` endpoint for OpenAPI specs

---

**Ready to deploy!** 🚀
