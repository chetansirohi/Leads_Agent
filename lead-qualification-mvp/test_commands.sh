#!/bin/bash

# Lead Qualification MVP - Test Commands
# This script provides all the commands needed to test the implementation

echo "=========================================="
echo "Lead Qualification MVP - Test Suite"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}STEP 1: Environment Setup${NC}"
echo "----------------------------------------"
echo "Make sure you're in the project root:"
echo "  cd /Users/chetansirohi/Desktop/Revops/lead-qualification-mvp"
echo ""
echo "Required environment variable:"
echo "  export OPENAI_API_KEY='your-key-here'"
echo ""

echo -e "${BLUE}STEP 2: Backend Setup${NC}"
echo "----------------------------------------"
echo "Navigate to backend:"
echo "  cd backend"
echo ""
echo "Create virtual environment (if not exists):"
echo "  python3 -m venv venv"
echo ""
echo "Activate virtual environment:"
echo "  source venv/bin/activate  # On Mac/Linux"
echo "  venv\\Scripts\\activate    # On Windows"
echo ""
echo "Install dependencies:"
echo "  pip install -r requirements.txt"
echo ""
echo "Initialize database:"
echo "  python3 -c 'from models.database import init_db, seed_data; init_db(); seed_data()'"
echo ""

echo -e "${BLUE}STEP 3: Start Backend Server${NC}"
echo "----------------------------------------"
echo "Start the FastAPI server:"
echo "  uvicorn main:app --reload --port 8000"
echo ""
echo "Verify backend is running:"
echo "  curl http://localhost:8000/health"
echo ""
echo "Open API docs in browser:"
echo "  http://localhost:8000/docs"
echo ""

echo -e "${YELLOW}Leave this terminal running and open a new terminal for testing${NC}"
echo ""

echo -e "${BLUE}STEP 4: Test Backend API Endpoints${NC}"
echo "----------------------------------------"

# Test 1: Health Check
echo -e "${GREEN}Test 1: Health Check${NC}"
echo "  curl http://localhost:8000/health"
echo ""

# Test 2: List all leads
echo -e "${GREEN}Test 2: List all leads${NC}"
echo "  curl http://localhost:8000/api/leads | python3 -m json.tool"
echo ""

# Test 3: Get specific lead (ID: 1)
echo -e "${GREEN}Test 3: Get lead #1${NC}"
echo "  curl http://localhost:8000/api/leads/1 | python3 -m json.tool"
echo ""

# Test 4: Start qualification workflow (will interrupt if score 5-7)
echo -e "${GREEN}Test 4: Start qualification for lead #1${NC}"
echo "  curl -X POST http://localhost:8000/api/leads/1/qualify | python3 -m json.tool"
echo ""
echo "  ${YELLOW}Expected response if interrupted:${NC}"
echo '  {'
echo '    "message": "Qualification paused for human review",'
echo '    "lead_id": 1,'
echo '    "thread_id": "lead_1_1234567890.123",'
echo '    "status": "needs_review",'
echo '    "score": 6.5,'
echo '    "reasoning": "Medium budget, good industry fit"'
echo '  }'
echo ""

# Test 5: List pending reviews
echo -e "${GREEN}Test 5: List pending reviews${NC}"
echo "  curl http://localhost:8000/api/dashboard/pending-reviews | python3 -m json.tool"
echo ""

# Test 6: Submit human decision (APPROVE) - Replace THREAD_ID with actual value
echo -e "${GREEN}Test 6: Approve lead (use thread_id from Test 4)${NC}"
echo "  ${YELLOW}Replace THREAD_ID with actual value from Test 4${NC}"
echo '  curl -X POST "http://localhost:8000/api/leads/1/human-decision?decision=approve&thread_id=THREAD_ID" | python3 -m json.tool'
echo ""

# Test 7: Submit human decision (REJECT)
echo -e "${GREEN}Test 7: Reject lead (use thread_id from Test 4)${NC}"
echo '  curl -X POST "http://localhost:8000/api/leads/1/human-decision?decision=reject&thread_id=THREAD_ID" | python3 -m json.tool'
echo ""

# Test 8: Check workflow status
echo -e "${GREEN}Test 8: Check workflow status${NC}"
echo '  curl "http://localhost:8000/api/leads/1/workflow-status?thread_id=THREAD_ID" | python3 -m json.tool'
echo ""

# Test 9: Get dashboard stats
echo -e "${GREEN}Test 9: Get dashboard statistics${NC}"
echo "  curl http://localhost:8000/api/dashboard/stats | python3 -m json.tool"
echo ""

# Test 10: Get workflow metrics
echo -e "${GREEN}Test 10: Get workflow metrics${NC}"
echo "  curl http://localhost:8000/api/dashboard/workflow-metrics | python3 -m json.tool"
echo ""

# Test 11: List sales reps
echo -e "${GREEN}Test 11: List sales reps${NC}"
echo "  curl http://localhost:8000/api/sales-reps | python3 -m json.tool"
echo ""

# Test 12: Reset database
echo -e "${GREEN}Test 12: Reset database${NC}"
echo "  curl -X POST http://localhost:8000/api/admin/reset-database | python3 -m json.tool"
echo "  ${YELLOW}WARNING: This deletes all data and restores sample data${NC}"
echo ""

echo -e "${BLUE}STEP 5: Frontend Setup${NC}"
echo "----------------------------------------"
echo "Open a new terminal and navigate to frontend:"
echo "  cd frontend"
echo ""
echo "Install dependencies (if not done):"
echo "  npm install"
echo ""
echo "Start development server:"
echo "  npm run dev"
echo ""
echo "Open in browser:"
echo "  http://localhost:3000"
echo ""

echo -e "${BLUE}STEP 6: Manual Testing Workflow${NC}"
echo "----------------------------------------"
echo "1. Open browser to http://localhost:3000"
echo "2. Go to 'Leads' page"
echo "3. Click 'Qualify' on any lead with status 'new'"
echo "4. Watch for notification:"
echo "   - If status changes to 'assigned' → Auto-routed (score >= 8)"
echo "   - If status changes to 'rejected' → Auto-rejected (score < 5)"
echo "   - If status changes to 'needs_review' → Check sidebar for badge"
echo ""
echo "5. If lead needs review:"
echo "   - Click 'Pending Reviews' in sidebar"
echo "   - Review AI reasoning and score"
echo "   - Click 'Approve & Route' or 'Reject'"
echo "   - Verify lead status updates"
echo ""
echo "6. Check Dashboard for:"
echo "   - Lead statistics"
echo "   - Workflow metrics (active, interrupted, completed)"
echo "   - Rep performance"
echo ""

echo -e "${BLUE}STEP 7: Test Human-in-the-Loop (HITL) Flow${NC}"
echo "----------------------------------------"
echo "Test the COMPLETE interrupt/resume cycle:"
echo ""
echo "1. Qualify a lead with medium score (5-7):"
echo "   curl -X POST http://localhost:8000/api/leads/2/qualify | python3 -m json.tool"
echo ""
echo "2. Note the thread_id from response"
echo ""
echo "3. Verify workflow is interrupted:"
echo '   curl "http://localhost:8000/api/leads/2/workflow-status?thread_id=THREAD_ID"'
echo "   Should show: status: 'interrupted'"
echo ""
echo "4. Resume workflow with approve:"
echo '   curl -X POST "http://localhost:8000/api/lead/2/human-decision?decision=approve&thread_id=THREAD_ID"'
echo ""
echo "5. Verify lead is now assigned:"
echo "   curl http://localhost:8000/api/leads/2 | python3 -m json.tool"
echo "   Should show: status: 'assigned' and assigned_rep_id"
echo ""

echo -e "${BLUE}STEP 8: Test Error Scenarios${NC}"
echo "----------------------------------------"
echo "Test error handling:"
echo ""
echo "1. Missing thread_id (should return 400):"
echo '   curl -X POST "http://localhost:8000/api/leads/1/human-decision?decision=approve"'
echo ""
echo "2. Invalid decision (should return 400):"
echo '   curl -X POST "http://localhost:8000/api/leads/1/human-decision?decision=invalid&thread_id=xxx"'
echo ""
echo "3. Non-existent lead (should return 404):"
echo "   curl http://localhost:8000/api/leads/99999"
echo ""
echo "4. Invalid thread_id (should return error):"
echo '   curl -X POST "http://localhost:8000/api/leads/1/human-decision?decision=approve&thread_id=invalid"'
echo ""

echo -e "${BLUE}STEP 9: Load Testing (Optional)${NC}"
echo "----------------------------------------"
echo "Test multiple leads at once:"
echo ""
echo "Qualify first 5 leads:"
echo "  for i in {1..5}; do"
echo "    curl -X POST http://localhost:8000/api/leads/\$i/qualify &"
echo "  done"
echo "  wait"
echo ""
echo "Check dashboard stats after:"
echo "  curl http://localhost:8000/api/dashboard/stats | python3 -m json.tool"
echo ""

echo -e "${BLUE}STEP 10: Database Inspection${NC}"
echo "----------------------------------------"
echo "View database directly (optional):"
echo ""
echo "SQLite CLI:"
echo "  sqlite3 backend/data/lead_qualification.db"
echo ""
echo "Useful queries:"
echo "  SELECT * FROM leads;"
echo "  SELECT * FROM leads WHERE status='needs_review';"
echo "  SELECT * FROM sales_reps;"
echo "  SELECT * FROM workflow_states;"
echo ""
echo "Exit SQLite:"
echo "  .quit"
echo ""

echo -e "${BLUE}STEP 11: Reset Database (If Needed)${NC}"
echo "----------------------------------------"
echo "Option 1: Using API (Recommended - also clears checkpoints):"
echo "  curl -X POST http://localhost:8000/api/admin/reset-database | python3 -m json.tool"
echo ""
echo "Option 2: Manual reset:"
echo "  cd backend"
echo "  rm data/lead_qualification.db"
echo "  python3 -c 'from models.database import init_db, seed_data; init_db(); seed_data()'"
echo ""

echo "=========================================="
echo "Testing Complete!"
echo "=========================================="
echo ""
echo -e "${GREEN}Key Things to Verify:${NC}"
echo "  Thread_id is returned when workflow interrupts"
echo "  Human decision requires thread_id to resume"
echo "  Workflow metrics show accurate counts"
echo "  Sidebar badge updates with pending count"
echo "  Dashboard shows workflow states"
echo "  Lead status updates correctly after resume"
echo ""
echo -e "${YELLOW}If you encounter issues:${NC}"
echo "  1. Check backend logs for errors"
echo "  2. Verify OPENAI_API_KEY is set"
echo "  3. Ensure database is initialized"
echo "  4. Check both servers are running (8000 and 3000)"
echo ""
