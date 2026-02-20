# Lead Qualification MVP - LangGraph AI Agent

A production-ready MVP demonstrating AI-powered lead qualification and routing using LangGraph with advanced features including human-in-the-loop, persistence, retries, and fallbacks.

## 🎯 Project Overview

This MVP directly addresses the **Application Engineer II - Revenue Operations** role requirements at HighLevel by implementing:

- **LangGraph workflows** with stateful orchestration
- **Human-in-the-loop** review for uncertain leads
- **Conditional routing** based on AI qualification scores
- **Persistence** with SQLite checkpointing
- **Retry logic** with exponential backoff and fallbacks
- **Pydantic** schemas for type safety
- **FastAPI** backend with REST architecture
- **Next.js** frontend with modern React patterns

## 🏗️ Architecture

```
Frontend (Next.js 15)  ←→  Backend (FastAPI)  ←→  AI Engine (LangGraph + OpenAI)
                                     ↓
                              SQLite Database
                              (with checkpointing)
```

### Key Components

1. **Lead Analysis Node** - Parses and validates lead data
2. **Qualification Node** - Uses GPT-4/3.5 to score leads (0-10)
3. **Routing Node** - Makes conditional routing decisions
4. **Human Interrupt Node** - Pauses for manual review when needed
5. **Assignment Node** - Matches leads to optimal sales reps

## 🚀 Quick Start

### Prerequisites
- Python 3.9-3.12 (NOT 3.14)
- Node.js 18+
- OpenAI API Key

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
export OPENAI_API_KEY="your-key-here"
python -c "from models.database import init_db, seed_data; init_db(); seed_data()"
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Access the app at http://localhost:3000

## ✨ Key Features

### 1. Human-in-the-Loop (HITL) - NATIVE INTERRUPT
Leads with medium confidence scores (5-7) trigger REAL human review using LangGraph's native interrupt():
- Workflow ACTUALLY pauses execution (not fake polling)
- State is automatically checkpointed with thread_id
- Dashboard shows "Needs Review" queue
- Managers can approve or reject
- Frontend calls API with thread_id
- Backend resumes workflow using Command(resume=...)
- Zero resource usage while waiting (genuinely paused)

### 2. Conditional Routing
Score-based routing with three paths:
- **≥8**: Auto-route to best-matched sales rep
- **5-7**: Human review required
- **<5**: Auto-reject

### 3. Persistence & Checkpointing
- Workflow state saved after each node
- Resume from interruptions
- Replay capabilities for debugging
- SQLite-based storage

### 4. Retry Logic & Fallbacks
- Exponential backoff (2s, 4s, 8s)
- Max 3 retries before fallback
- GPT-4 → GPT-3.5 → Rule-based fallback
- No data loss on API failures

### 5. Intelligent Rep Matching
Matches leads to reps based on:
- Industry expertise alignment
- Current workload capacity
- Performance scores
- Territory matching

## 📊 Dashboard Features

- **Real-time metrics**: Total leads, qualified, pending review, conversion rate
- **Lead management**: View, filter, and qualify leads
- **Human review queue**: Approve/reject uncertain leads
- **Sales rep overview**: Workload and performance tracking
- **Assignment tracking**: View lead-rep matches with reasoning

## 🧪 Sample Data

Pre-loaded with realistic data:
- **10 leads** across SaaS, Manufacturing, Retail, Healthcare, Finance
- **5 sales reps** with different expertise areas
- Varying budgets ($25K - $500K)
- Mixed company sizes (startup, SMB, enterprise)

## 📚 Documentation

### Examples Folder
Contains production-ready code patterns:
- `langgraph_nodes.py` - Different node implementations
- `conditional_edges.py` - Routing strategies
- `human_interrupt.py` - HITL patterns
- `pydantic_schemas.py` - Data validation examples

### Architecture
See `examples/ARCHITECTURE.md` for:
- System diagrams
- Component interactions
- State management
- Error handling flows

### Deployment
See `examples/DEPLOYMENT.md` for:
- Docker setup
- Cloud deployment (AWS, Railway, Vercel)
- Production considerations
- Scaling strategies

## 🎤 Interview Talking Points

### LangGraph Expertise
- "I implemented a 7-node workflow with conditional edges"
- "Used interrupt_before for human-in-the-loop"
- "Checkpointing enables resume and replay capabilities"

### Production Engineering
- "Retry logic with exponential backoff handles transient failures"
- "Fallback chain ensures system degrades gracefully"
- "Pydantic schemas ensure type safety across the stack"

### RevOps Domain
- "Lead qualification matches sales rep expertise to industry"
- "Human review queue for edge cases builds trust"
- "Audit trail shows every decision with reasoning"

### Reliability
- "SQLite persistence for MVP, easily migrate to PostgreSQL"
- "Stateless API design scales horizontally"
- "Graceful error handling at every layer"

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 15, React, TypeScript, Tailwind CSS, shadcn/ui |
| **Backend** | FastAPI, Python 3.11 |
| **AI/ML** | LangGraph 1.0, LangChain, OpenAI GPT-4/3.5 |
| **Database** | SQLite (MVP) → PostgreSQL (production) |
| **Validation** | Pydantic 2.x |
| **Resilience** | Tenacity (retry logic) |

## 📈 Future Enhancements

### Production Improvements
- [ ] PostgreSQL database
- [ ] Redis caching
- [ ] Celery for async processing
- [ ] Authentication (OAuth2/JWT)
- [ ] Real-time WebSocket updates
- [ ] Advanced analytics dashboard

### Advanced Features
- [ ] Email/SMS notifications
- [ ] Calendar integration
- [ ] Call transcription integration
- [ ] Advanced rep scoring algorithms
- [ ] A/B testing for qualification criteria

## 🐛 Known Limitations (MVP)

- SQLite (single-file) - fine for demo, use PostgreSQL in production
- Mock authentication - implement real auth for production
- In-memory checkpointing - use persistent storage in production
- No email notifications - add for production
- Simplified rep matching - enhance with ML in production

## 📝 Project Structure

```
lead-qualification-mvp/
├── backend/
│   ├── main.py                 # FastAPI app entry
│   ├── models/
│   │   ├── schemas.py          # Pydantic models
│   │   └── database.py         # SQLite operations
│   ├── agents/
│   │   └── qualification.py    # LangGraph workflow
│   ├── requirements.txt
│   └── data/                   # SQLite database
├── frontend/
│   ├── app/                    # Next.js app router
│   ├── components/             # React components
│   └── package.json
├── examples/
│   ├── ARCHITECTURE.md         # System diagrams
│   ├── DEPLOYMENT.md           # Deployment guide
│   ├── langgraph_nodes.py      # Code patterns
│   ├── conditional_edges.py
│   ├── human_interrupt.py
│   └── pydantic_schemas.py
└── README.md                   # This file
```

## 🤝 Contributing

This is an interview MVP project. For production use:
1. Add proper authentication
2. Implement rate limiting
3. Add comprehensive logging
4. Setup monitoring (LangSmith, DataDog, etc.)
5. Add tests (unit, integration, e2e)

## 📄 License

MIT License - Feel free to use for your own projects!

## 🎓 Learning Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Python Docs](https://python.langchain.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)

---

**Built for the HighLevel Application Engineer II - Revenue Operations Interview**

This MVP demonstrates production-grade AI workflow implementation with all the key features mentioned in the job description: LangGraph orchestration, human-in-the-loop, conditional routing, persistence, retries, and fallbacks.
