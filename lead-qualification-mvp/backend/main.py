"""
Lead Qualification API - FastAPI Backend

This module provides RESTful API endpoints for the lead qualification system.
It integrates with LangGraph workflows for AI-powered lead routing.

Key Features:
- Async endpoints for non-blocking workflow execution
- Thread-based workflow tracking for checkpoint resumption
- Proper error handling with HTTP status codes
- Pydantic validation for type safety
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import schemas
from models.schemas import (
    Lead, LeadCreate, LeadUpdate, LeadStatus, SalesRep, 
    DashboardStats, Assignment
)

# Import database functions
from models.database import (
    init_db, seed_data, get_all_leads, get_lead_by_id, 
    update_lead_status, get_all_sales_reps, create_assignment,
    get_dashboard_stats, get_db_connection
)

# Import LangGraph workflow functions
from agents.qualification import (
    run_qualification_workflow, 
    resume_workflow,
    get_workflow_status
)

# Initialize database on startup
init_db()
seed_data()

# Create FastAPI app
app = FastAPI(
    title="Lead Qualification API",
    description="AI-powered lead qualification and routing system with LangGraph",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with system status and features."""
    return {
        "message": "Lead Qualification API",
        "status": "running",
        "version": "1.0.0",
        "features": [
            "LangGraph workflow orchestration with native interrupt()",
            "Human-in-the-loop with Command(resume=...)",
            "Checkpoint persistence with thread_id tracking",
            "Conditional routing based on AI qualification scores",
            "Retry logic with exponential backoff and fallbacks",
            "Pydantic schema validation",
            "Idempotent workflow operations"
        ]
    }


# ============================================================================
# LEAD ENDPOINTS
# ============================================================================

@app.get("/api/leads", response_model=List[Lead])
async def list_leads():
    """
    Get all leads from the database.
    
    Returns:
        List of Lead objects ordered by creation date (newest first)
    """
    return get_all_leads()


@app.get("/api/leads/{lead_id}", response_model=Lead)
async def get_lead(lead_id: int):
    """
    Get a specific lead by ID.
    
    Args:
        lead_id: The database ID of the lead
    
    Returns:
        Lead object if found
    
    Raises:
        HTTPException 404: If lead not found
    """
    lead = get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@app.post("/api/leads/{lead_id}/qualify")
async def qualify_lead_endpoint(lead_id: int):
    """
    Start qualification workflow for a lead.
    
    This endpoint initiates the LangGraph workflow which:
    1. Analyzes lead data completeness
    2. Uses GPT-4 to score the lead (0-10)
    3. Routes based on score:
       - Score >= 8: Auto-route to best sales rep
       - Score 5-7: Interrupt for human review (returns thread_id)
       - Score < 5: Auto-reject
    
    Args:
        lead_id: The database ID of the lead to qualify
    
    Returns:
        {
            "message": Status message,
            "lead_id": Lead ID,
            "status": "assigned" | "needs_review" | "rejected",
            "score": Qualification score (if available),
            "reasoning": AI reasoning (if available),
            "thread_id": Present if workflow interrupted for human review
        }
    
    Raises:
        HTTPException 404: If lead not found
        HTTPException 500: If workflow execution fails
    """
    lead = get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Generate unique thread_id for this workflow instance
    # Format: lead_{id}_{timestamp} ensures uniqueness
    thread_id = f"lead_{lead_id}_{datetime.now().timestamp()}"
    
    # Update status to analyzing (shows in-progress state in UI)
    update_lead_status(lead_id, LeadStatus.ANALYZING)
    
    try:
        # Run the workflow
        # If interrupt() is called (score 5-7), this returns the interrupted state
        result = await run_qualification_workflow(
            lead_id=lead_id,
            lead_data=lead.dict(),
            thread_id=thread_id
        )
        
        # Build response based on workflow outcome
        response = {
            "message": "Qualification completed",
            "lead_id": lead_id,
            "thread_id": thread_id,
            "status": "unknown",
            "score": result.get('qualification_score'),
            "reasoning": result.get('qualification_reasoning')
        }
        
        # Determine status based on workflow result
        if result.get('requires_human_review'):
            # Workflow interrupted - human review needed
            response["status"] = "needs_review"
            response["message"] = "Qualification paused for human review"
            # IMPORTANT: Return thread_id so frontend can resume later
            response["thread_id"] = thread_id
            
        elif result.get('assigned_rep_id'):
            # Lead successfully assigned to sales rep
            response["status"] = "assigned"
            response["message"] = f"Lead assigned to rep {result['assigned_rep_id']}"
            
        elif result.get('error'):
            # Error during qualification
            response["status"] = "error"
            response["message"] = f"Qualification error: {result['error']}"
            update_lead_status(lead_id, LeadStatus.NEW)  # Reset to allow retry
            
        else:
            # Lead rejected (score < 5)
            response["status"] = "rejected"
            response["message"] = "Lead rejected (low score)"
        
        return response
        
    except Exception as e:
        # Reset status on failure
        update_lead_status(lead_id, LeadStatus.NEW)
        raise HTTPException(
            status_code=500, 
            detail=f"Qualification workflow failed: {str(e)}"
        )


@app.post("/api/leads/{lead_id}/human-decision")
async def submit_human_decision(
    lead_id: int,
    decision: str = Query(..., description="Human decision: 'approve' or 'reject'"),
    thread_id: Optional[str] = Query(None, description="Thread ID from interrupted workflow"),
    reason: Optional[str] = Query(None, description="Optional reason for decision")
):
    """
    Submit human decision for a lead that needs review.
    
    This endpoint resumes a workflow that was interrupted by the native
    interrupt() function. It uses the Command(resume=...) pattern to
    properly resume execution from the checkpoint.
    
    Args:
        lead_id: The database ID of the lead
        decision: 'approve' or 'reject'
        thread_id: REQUIRED - The thread_id from the interrupted workflow
        reason: Optional reason for the decision (for audit trail)
    
    Returns:
        {
            "message": Success message,
            "lead_id": Lead ID,
            "decision": Decision made,
            "thread_id": Thread ID,
            "assigned_rep_id": Sales rep ID (if approved)
        }
    
    Raises:
        HTTPException 400: If thread_id missing or invalid decision
        HTTPException 404: If lead not found
        HTTPException 500: If resume fails
    
    Example:
        POST /api/leads/123/human-decision?decision=approve&thread_id=lead_123_1234567890.123
    """
    # Validate decision
    if decision not in ['approve', 'reject']:
        raise HTTPException(
            status_code=400, 
            detail="Invalid decision. Must be 'approve' or 'reject'"
        )
    
    # CRITICAL: thread_id is required to resume the workflow
    if not thread_id:
        raise HTTPException(
            status_code=400,
            detail="thread_id is required to resume workflow. "
                   "Get this from the /qualify endpoint response."
        )
    
    # Verify lead exists
    lead = get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    try:
        # Resume the workflow with human decision
        # This uses Command(resume=...) which is idempotent (safe to retry)
        result = await resume_workflow(thread_id, decision)
        
        # Update database based on final workflow result
        if decision == 'approve' and result.get('assigned_rep_id'):
            update_lead_status(
                lead_id,
                LeadStatus.ASSIGNED,
                assigned_rep_id=result['assigned_rep_id'],
                qualification_score=result.get('qualification_score'),
                qualification_reasoning=result.get('qualification_reasoning'),
                thread_id=None  # Clear thread_id after completion
            )
            message = f"Lead approved and assigned to rep {result['assigned_rep_id']}"
            
        elif decision == 'approve' and not result.get('assigned_rep_id'):
            # Approved but no rep available
            update_lead_status(
                lead_id,
                LeadStatus.QUALIFIED,  # Mark as qualified but unassigned
                qualification_score=result.get('qualification_score'),
                qualification_reasoning=result.get('qualification_reasoning'),
                thread_id=None  # Clear thread_id after completion
            )
            message = "Lead approved but no suitable rep found"
            
        else:  # reject
            update_lead_status(
                lead_id,
                LeadStatus.REJECTED,
                qualification_score=result.get('qualification_score'),
                qualification_reasoning=result.get('qualification_reasoning'),
                thread_id=None  # Clear thread_id after completion
            )
            message = "Lead rejected"
        
        return {
            "message": message,
            "lead_id": lead_id,
            "decision": decision,
            "thread_id": thread_id,
            "assigned_rep_id": result.get('assigned_rep_id'),
            "score": result.get('qualification_score')
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process decision: {str(e)}"
        )


@app.get("/api/leads/{lead_id}/workflow-status")
async def check_workflow_status(lead_id: int, thread_id: str):
    """
    Check the status of a workflow by thread_id.
    
    Useful for:
    - Checking if a workflow is still waiting for human input
    - Verifying workflow completed after resume
    - Debugging workflow state
    
    Args:
        lead_id: The database ID of the lead
        thread_id: The thread ID to check
    
    Returns:
        {
            "thread_id": Thread ID,
            "status": "interrupted" | "completed" | "not_found",
            "current_node": Current node in workflow,
            "lead_id": Lead ID,
            "qualification_score": Score (if available),
            "requires_human_review": Whether waiting for human input,
            "assigned_rep_id": Rep ID (if assigned)
        }
    """
    try:
        status = await get_workflow_status(thread_id)
        return status
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get workflow status: {str(e)}"
        )


# ============================================================================
# SALES REP ENDPOINTS
# ============================================================================

@app.get("/api/sales-reps", response_model=List[SalesRep])
async def list_sales_reps():
    """
    Get all sales representatives.
    
    Returns:
        List of SalesRep objects with their expertise, workload, and performance
    """
    return get_all_sales_reps()


# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_stats():
    """
    Get dashboard statistics.
    
    Returns:
        DashboardStats with:
        - total_leads: Total number of leads
        - qualified_leads: Number of qualified/assigned leads
        - pending_review: Number of leads awaiting human review
        - rejected_leads: Number of rejected leads
        - conversion_rate: Percentage of qualified leads
        - avg_deal_size: Average budget of all leads
        - rep_performance: Performance metrics per rep
    """
    stats = get_dashboard_stats()
    return DashboardStats(**stats)


@app.get("/api/dashboard/pending-reviews")
async def get_pending_reviews():
    """
    Get all leads that need human review.
    
    Returns detailed information for the human review queue including:
    - Lead information (name, company, email, industry, budget)
    - AI qualification score and reasoning
    - Any available thread_id for workflow resumption
    
    This endpoint powers the /pending-reviews page in the frontend.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT l.*, sr.name as assigned_rep_name
        FROM leads l
        LEFT JOIN sales_reps sr ON l.assigned_rep_id = sr.id
        WHERE l.status = 'needs_review'
        ORDER BY l.qualification_score DESC, l.created_at DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    pending_reviews = []
    for row in rows:
        pending_reviews.append({
            "id": row[0],
            "name": row[1],
            "company": row[2],
            "email": row[3],
            "phone": row[4],
            "industry": row[5],
            "budget": row[6],
            "company_size": row[7],
            "status": row[8],
            "created_at": row[9],
            "qualification_score": row[11],
            "qualification_reasoning": row[12],
            "thread_id": row[13]
        })

    return pending_reviews


@app.get("/api/dashboard/workflow-metrics")
async def get_workflow_metrics():
    """
    Get workflow-specific metrics for the dashboard.
    
    NEW ENDPOINT: Provides real-time workflow state counts:
    - active_workflows: Currently running workflows
    - interrupted_workflows: Waiting for human input
    - completed_workflows: Finished successfully
    - failed_workflows: Encountered errors
    
    This helps monitor system health and human review queue depth.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Count by status
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN status = 'analyzing' THEN 1 END) as active,
            COUNT(CASE WHEN status = 'needs_review' THEN 1 END) as interrupted,
            COUNT(CASE WHEN status IN ('assigned', 'rejected') THEN 1 END) as completed,
            COUNT(CASE WHEN status = 'error' THEN 1 END) as failed
        FROM leads
    """)
    
    row = cursor.fetchone()
    conn.close()
    
    return {
        "active_workflows": row[0],
        "interrupted_workflows": row[1],
        "completed_workflows": row[2],
        "failed_workflows": row[3]
    }


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        {
            "status": "healthy" | "unhealthy",
            "database": "connected" | "disconnected",
            "timestamp": Current ISO timestamp
        }
    """
    try:
        # Test database connection
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# DATABASE RESET
# ============================================================================

@app.post("/api/admin/reset-database")
async def reset_database():
    """
    Reset the database to initial state.
    
    WARNING: This deletes all data and reseeds with sample data.
    Use only for testing/demo purposes.
    
    Returns:
        {
            "message": "Database reset successful",
            "timestamp": ISO timestamp
        }
    """
    try:
        import os
        
        # Delete existing database file
        db_path = "./data/lead_qualification.db"
        if os.path.exists(db_path):
            os.remove(db_path)
        
        # Reinitialize database
        init_db()
        seed_data()
        
        return {
            "message": "Database reset successful",
            "timestamp": datetime.now().isoformat(),
            "warning": "All data has been deleted and reset to sample data"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset database: {str(e)}"
        )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Run with auto-reload for development
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
