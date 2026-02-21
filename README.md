# AI Zakat Management System

Sistem Pengurusan Zakat Berbasis Kecerdasan Buatan (AI).

## Sistem Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│  - Dashboard Pemantauan Asnaf                               │
│  - Smart Assistant Chatbot                                  │
│  - Panel Audit & Governance                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  - REST API                                                 │
│  - Authentication & Authorization                           │
│  - Business Logic                                           │
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   AI Services   │  │   Database      │  │   File Storage  │
│   (External AI) │  │   (PostgreSQL)  │  │   (Local)       │
│   qwen3 LLM     │  │                 │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## Ports Configuration

| Service | Port |
|---------|------|
| Backend API | 6789 |
| Frontend | 7890 |
| PostgreSQL | 5432 |
| ChromaDB | 8001 |

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
cd ai-zakat-system

# Start all services
docker compose up -d

# Access the application
# Frontend: http://localhost:7890
# Backend API: http://localhost:6789
# API Docs: http://localhost:6789/docs
```

### Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 6789 --reload
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Register
- `GET /api/auth/me` - Get current user

### Applicants
- `GET /api/applicants` - List applicants
- `POST /api/applicants` - Create applicant
- `GET /api/applicants/{id}` - Get applicant details
- `PATCH /api/applicants/{id}` - Update applicant
- `POST /api/applicants/{id}/assess` - Run AI assessment

### Payments
- `GET /api/payments` - List payments
- `POST /api/payments` - Create payment
- `POST /api/payments/{id}/approve` - Approve/reject payment

### Dashboard
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/dashboard/critical-cases` - Critical cases

### Chatbot
- `POST /api/chatbot/chat` - Chat with AI assistant
- `GET /api/chatbot/faq` - Get FAQ

### Audit
- `GET /api/audit` - Get audit logs
- `GET /api/audit/stats/summary` - Get audit summary

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| ORM | SQLAlchemy + Pydantic |
| Frontend | React + TypeScript |
| UI | Tailwind CSS |
| Charts | Recharts |
| Maps | Leaflet |
| AI API | External (qwen3 models) |
| Vector DB | ChromaDB |

## AI Configuration

The system uses an external AI API server for LLM, embeddings, and ASR:

```env
# AI API (External Server)
AI_API_URL=http://localhost:9999
AI_API_KEY=your-api-key-here

# AI Models
LLM_MODEL=qwen3.5-397b-a17b-fp8-thinking
EMBEDDING_MODEL=qwen3-vl-embedding-8b
ASR_MODEL=qwen3-asr-1.7b
```

## Configuration

Environment variables can be configured in `backend/.env`:

```env
# Server
HOST=0.0.0.0
PORT=6789

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/mawp_ai

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256

# AI API (External Server)
AI_API_URL=http://localhost:9999
AI_API_KEY=your-api-key-here
LLM_MODEL=qwen3.5-397b-a17b-fp8-thinking
EMBEDDING_MODEL=qwen3-vl-embedding-8b

# Vector Store
CHROMA_DB_DIR=/app/chroma_db
```

## Project Structure

```
ai-zakat-system/
├── backend/
│   ├── app/
│   │   ├── api/routes/     # API routes
│   │   ├── core/           # Configuration
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # AI services
│   │   └── main.py         # Application entry
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   ├── types/         # TypeScript types
│   │   └── App.tsx        # Main app
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Security Features

- JWT-based authentication
- Role-based access control (RBAC)
- Audit trail logging
- Data encryption at rest and in transit

## License

Copyright © 2026. All rights reserved.