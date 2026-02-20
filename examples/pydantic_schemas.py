"""
Example: Pydantic Schema Definitions
Demonstrates data validation and serialization patterns.
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Basic Schema
class LeadBase(BaseModel):
    """Base lead schema with common fields"""
    name: str = Field(..., min_length=1, max_length=100)
    company: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    phone: Optional[str] = None
    industry: str
    budget: Optional[float] = Field(None, ge=0)
    company_size: Optional[str] = None

# Schema with Validation
class LeadCreate(LeadBase):
    """Schema for creating new leads with validation"""
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format"""
        if v and not v.replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Phone number must contain only digits, dashes, and spaces')
        return v
    
    @validator('industry')
    def validate_industry(cls, v):
        """Validate industry is from allowed list"""
        allowed = ['SaaS', 'Manufacturing', 'Retail', 'Healthcare', 'Finance', 'Technology']
        if v not in allowed:
            raise ValueError(f'Industry must be one of: {allowed}')
        return v
    
    @validator('budget')
    def validate_budget(cls, v):
        """Budget validation"""
        if v and v < 1000:
            raise ValueError('Budget must be at least $1,000')
        return v

# Schema with Status Tracking
class LeadStatus(str, Enum):
    NEW = "new"
    ANALYZING = "analyzing"
    QUALIFIED = "qualified"
    NEEDS_REVIEW = "needs_review"
    REJECTED = "rejected"
    ASSIGNED = "assigned"

class Lead(LeadBase):
    """Full lead model with database fields"""
    id: int
    status: LeadStatus = LeadStatus.NEW
    created_at: datetime
    assigned_rep_id: Optional[int] = None
    qualification_score: Optional[float] = Field(None, ge=0, le=10)
    qualification_reasoning: Optional[str] = None
    
    class Config:
        from_attributes = True  # Enable ORM mode
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "John Doe",
                "company": "Tech Corp",
                "email": "john@techcorp.com",
                "industry": "SaaS",
                "budget": 50000,
                "status": "qualified",
                "qualification_score": 8.5
            }
        }

# Nested Schema
class SalesRep(BaseModel):
    """Sales representative schema"""
    id: int
    name: str
    email: EmailStr
    expertise: List[str]  # Industry expertise
    territory: str
    current_load: int = Field(default=0, ge=0)
    max_capacity: int = Field(default=10, ge=1)
    performance_score: float = Field(default=3.0, ge=0, le=5)
    
    @property
    def available_capacity(self) -> int:
        """Calculate available capacity"""
        return self.max_capacity - self.current_load
    
    @property
    def is_available(self) -> bool:
        """Check if rep has capacity for new leads"""
        return self.available_capacity > 0

# Response Schema with Computed Fields
class LeadResponse(BaseModel):
    """API response schema for leads"""
    success: bool
    data: Optional[Lead] = None
    message: Optional[str] = None
    errors: Optional[List[str]] = None

# Dashboard Stats Schema
class DashboardStats(BaseModel):
    """Dashboard statistics schema"""
    total_leads: int
    qualified_leads: int
    pending_review: int
    rejected_leads: int
    conversion_rate: float = Field(..., ge=0, le=100)
    avg_deal_size: float
    rep_performance: List[dict]
    
    @validator('conversion_rate')
    def round_conversion(cls, v):
        """Round conversion rate to 1 decimal"""
        return round(v, 1)

# Workflow State Schema
class WorkflowState(BaseModel):
    """LangGraph workflow state schema"""
    workflow_id: str
    lead_id: int
    current_node: str
    status: str  # running, interrupted, completed
    state_data: dict
    checkpoint_data: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

# API Request/Response Examples
class QualificationRequest(BaseModel):
    """Request to start qualification workflow"""
    lead_id: int
    auto_approve_threshold: float = Field(default=8.0, ge=0, le=10)

class QualificationResponse(BaseModel):
    """Response from qualification workflow"""
    lead_id: int
    score: float
    reasoning: str
    status: str
    assigned_rep_id: Optional[int]
    requires_human_review: bool

# Usage Examples
if __name__ == "__main__":
    # Create a lead
    lead_data = {
        "name": "Jane Smith",
        "company": "Startup Inc",
        "email": "jane@startup.com",
        "phone": "555-0123",
        "industry": "SaaS",
        "budget": 75000
    }
    
    lead = LeadCreate(**lead_data)
    print(f"Created lead: {lead.json()}")
    
    # Validate invalid data
    try:
        invalid_lead = LeadCreate(
            name="",  # Too short
            company="Test",
            email="invalid-email",
            industry="Unknown"
        )
    except Exception as e:
        print(f"Validation error: {e}")
    
    # Create sales rep
    rep = SalesRep(
        id=1,
        name="Alice Johnson",
        email="alice@company.com",
        expertise=["SaaS", "Technology"],
        territory="North America",
        current_load=3,
        max_capacity=10
    )
    
    print(f"Rep available: {rep.is_available}")
    print(f"Available capacity: {rep.available_capacity}")
