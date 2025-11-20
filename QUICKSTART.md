# 🚀 Quick Start Guide

## Prerequisites

Before starting, ensure you have:
- Docker Desktop installed and running
- OpenAI API key (required)
- YouTube Data API key (optional, for better video search)
- SendGrid API key (optional, for email delivery)

## Step 1: Environment Setup

### Create Backend Environment File

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` with your API keys:

```env
# Required
OPENAI_API_KEY=sk-your-openai-key-here
DATABASE_URL=postgresql://ytblog:ytblog123@postgres:5432/ytblog
REDIS_URL=redis://redis:6379/0

# Optional
YOUTUBE_API_KEY=your-youtube-api-key
SENDGRID_API_KEY=your-sendgrid-key
SENDGRID_FROM_EMAIL=your-email@example.com
```

## Step 2: Start All Services

```bash
# From project root
docker-compose up --build
```

This starts:
- ✅ PostgreSQL (with pgvector)
- ✅ Redis
- ✅ Backend API (FastAPI)
- ✅ Celery Worker
- ✅ Frontend (React)

## Step 3: Access the Application

Open your browser to:
- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## Step 4: Generate Your First Blog

1. Enter a YouTube channel name (e.g., "OpenAI")
2. Enter a video title (e.g., "GPT-4 Tutorial")
3. Optional: Add your email to receive the blog
4. Click "Generate Blog Post"
5. Watch the progress bar as the AI works
6. View your beautiful blog post!

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps

# View backend logs
docker-compose logs backend

# Restart services
docker-compose down
docker-compose up
```

### Celery Worker Not Processing

```bash
# Check worker logs
docker-compose logs celery_worker

# Verify Redis connection
docker-compose exec redis redis-cli ping
```

### Frontend Not Loading

```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up --build frontend
```

## Development Mode

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Run Database Migrations

```bash
cd backend
alembic upgrade head
```

### Run Tests

```bash
# Backend tests
cd backend
pytest -v

# Frontend tests
cd frontend
npm run test
```

## API Usage Examples

### Generate Blog Post

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "channel_name": "OpenAI",
    "video_title": "GPT-4",
    "email": "optional@example.com"
  }'
```

Response:
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "pending"
}
```

### Check Status

```bash
curl http://localhost:8000/api/v1/status/123e4567-e89b-12d3-a456-426614174000
```

Response:
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "progress": 100,
  "blog_post": {
    "id": 1,
    "title": "Understanding GPT-4...",
    "content": "# GPT-4 Deep Dive\n\n...",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key for GPT-4 |
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `REDIS_URL` | Yes | - | Redis connection string |
| `YOUTUBE_API_KEY` | No | - | YouTube Data API v3 key |
| `SENDGRID_API_KEY` | No | - | SendGrid API key |
| `SENDGRID_FROM_EMAIL` | No | - | Sender email address |
| `CORS_ORIGINS` | No | `*` | Allowed CORS origins |

## Next Steps

- Read [RESUME.md](RESUME.md) for architecture details
- Check [README.md](README.md) for full documentation
- Explore API docs at http://localhost:8000/docs
- Customize prompts in `backend/app/services/llm_pipeline.py`
- Modify UI in `frontend/src/components/`

## Support

For issues or questions, please check:
1. Docker logs: `docker-compose logs <service_name>`
2. API documentation: http://localhost:8000/docs
3. GitHub Issues (if available)

Happy blogging! 🎉
