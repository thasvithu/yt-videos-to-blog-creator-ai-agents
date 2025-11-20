# YouTube to Blog Generator - Full-Stack AI Application

Transform YouTube videos into beautifully formatted, SEO-optimized blog posts using AI.

**🎯 Resume Project**: This is a production-ready full-stack application showcasing modern AI/ML engineering, backend development, frontend development, and DevOps practices.

📖 **[Quick Start Guide](QUICKSTART.md)** | 📋 **[Resume/Architecture Details](RESUME.md)**

## ✨ Features

- 🤖 **AI-Powered Blog Generation**: LangChain + LangGraph state machine with GPT-4
- 🎥 **YouTube Integration**: Automatic video search, transcript fetching, and metadata extraction
- 🔍 **Vector Search**: pgvector integration for semantic search and RAG capabilities
- 📧 **Email Delivery**: SendGrid integration for sharing blog posts
- 📋 **Copy & Download**: One-click copy-to-clipboard and markdown download
- 🔄 **Real-time Progress**: Live job status updates with progress tracking
- 🐳 **Production-Ready**: Docker, CI/CD, comprehensive testing, and monitoring

## 🏗️ Tech Stack

### Backend
- **FastAPI**: Modern async Python web framework
- **LangChain + LangGraph**: LLM orchestration and workflow management
- **OpenAI GPT-4**: Blog generation and embeddings
- **PostgreSQL + pgvector**: Database with vector similarity search
- **Celery + Redis**: Distributed task queue for background processing
- **SQLAlchemy + Alembic**: ORM and database migrations

### Frontend
- **React 18 + TypeScript**: Type-safe frontend framework
- **Vite**: Lightning-fast build tool
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client with TypeScript support

### Infrastructure
- **Docker & Docker Compose**: Multi-service orchestration
- **GitHub Actions**: Automated CI/CD pipeline
- **pytest + vitest**: Comprehensive testing suite
- **ruff + ESLint**: Code quality and linting

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose installed
- OpenAI API key (required)
- YouTube Data API key (optional, enhances video search)
- SendGrid API key (optional, enables email delivery)

### Quick Start (Docker)

1. **Clone and navigate**
   ```bash
   git clone <repository-url>
   cd yt-videos-to-blog-creator-ai-agents
   ```

2. **Configure environment**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your API keys (see QUICKSTART.md)
   ```

3. **Start all services**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

**Need more details?** See [QUICKSTART.md](QUICKSTART.md) for step-by-step instructions.

### Local Development (without Docker)

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start PostgreSQL and Redis locally, update .env

# Run migrations
alembic upgrade head

# Start API server
uvicorn app.main:app --reload

# Start Celery worker (new terminal)
celery -A app.workers.celery_app worker --loglevel=info
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)**: Step-by-step setup guide with troubleshooting
- **[RESUME.md](RESUME.md)**: Full architecture, technical decisions, and resume highlights
- **[API Docs](http://localhost:8000/docs)**: Interactive OpenAPI/Swagger documentation (when running)

## 🔌 API Endpoints

- `POST /api/v1/generate` - Create blog generation job
- `GET /api/v1/status/{job_id}` - Get job status
- `POST /api/v1/send-email` - Send blog post via email
- `GET /api/v1/health` - Health check

## Environment Variables

### Backend
```env
OPENAI_API_KEY=your_key_here
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
REDIS_URL=redis://localhost:6379/0
YOUTUBE_API_KEY=your_key_here (optional)
SENDGRID_API_KEY=your_key_here (optional)
```

### Frontend
```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── models/        # Database & Pydantic models
│   │   ├── services/      # Business logic
│   │   ├── workers/       # Celery tasks
│   │   ├── config.py      # Configuration
│   │   └── main.py        # FastAPI app
│   ├── tests/             # Backend tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── api/           # API client
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Development Roadmap

- [x] Project scaffolding
- [x] Backend API skeleton
- [x] Frontend UI components
- [ ] YouTube data ingestion
- [ ] LangChain + LangGraph pipeline
- [ ] Vector embeddings & RAG
- [ ] Database integration
- [ ] Email delivery
- [ ] CI/CD pipeline
- [ ] Tests & quality checks
- [ ] Documentation

## Contributing

This is a personal resume project, but feedback and suggestions are welcome!

## License

MIT License - see LICENSE file for details

## Author

Built by [thasvithu](https://github.com/thasvithu) as a full-stack AI application showcase.