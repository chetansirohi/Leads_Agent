import sqlite3
from datetime import datetime
from typing import List, Optional
from models.schemas import Lead, LeadStatus, SalesRep, Assignment, HumanDecision, WorkflowState
import json
import os

DB_PATH = "./data/lead_qualification.db"

def init_db():
    os.makedirs("./data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Leads table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            company TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            industry TEXT NOT NULL,
            budget REAL,
            company_size TEXT,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            assigned_rep_id INTEGER,
            qualification_score REAL,
            qualification_reasoning TEXT,
            thread_id TEXT
        )
    """)
    
    # Sales reps table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales_reps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            expertise TEXT,  -- JSON array
            territory TEXT NOT NULL,
            current_load INTEGER DEFAULT 0,
            max_capacity INTEGER DEFAULT 10,
            performance_score REAL DEFAULT 3.0
        )
    """)
    
    # Assignments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER NOT NULL,
            rep_id INTEGER NOT NULL,
            qualification_score REAL NOT NULL,
            reasoning TEXT NOT NULL,
            confidence TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Human decisions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS human_decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id INTEGER NOT NULL,
            decision_type TEXT NOT NULL,
            decision_reason TEXT NOT NULL,
            new_rep_id INTEGER,
            decided_by TEXT NOT NULL,
            decided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Workflow states table (for persistence)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workflow_states (
            workflow_id TEXT PRIMARY KEY,
            lead_id INTEGER NOT NULL,
            current_node TEXT NOT NULL,
            status TEXT NOT NULL,
            state_data TEXT,  -- JSON
            checkpoint_data TEXT,  -- JSON
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def seed_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if data exists
    cursor.execute("SELECT COUNT(*) FROM sales_reps")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    # Seed sales reps
    reps = [
        ("Alice Johnson", "alice@company.com", json.dumps(["SaaS", "Technology"]), "North America", 3, 10, 4.5),
        ("Bob Smith", "bob@company.com", json.dumps(["Manufacturing", "Industrial"]), "North America", 5, 10, 4.2),
        ("Carol Williams", "carol@company.com", json.dumps(["Retail", "E-commerce", "Consumer"]), "Europe", 2, 10, 4.8),
        ("David Brown", "david@company.com", json.dumps(["Healthcare", "Pharma"]), "Europe", 4, 10, 4.0),
        ("Emma Davis", "emma@company.com", json.dumps(["Finance", "Fintech"]), "APAC", 1, 10, 4.6),
    ]
    
    cursor.executemany("""
        INSERT INTO sales_reps (name, email, expertise, territory, current_load, max_capacity, performance_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, reps)
    
    # Seed leads
    leads = [
        ("TechStartup Inc.", "John Doe", "john@techstartup.com", "555-0101", "SaaS", 50000.0, "startup"),
        ("Manufacturing Co.", "Jane Smith", "jane@manufacturing.com", "555-0102", "Manufacturing", 100000.0, "smb"),
        ("Retail Giant", "Mike Johnson", "mike@retail.com", "555-0103", "Retail", 500000.0, "enterprise"),
        ("Health Plus", "Sarah Lee", "sarah@healthplus.com", "555-0104", "Healthcare", 75000.0, "smb"),
        ("FinTech Solutions", "Tom Wilson", "tom@fintech.com", "555-0105", "Finance", 200000.0, "startup"),
        ("E-Shop Pro", "Lisa Chen", "lisa@eshop.com", "555-0106", "E-commerce", 150000.0, "smb"),
        ("Industrial Systems", "Robert Taylor", "robert@industrial.com", "555-0107", "Industrial", 300000.0, "enterprise"),
        ("PharmaCorp", "Amanda White", "amanda@pharma.com", "555-0108", "Pharma", 400000.0, "enterprise"),
        ("Small Retailer", "Chris Martin", "chris@smallretail.com", "555-0109", "Retail", 25000.0, "startup"),
        ("Tech Solutions Ltd", "Patricia Brown", "patricia@techsol.com", "555-0110", "Technology", 120000.0, "smb"),
        ("Tiny Startup", "Mike Lee", "mike@tinystartup.com", "555-0111", "Retail", 5000.0, "startup"),
        ("Mom Pop Store", "Susan Kim", "susan@mompop.com", "555-0112", "Retail", 8000.0, "startup"),
    ]
    
    cursor.executemany("""
        INSERT INTO leads (company, name, email, phone, industry, budget, company_size)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, leads)
    
    conn.commit()
    conn.close()

# Database helper functions
def get_db_connection():
    return sqlite3.connect(DB_PATH)

def get_all_leads() -> List[Lead]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [Lead(
        id=row[0],
        name=row[1],
        company=row[2],
        email=row[3],
        phone=row[4],
        industry=row[5],
        budget=row[6],
        company_size=row[7],
        status=LeadStatus(row[8]),
        created_at=datetime.fromisoformat(row[9]),
        assigned_rep_id=row[10],
        qualification_score=row[11],
        qualification_reasoning=row[12],
        thread_id=row[13]
    ) for row in rows]

def get_lead_by_id(lead_id: int) -> Optional[Lead]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return Lead(
        id=row[0],
        name=row[1],
        company=row[2],
        email=row[3],
        phone=row[4],
        industry=row[5],
        budget=row[6],
        company_size=row[7],
        status=LeadStatus(row[8]),
        created_at=datetime.fromisoformat(row[9]),
        assigned_rep_id=row[10],
        qualification_score=row[11],
        qualification_reasoning=row[12],
        thread_id=row[13]
    )

def update_lead_status(lead_id: int, status: LeadStatus, **kwargs):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    updates = ["status = ?"]
    values = [status.value]
    
    for key, value in kwargs.items():
        updates.append(f"{key} = ?")
        values.append(value)
    
    values.append(lead_id)
    
    cursor.execute(f"""
        UPDATE leads SET {', '.join(updates)}
        WHERE id = ?
    """, values)
    
    conn.commit()
    conn.close()
    conn.close()

def get_all_sales_reps() -> List[SalesRep]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales_reps")
    rows = cursor.fetchall()
    conn.close()
    
    return [SalesRep(
        id=row[0],
        name=row[1],
        email=row[2],
        expertise=json.loads(row[3]),
        territory=row[4],
        current_load=row[5],
        max_capacity=row[6],
        performance_score=row[7]
    ) for row in rows]

def get_sales_rep_by_id(rep_id: int) -> Optional[SalesRep]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales_reps WHERE id = ?", (rep_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return SalesRep(
        id=row[0],
        name=row[1],
        email=row[2],
        expertise=json.loads(row[3]),
        territory=row[4],
        current_load=row[5],
        max_capacity=row[6],
        performance_score=row[7]
    )

def update_rep_load(rep_id: int, delta: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE sales_reps 
        SET current_load = current_load + ?
        WHERE id = ?
    """, (delta, rep_id))
    conn.commit()
    conn.close()

def create_assignment(assignment: Assignment) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO assignments (lead_id, rep_id, qualification_score, reasoning, confidence)
        VALUES (?, ?, ?, ?, ?)
    """, (assignment.lead_id, assignment.rep_id, assignment.qualification_score, 
          assignment.reasoning, assignment.confidence))
    conn.commit()
    assignment_id = cursor.lastrowid
    conn.close()
    return assignment_id

def save_workflow_state(state: WorkflowState):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO workflow_states 
        (workflow_id, lead_id, current_node, status, state_data, checkpoint_data, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (state.workflow_id, state.lead_id, state.current_node, state.status,
          json.dumps(state.state_data), json.dumps(state.checkpoint_data) if state.checkpoint_data else None,
          datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_workflow_state(workflow_id: str) -> Optional[WorkflowState]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workflow_states WHERE workflow_id = ?", (workflow_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return WorkflowState(
        workflow_id=row[0],
        lead_id=row[1],
        current_node=row[2],
        status=row[3],
        state_data=json.loads(row[4]) if row[4] else {},
        checkpoint_data=json.loads(row[5]) if row[5] else None,
        created_at=datetime.fromisoformat(row[6]),
        updated_at=datetime.fromisoformat(row[7])
    )

def get_dashboard_stats() -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total leads
    cursor.execute("SELECT COUNT(*) FROM leads")
    total_leads = cursor.fetchone()[0]
    
    # Qualified leads
    cursor.execute("SELECT COUNT(*) FROM leads WHERE status IN ('qualified', 'assigned')")
    qualified_leads = cursor.fetchone()[0]
    
    # Pending review
    cursor.execute("SELECT COUNT(*) FROM leads WHERE status = 'needs_review'")
    pending_review = cursor.fetchone()[0]
    
    # Rejected leads
    cursor.execute("SELECT COUNT(*) FROM leads WHERE status = 'rejected'")
    rejected_leads = cursor.fetchone()[0]
    
    # Conversion rate
    conversion_rate = (qualified_leads / total_leads * 100) if total_leads > 0 else 0
    
    # Average deal size
    cursor.execute("SELECT AVG(budget) FROM leads WHERE budget IS NOT NULL")
    avg_deal_size = cursor.fetchone()[0] or 0
    
    # Rep performance
    cursor.execute("""
        SELECT sr.name, COUNT(a.id) as assigned_leads, AVG(a.qualification_score) as avg_score
        FROM sales_reps sr
        LEFT JOIN assignments a ON sr.id = a.rep_id
        GROUP BY sr.id
    """)
    rep_performance = [
        {"name": row[0], "assigned_leads": row[1], "avg_score": round(row[2] or 0, 2)}
        for row in cursor.fetchall()
    ]
    
    conn.close()
    
    return {
        "total_leads": total_leads,
        "qualified_leads": qualified_leads,
        "pending_review": pending_review,
        "rejected_leads": rejected_leads,
        "conversion_rate": round(conversion_rate, 1),
        "avg_deal_size": round(avg_deal_size, 0),
        "rep_performance": rep_performance
    }
