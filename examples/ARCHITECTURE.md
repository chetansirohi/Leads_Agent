# LangGraph & LangChain Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Next.js 15    │  │   React         │  │   TypeScript    │  │
│  │   (Frontend)    │  │   Components    │  │   Types         │  │
│  └────────┬────────┘  └─────────────────┘  └─────────────────┘  │
│           │                                                      │
│           │ HTTP/REST (Port 3000 → 8000)                         │
│           ▼                                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API LAYER                                 │
│                    FastAPI (Python)                              │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  /api/leads │  │ /api/sales  │  │ /api/dash   │             │
│  │  (CRUD)     │  │  -reps      │  │  board      │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │           Workflow Orchestration (LangGraph)            │    │
│  │                                                         │    │
│  │   Nodes: analyze → qualify → route → assign            │    │
│  │                                                         │    │
│  │   Features:                                             │    │
│  │   • Human-in-the-loop (interrupt)                      │    │
│  │   • Conditional edges (score-based routing)            │    │
│  │   • Persistence (checkpointing)                        │    │
│  │   • Retry logic (exponential backoff)                  │    │
│  │   • Fallbacks (GPT-4 → GPT-3.5)                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              LLM Integration (LangChain)                │    │
│  │                                                         │    │
│  │   Primary: GPT-4 (high quality)                        │    │
│  │   Fallback: GPT-3.5 (cost-effective)                   │    │
│  │                                                         │    │
│  │   Capabilities:                                         │    │
│  │   • Structured output (JSON)                           │    │
│  │   • Function calling                                   │    │
│  │   • Context management                                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
└──────────────────────────────┼───────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    SQLite Database                       │    │
│  │                                                         │    │
│  │   Tables:                                               │    │
│  │   • leads (lead information)                           │    │
│  │   • sales_reps (rep profiles)                          │    │
│  │   • assignments (lead-rep matches)                     │    │
│  │   • workflow_states (checkpoints)                      │    │
│  │   • human_decisions (approval logs)                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              LangGraph Checkpointing                    │    │
│  │                                                         │    │
│  │   • Persist workflow state after each node             │    │
│  │   • Resume from interruptions                          │    │
│  │   • Replay capabilities                                │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Detailed Workflow Diagram

```
Lead Submission
      │
      ▼
┌─────────────┐
│   ANALYZE   │──────────────────────────────────────────────┐
│  (Parse &   │                                              │
│   Validate) │                                              │
└──────┬──────┘                                              │
       │                                                     │
       ▼                                                     │
┌─────────────┐                                              │
│   QUALIFY   │◄─────────────────────────────────────────────┘
│   (LLM)     │  Retry with exponential backoff (max 3)
│  Score 0-10 │  Fallback: GPT-4 → GPT-3.5
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   ROUTE     │
│  Decision   │
└──────┬──────┘
       │
       ├────────────────┬────────────────┐
       │                │                │
       ▼                ▼                ▼
  Score >= 8      5 <= Score < 8    Score < 5
  High Quality     Medium Quality    Low Quality
       │                │                │
       ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  AUTO_ROUTE │  │   HUMAN     │  │ AUTO_REJECT │
│   (Assign   │  │  INTERRUPT  │  │  (Update    │
│    to Rep)  │  │             │  │   status)   │
└─────────────┘  └──────┬──────┘  └─────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │ Dashboard Shows │
              │  "Needs Review" │
              └────────┬────────┘
                       │
              Human makes decision
              [Approve] [Reject] [Reassign]
                       │
                       ▼
              ┌─────────────────┐
              │ Resume Workflow │
              └────────┬────────┘
                       │
                       ▼
                 ┌─────────────┐
                 │  Finalize   │
                 │ Assignment  │
                 └─────────────┘
```

## Component Interactions

### 1. Lead Qualification Flow
```
Frontend          FastAPI           LangGraph         OpenAI        SQLite
   │                 │                 │                │             │
   │──POST /qualify─▶│                 │                │             │
   │                 │──trigger      ─▶│                │             │
   │                 │   workflow      │                │             │
   │                 │                 │──analyze lead──│             │
   │                 │                 │                │             │
   │                 │                 │◀─structured───│             │
   │                 │                 │   JSON output  │             │
   │                 │                 │                │             │
   │                 │                 │──checkpoint───▶│             │
   │                 │                 │   state        │             │
   │                 │                 │                │             │
   │                 │                 │──score lead───▶│             │
   │                 │                 │   (0-10)       │             │
   │                 │                 │                │             │
   │                 │                 │◀─qualification│             │
   │                 │                 │   result       │             │
   │                 │                 │                │             │
   │                 │                 │──conditional───│             │
   │                 │                 │   routing      │             │
   │                 │                 │                │             │
   │                 │                 │──interrupt───▶│             │
   │                 │◀─needs review───│   (if needed)  │             │
   │◀─pending review─│                 │                │             │
   │   response      │                 │                │             │
```

### 2. Human-in-the-Loop Resume
```
Frontend          FastAPI           LangGraph         SQLite
   │                 │                 │                │
   │──POST decision─▶│                 │                │
   │   (approve/    │                 │                │
   │    reject)      │                 │                │
   │                 │──resume        ─▶│               │
   │                 │   workflow      │                │
   │                 │                 │──load state───▶│
   │                 │                 │   from db      │
   │                 │                 │                │
   │                 │                 │──apply human───│
   │                 │                 │   decision     │
   │                 │                 │                │
   │                 │                 │──route to rep──│
   │                 │                 │   (if approved)│
   │                 │                 │                │
   │                 │                 │──save final───▶│
   │                 │                 │   state        │
   │                 │                 │                │
   │                 │◀─completed──────│                │
   │◀─success────────│                 │                │
```

## LangGraph State Management

```
┌─────────────────────────────────────────────────────┐
│              LeadState (TypedDict)                  │
├─────────────────────────────────────────────────────┤
│ lead_id: int                                        │
│ lead_data: dict                                     │
│ current_node: str                                   │
│ qualification_score: float | None                   │
│ qualification_reasoning: str | None                 │
│ matched_criteria: list[str]                         │
│ assigned_rep_id: int | None                         │
│ assignment_confidence: str                          │
│ requires_human_review: bool                         │
│ human_decision: str | None                          │
│ retry_count: int                                    │
│ error: str | None                                   │
└─────────────────────────────────────────────────────┘
                          │
                          │ Checkpoint after each node
                          ▼
┌─────────────────────────────────────────────────────┐
│              SQLite Checkpointer                    │
├─────────────────────────────────────────────────────┤
│ workflow_id: str (PK)                               │
│ lead_id: int                                        │
│ current_node: str                                   │
│ status: str                                         │
│ state_data: JSON                                    │
│ checkpoint_data: JSON                               │
│ created_at: timestamp                               │
│ updated_at: timestamp                               │
└─────────────────────────────────────────────────────┘
```

## Error Handling & Retry Strategy

```
LLM Call Attempt 1
      │
      ├─► Success ──► Continue
      │
      ▼ Failure
Wait 2 seconds (exponential backoff)
      │
LLM Call Attempt 2
      │
      ├─► Success ──► Continue
      │
      ▼ Failure
Wait 4 seconds
      │
LLM Call Attempt 3
      │
      ├─► Success ──► Continue
      │
      ▼ Failure
Use Fallback Model (GPT-3.5)
      │
      ├─► Success ──► Continue with warning
      │
      ▼ Failure
Use Rule-based Fallback
      │
      ▼
Log Error & Return Default Score
```

## Deployment Architecture (Production)

```
┌─────────────────────────────────────────────────────────────┐
│                        Load Balancer                         │
│                     (CloudFlare / AWS ALB)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Next.js    │ │   Next.js    │ │   Next.js    │
│   Instance 1 │ │   Instance 2 │ │   Instance 3 │
│   (Port 3000)│ │   (Port 3000)│ │   (Port 3000)│
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Cluster                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  Worker 1  │  │  Worker 2  │  │  Worker 3  │            │
│  │  (Uvicorn) │  │  (Uvicorn) │  │  (Uvicorn) │            │
│  │  Port 8000 │  │  Port 8001 │  │  Port 8002 │            │
│  └──────┬─────┘  └──────┬─────┘  └──────┬─────┘            │
└─────────┼───────────────┼───────────────┼──────────────────┘
          │               │               │
          └───────────────┼───────────────┘
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
    ┌─────────────────┐     ┌─────────────────┐
    │   PostgreSQL    │     │    Redis        │
    │   (Primary DB)  │     │    (Cache &     │
    │                 │     │     Queue)      │
    └─────────────────┘     └─────────────────┘
              │                       │
              ▼                       ▼
    ┌─────────────────────────────────────────┐
    │         LangGraph Workers               │
    │   (Celery / RQ for async processing)   │
    │                                         │
    │   • Background qualification           │
    │   • Email notifications                │
    │   • Report generation                  │
    └─────────────────────────────────────────┘
```

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 15, React, TypeScript | UI/UX, SSR, API routes |
| **Styling** | Tailwind CSS, shadcn/ui | Consistent design system |
| **Charts** | Recharts | Data visualization |
| **Backend** | FastAPI, Python 3.9+ | High-performance API |
| **AI/ML** | LangGraph, LangChain, OpenAI | Workflow orchestration |
| **Validation** | Pydantic | Type safety, schema validation |
| **Database** | SQLite (MVP) → PostgreSQL (Prod) | Data persistence |
| **Retries** | Tenacity | Resilient external API calls |
| **Monitoring** | LangSmith (optional) | LLM observability |

## Key Design Principles

1. **Statelessness**: API layer is stateless; all state in database
2. **Idempotency**: Workflow operations can be safely retried
3. **Observability**: Every decision logged with reasoning
4. **Graceful Degradation**: Fallbacks at every layer
5. **Human Override**: AI assists, humans decide on edge cases
