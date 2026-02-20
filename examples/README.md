# Examples Folder

This folder contains code examples and patterns used in the Lead Qualification MVP.

## Contents

1. **LangGraph Patterns**
   - Node implementations
   - Conditional edges
   - Human-in-the-loop patterns
   - State management

2. **Database Patterns**
   - Pydantic schemas
   - SQLite operations
   - Data seeding

3. **Integration Examples**
   - API routes
   - Frontend components
   - Workflow orchestration

## Key Concepts Demonstrated

### Human-in-the-Loop
The workflow can pause and wait for human input when confidence is low or manual review is needed.

### Conditional Routing
Based on qualification scores, leads are automatically routed to different paths:
- Score >= 8: Auto-route to sales rep
- Score 5-7: Human review required
- Score < 5: Auto-reject

### Persistence
Workflow state is persisted using LangGraph's checkpointing mechanism, allowing:
- Resume after interruptions
- Audit trail of decisions
- Replay capabilities

### Retry Logic
LLM calls include exponential backoff retry logic with fallback to cheaper models.

## Architecture

```
Frontend (Next.js) <--REST--> Backend (FastAPI) <--SQLite--> Database
                                     |
                                     v
                              LangGraph Workflow
                                     |
                                     v
                              OpenAI GPT-4/3.5
```
