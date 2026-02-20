"""
Example: LangGraph Node Implementations
Demonstrates different types of nodes in the workflow.
"""

from typing import TypedDict

class WorkflowState(TypedDict):
    lead_id: int
    data: dict
    score: float
    status: str

# Node 1: Simple Transform Node
def analyze_node(state: WorkflowState) -> WorkflowState:
    """Simple node that transforms data"""
    print(f"Analyzing lead {state['lead_id']}")
    state['status'] = 'analyzed'
    return state

# Node 2: Async Node with External API Call
def enrich_node(state: WorkflowState) -> WorkflowState:
    """Node that calls external API (e.g., Clearbit, Apollo)"""
    # In production: Call enrichment API
    # enriched_data = await enrichment_api.get_company_data(state['data']['company'])
    state['data']['enriched'] = True
    return state

# Node 3: LLM-based Node
def qualify_with_llm(state: WorkflowState) -> WorkflowState:
    """Node that uses LLM for qualification"""
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(model="gpt-4")
    prompt = f"Score this lead: {state['data']}"
    
    response = llm.invoke(prompt)
    state['score'] = float(response.content)
    return state

# Node 4: Conditional Router Node
def route_node(state: WorkflowState) -> str:
    """Node that returns routing decision"""
    if state['score'] >= 8:
        return "high_value"
    elif state['score'] >= 5:
        return "medium_value"
    else:
        return "low_value"

# Node 5: Human Interrupt Node
def human_review_node(state: WorkflowState) -> WorkflowState:
    """Node that pauses for human input"""
    # This will interrupt the workflow
    state['status'] = 'awaiting_human_review'
    # Workflow pauses here until human provides input
    return state

# Node 6: Side Effect Node (Database Write)
def save_to_db_node(state: WorkflowState) -> WorkflowState:
    """Node that persists data"""
    # db.save_lead(state['lead_id'], state['score'])
    state['status'] = 'saved'
    return state

# Example usage in graph builder:
# workflow.add_node("analyze", analyze_node)
# workflow.add_node("enrich", enrich_node)
# workflow.add_node("qualify", qualify_with_llm)
# workflow.add_node("route", route_node)
# workflow.add_node("human_review", human_review_node)
# workflow.add_node("save", save_to_db_node)
