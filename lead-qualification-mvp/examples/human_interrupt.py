"""
Example: Human-in-the-Loop Implementation
Demonstrates how to implement human interrupts in LangGraph.
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

class ApprovalState(TypedDict):
    lead_id: int
    qualification_score: float
    reasoning: str
    requires_approval: bool
    approved: Optional[bool]
    approver: Optional[str]
    approval_notes: Optional[str]

# Node 1: Qualify Lead
def qualify_node(state: ApprovalState) -> ApprovalState:
    """Qualify the lead and determine if approval is needed"""
    score = state['qualification_score']
    
    # High confidence leads don't need approval
    if score >= 8:
        state['requires_approval'] = False
        state['approved'] = True
    else:
        state['requires_approval'] = True
        state['approved'] = None  # Waiting for approval
    
    return state

# Node 2: Request Human Approval (Interrupt Point)
def request_approval(state: ApprovalState) -> ApprovalState:
    """Pause workflow for human approval"""
    # Workflow interrupts here
    # State is persisted and can be resumed later
    print(f"Workflow paused for lead {state['lead_id']}")
    print(f"   Score: {state['qualification_score']}")
    print(f"   Reasoning: {state['reasoning']}")
    print(f"   Waiting for human decision...")
    
    # In production:
    # - Send notification to dashboard
    # - Create task in queue
    # - Wait for API call with decision
    
    return state

# Node 3: Process Approval Decision
def process_approval(state: ApprovalState) -> ApprovalState:
    """Resume workflow with human decision"""
    if state.get('approved') is True:
        print(f"Lead {state['lead_id']} approved by {state['approver']}")
        # Proceed with routing
    else:
        print(f"Lead {state['lead_id']} rejected by {state['approver']}")
        print(f"   Notes: {state.get('approval_notes', 'N/A')}")
        # Handle rejection
    
    return state

# Node 4: Route to Sales Rep
def route_to_rep(state: ApprovalState) -> ApprovalState:
    """Assign approved lead to sales rep"""
    if state.get('approved'):
        print(f"Routing lead {state['lead_id']} to sales rep")
        # db.assign_lead(state['lead_id'], rep_id)
    return state

# Build workflow with interrupt
def create_approval_workflow():
    workflow = StateGraph(ApprovalState)
    
    workflow.add_node("qualify", qualify_node)
    workflow.add_node("request_approval", request_approval)
    workflow.add_node("process_approval", process_approval)
    workflow.add_node("route", route_to_rep)
    
    workflow.set_entry_point("qualify")
    
    # Conditional: Does it need approval?
    workflow.add_conditional_edges(
        "qualify",
        lambda s: "needs_approval" if s['requires_approval'] else "auto_approve",
        {
            "needs_approval": "request_approval",
            "auto_approve": "route"
        }
    )
    
    workflow.add_edge("request_approval", "process_approval")
    workflow.add_edge("process_approval", "route")
    workflow.add_edge("route", END)
    
    # Compile with checkpointing and interrupt
    checkpointer = MemorySaver()
    app = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["process_approval"]  # Interrupt before processing
    )
    
    return app

# Example Usage
async def example_usage():
    """Demonstrate human-in-the-loop workflow"""
    
    # 1. Start workflow
    app = create_approval_workflow()
    config = {"configurable": {"thread_id": "lead_123"}}
    
    initial_state = {
        "lead_id": 123,
        "qualification_score": 6.5,  # Needs approval
        "reasoning": "Medium budget, good fit",
        "requires_approval": False,
        "approved": None,
        "approver": None,
        "approval_notes": None
    }
    
    # 2. Run until interrupt
    result = await app.ainvoke(initial_state, config)
    print(f"\nWorkflow paused at: {result}")
    
    # 3. Human makes decision (via dashboard/API)
    # In real scenario, this comes from user input
    state = app.get_state(config)
    state.values['approved'] = True
    state.values['approver'] = 'manager@company.com'
    state.values['approval_notes'] = 'Good potential, approve'
    
    # 4. Resume workflow
    final_result = await app.ainvoke(state.values, config)
    print(f"\nFinal result: {final_result}")

# Alternative: Batch Approval Pattern
def batch_approval_example():
    """Handle multiple leads waiting for approval"""
    
    # Get all leads waiting for approval
    # pending_leads = db.get_pending_approvals()
    
    # Create approval queue
    # for lead in pending_leads:
    #     workflow.submit_for_approval(lead)
    
    # Dashboard shows queue:
    # - Lead ID | Score | Reasoning | Actions [Approve] [Reject] [Reassign]
    
    pass

# Alternative: Escalation Pattern
def escalation_pattern():
    """Escalate to different approvers based on deal size"""
    
    def route_to_approver(state: ApprovalState) -> str:
        score = state['qualification_score']
        
        if score >= 9:
            return "senior_manager"  # High value deals
        elif score >= 7:
            return "team_lead"       # Standard deals
        else:
            return "peer_review"     # Low confidence
    
    # workflow.add_conditional_edges("request_approval", route_to_approver, {...})
    pass

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
