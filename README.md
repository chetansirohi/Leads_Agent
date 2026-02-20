# Lead Qualification MVP

AI-powered lead qualification system using LangGraph + FastAPI + Next.js

## Features

- **LangGraph Workflow** - Native interrupt() for human-in-the-loop
- **AI Qualification** - GPT-4 scoring with GPT-3.5 fallback
- **Smart Routing** - Auto-route high scores, human review for medium, auto-reject low
- **Sales Rep Matching** - Industry expertise + performance + workload balancing
- **Dashboard** - Real-time stats, workflow metrics, and lead management

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- OpenAI API Key

### Backend Setup (FastAPI)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database (creates tables and seed data)
python3 -c "from models.database import init_db, seed_data; init_db(); seed_data()"

# Start the backend server
uvicorn main:app --reload --port 8000
```

The backend API will be available at: http://localhost:8000

### Frontend Setup (Next.js)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at: http://localhost:3000

## Environment Variables

### Backend (.env)

Create a `.env` file in the `backend/` directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Get your API key from: https://platform.openai.com/api-keys

### Frontend (.env.local)

The frontend already has a default configuration pointing to localhost:8000. To change the backend URL, create a `.env.local` file in the `frontend/` directory:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## How It Works

1. **Qualify a Lead** - Click "Qualify" on any new lead
2. **AI Scoring** - GPT-4 scores the lead (0-10)
3. **Routing Logic**:
   - Score ≥ 8: Auto-assigned to best sales rep
   - Score 5-7: Human review required (interrupt)
   - Score < 5: Auto-rejected
4. **Human Decision** - Approve or reject in Pending Reviews

## API Endpoints

- `GET /api/leads` - List all leads
- `POST /api/leads/{id}/qualify` - Start qualification workflow
- `POST /api/leads/{id}/human-decision` - Submit human decision
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/dashboard/pending-reviews` - Leads needing review
- `POST /api/admin/reset-database` - Reset database to seed data

## Deployment

### Option 1: Vercel (Frontend only)

Deploy the frontend to Vercel and host the backend separately:

1. Deploy frontend to Vercel
2. Deploy backend to Render/Railway/Fly.io
3. Set `NEXT_PUBLIC_API_BASE_URL` to your backend URL

### Option 2: Vercel (Both Frontend + FastAPI)

FastAPI is supported on Vercel! See: https://vercel.com/docs/frameworks/fastapi

1. Push code to GitHub
2. Create two Vercel projects:
   - Frontend: Import `frontend/` directory
   - Backend: Import `backend/` directory
3. Add `OPENAI_API_KEY` environment variable to backend

## Tech Stack

- **Backend**: FastAPI, LangGraph, OpenAI GPT-4
- **Frontend**: Next.js, TypeScript, Tailwind CSS
- **Database**: SQLite (can migrate to PostgreSQL)

## License

MIT
