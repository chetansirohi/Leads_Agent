const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export interface Lead {
  id: number;
  name: string;
  company: string;
  email: string;
  industry: string;
  budget: number;
  company_size: string;
  status: 'new' | 'analyzing' | 'needs_review' | 'qualified' | 'assigned' | 'rejected';
  qualification_score?: number;
  qualification_reasoning?: string;
  assigned_rep_id?: number;
  created_at: string;
  updated_at: string;
  thread_id?: string;
}

export interface SalesRep {
  id: number;
  name: string;
  expertise: string[];
  current_load: number;
  max_capacity: number;
  performance_score: number;
}

export interface DashboardStats {
  total_leads: number;
  new_leads: number;
  qualified_leads: number;
  assigned_leads: number;
  pending_reviews: number;
  rejected_leads: number;
}

export interface WorkflowMetrics {
  active_workflows: number;
  interrupted_workflows: number;
  completed_workflows: number;
  failed_workflows: number;
}

export interface QualifyResponse {
  message: string;
  lead_id: number;
  thread_id: string;
  status: string;
  score?: number;
  reasoning?: string;
  assigned_rep_id?: number;
}

export interface HumanDecisionResponse {
  message: string;
  lead_id: number;
  decision: string;
  thread_id: string;
  assigned_rep_id?: number;
  score?: number;
}

export async function fetchLeads(): Promise<Lead[]> {
  const res = await fetch(`${API_BASE_URL}/api/leads`);
  if (!res.ok) throw new Error('Failed to fetch leads');
  return res.json();
}

export async function fetchLead(id: number): Promise<Lead> {
  const res = await fetch(`${API_BASE_URL}/api/leads/${id}`);
  if (!res.ok) throw new Error('Failed to fetch lead');
  return res.json();
}

export async function qualifyLead(leadId: number): Promise<QualifyResponse> {
  const res = await fetch(`${API_BASE_URL}/api/leads/${leadId}/qualify`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to qualify lead');
  return res.json();
}

export async function submitHumanDecision(
  leadId: number,
  decision: 'approve' | 'reject',
  threadId: string,
  reason?: string
): Promise<HumanDecisionResponse> {
  const params = new URLSearchParams({
    decision,
    thread_id: threadId,
  });
  if (reason) params.append('reason', reason);

  const res = await fetch(
    `${API_BASE_URL}/api/leads/${leadId}/human-decision?${params}`,
    { method: 'POST' }
  );
  if (!res.ok) throw new Error('Failed to submit decision');
  return res.json();
}

export async function fetchPendingReviews(): Promise<Lead[]> {
  const res = await fetch(`${API_BASE_URL}/api/dashboard/pending-reviews`);
  if (!res.ok) throw new Error('Failed to fetch pending reviews');
  return res.json();
}

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const res = await fetch(`${API_BASE_URL}/api/dashboard/stats`);
  if (!res.ok) throw new Error('Failed to fetch dashboard stats');
  return res.json();
}

export async function fetchWorkflowMetrics(): Promise<WorkflowMetrics> {
  const res = await fetch(`${API_BASE_URL}/api/dashboard/workflow-metrics`);
  if (!res.ok) throw new Error('Failed to fetch workflow metrics');
  return res.json();
}

export async function fetchSalesReps(): Promise<SalesRep[]> {
  const res = await fetch(`${API_BASE_URL}/api/sales-reps`);
  if (!res.ok) throw new Error('Failed to fetch sales reps');
  return res.json();
}

export async function resetDatabase(): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/admin/reset-database`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to reset database');
}
