"""
Example: Conditional Edges and Routing Patterns
Demonstrates different routing strategies in LangGraph.
"""

from typing import TypedDict
from langgraph.graph import StateGraph, END

class State(TypedDict):
    score: float
    priority: str
    path: str

# Pattern 1: Score-based Routing
def route_by_score(state: State) -> str:
    """Route based on qualification score"""
    score = state['score']
    
    if score >= 9:
        return "priority"  # Fast track
    elif score >= 7:
        return "standard"  # Normal process
    elif score >= 5:
        return "review"    # Needs review
    else:
        return "reject"    # Auto-reject

# Usage in graph:
# workflow.add_conditional_edges(
#     "qualify",
#     route_by_score,
#     {
#         "priority": "fast_track_node",
#         "standard": "standard_node",
#         "review": "human_review_node",
#         "reject": "reject_node"
#     }
# )

# Pattern 2: Priority-based Routing
def route_by_priority(state: State) -> str:
    """Route based on lead priority"""
    priority = state['priority']
    
    routing_map = {
        "enterprise": "enterprise_team",
        "smb": "smb_team",
        "startup": "startup_team"
    }
    
    return routing_map.get(priority, "default_team")

# Pattern 3: Multi-criteria Routing
def route_multi_criteria(state: State) -> str:
    """Route based on multiple factors"""
    score = state['score']
    priority = state['priority']
    
    # Enterprise leads with high scores go to senior reps
    if priority == "enterprise" and score >= 8:
        return "senior_rep"
    
    # Medium scores need nurture
    elif 5 <= score < 8:
        return "nurture_sequence"
    
    # Low scores but high priority get special handling
    elif score < 5 and priority == "enterprise":
        return "research_team"
    
    else:
        return "general_queue"

# Pattern 4: Cyclic Routing (Retry Logic)
def route_with_retry(state: State) -> str:
    """Route that can loop back for retries"""
    if state.get('error'):
        if state.get('retry_count', 0) < 3:
            return "retry"  # Loop back
        else:
            return "fail"   # Max retries reached
    return "success"

# Usage:
# workflow.add_conditional_edges(
#     "process",
#     route_with_retry,
#     {
#         "retry": "process",  # Loop back to same node
#         "fail": "error_handler",
#         "success": END
#     }
# )

# Pattern 5: Time-based Routing
def route_by_time(state: State) -> str:
    """Route based on business hours"""
    from datetime import datetime
    
    hour = datetime.now().hour
    
    # After hours - queue for tomorrow
    if hour < 9 or hour > 17:
        return "queue_for_tomorrow"
    
    # Lunch time - lower priority
    elif 12 <= hour <= 13:
        return "afternoon_queue"
    
    else:
        return "immediate_process"

# Pattern 6: Dynamic Routing with Database Lookup
def route_by_rep_availability(state: State) -> str:
    """Route based on sales rep availability"""
    # In production:
    # available_reps = db.get_available_reps(state['territory'])
    # if available_reps:
    #     state['assigned_rep'] = available_reps[0]
    #     return "assign"
    # else:
    #     return "queue"
    pass

# Complete example graph setup:
def create_routing_example():
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("qualify", lambda s: s)  # Placeholder
    workflow.add_node("high_priority", lambda s: {**s, "path": "high"})
    workflow.add_node("medium_priority", lambda s: {**s, "path": "medium"})
    workflow.add_node("low_priority", lambda s: {**s, "path": "low"})
    
    # Set entry point
    workflow.set_entry_point("qualify")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "qualify",
        route_by_score,
        {
            "priority": "high_priority",
            "standard": "medium_priority",
            "review": "medium_priority",  # Same as standard for this example
            "reject": "low_priority"
        }
    )
    
    # All paths end
    workflow.add_edge("high_priority", END)
    workflow.add_edge("medium_priority", END)
    workflow.add_edge("low_priority", END)
    
    return workflow.compile()

if __name__ == "__main__":
    app = create_routing_example()
    result = app.invoke({"score": 8.5, "priority": "enterprise", "path": ""})
    print(f"Routing result: {result}")
