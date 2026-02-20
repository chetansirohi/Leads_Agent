from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class LeadStatus(str, Enum):
    NEW = "new"
    ANALYZING = "analyzing"
    QUALIFIED = "qualified"
    NEEDS_REVIEW = "needs_review"
    REJECTED = "rejected"
    ASSIGNED = "assigned"

class SalesRep(BaseModel):
    id: int
    name: str
    email: str
    expertise: List[str]  # e.g., ["SaaS", "Manufacturing"]
    territory: str
    current_load: int = 0
    max_capacity: int = 10
    performance_score: float = Field(ge=0, le=5)
    
    class Config:
        from_attributes = True

class Lead(BaseModel):
    id: int
    name: str
    company: str
    email: str
    phone: Optional[str] = None
    industry: str
    budget: Optional[float] = None
    company_size: Optional[str] = None  # startup, smb, enterprise
    status: LeadStatus = LeadStatus.NEW
    created_at: datetime
    assigned_rep_id: Optional[int] = None
    qualification_score: Optional[float] = None
    qualification_reasoning: Optional[str] = None
    thread_id: Optional[str] = None  # NEW: Stores thread_id when workflow interrupts
    
    class Config:
        from_attributes = True

class LeadCreate(BaseModel):
    name: str
    company: str
    email: str
    phone: Optional[str] = None
    industry: str
    budget: Optional[float] = None
    company_size: Optional[str] = None

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    company: Optional[str] = None
    status: Optional[LeadStatus] = None
    assigned_rep_id: Optional[int] = None

class Assignment(BaseModel):
    id: int
    lead_id: int
    rep_id: int
    qualification_score: float
    reasoning: str
    confidence: str  # high, medium, low
    created_at: datetime
    
    class Config:
        from_attributes = True

class HumanDecision(BaseModel):
    id: int
    assignment_id: int
    decision_type: str  # approve, reject, reassign
    decision_reason: str
    new_rep_id: Optional[int] = None
    decided_by: str
    decided_at: datetime

class WorkflowState(BaseModel):
    workflow_id: str
    lead_id: int
    current_node: str
    status: str  # running, interrupted, completed
    state_data: dict
    checkpoint_data: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

class DashboardStats(BaseModel):
    total_leads: int
    qualified_leads: int
    pending_review: int
    rejected_leads: int
    conversion_rate: float
    avg_deal_size: float
    rep_performance: List[dict]

class QualificationResult(BaseModel):
    score: float
    reasoning: str
    matched_criteria: List[str]
    confidence: str
