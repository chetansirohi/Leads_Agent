'use client';

import { useState, useEffect } from 'react';
import { fetchPendingReviews, submitHumanDecision, Lead } from '@/lib/api';

export default function PendingReviewsPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [threadIds, setThreadIds] = useState<Record<number, string>>({});
  const [processing, setProcessing] = useState<Record<number, boolean>>({});
  const [results, setResults] = useState<Record<number, string>>({});
  const [loading, setLoading] = useState(true);

  async function loadPendingReviews() {
    try {
      const data = await fetchPendingReviews();
      setLeads(data);
      // Auto-populate thread_ids from lead data
      const threadMap: Record<number, string> = {};
      data.forEach((lead) => {
        if (lead.thread_id) {
          threadMap[lead.id] = lead.thread_id;
        }
      });
      setThreadIds(threadMap);
    } catch (error) {
      console.error('Failed to load pending reviews', error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadPendingReviews();
    const interval = setInterval(loadPendingReviews, 30000);
    return () => clearInterval(interval);
  }, []);

  async function handleDecision(leadId: number, decision: 'approve' | 'reject') {
    const threadId = threadIds[leadId];
    if (!threadId) {
      alert('Error: Thread ID is missing. Cannot submit decision.');
      return;
    }

    setProcessing((prev) => ({ ...prev, [leadId]: true }));
    setResults((prev) => ({ ...prev, [leadId]: '' }));

    try {
      const result = await submitHumanDecision(leadId, decision, threadId);
      setResults((prev) => ({ ...prev, [leadId]: result.message }));
      setTimeout(loadPendingReviews, 1500);
    } catch (error) {
      console.error('Failed to submit decision', error);
      setResults((prev) => ({ ...prev, [leadId]: 'Error submitting decision' }));
    } finally {
      setProcessing((prev) => ({ ...prev, [leadId]: false }));
    }
  }

  const handleThreadIdChange = (leadId: number, value: string) => {
    setThreadIds((prev) => ({ ...prev, [leadId]: value }));
  };

  const getScoreColor = (score?: number) => {
    if (score === undefined || score === null) return 'text-slate-400';
    if (score >= 8) return 'text-green-600';
    if (score >= 5) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-800">Loading pending reviews...</div>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Pending Reviews</h1>

      {leads.length === 0 ? (
        <div className="text-center py-12 text-gray-600">
          No leads need human review. All caught up!
        </div>
      ) : (
        <div className="space-y-4">
          {leads.map((lead) => (
            <div key={lead.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{lead.name}</h3>
                  <p className="text-gray-600">{lead.company} • {lead.industry}</p>
                </div>
                <div className="text-right">
                  <div className={`text-3xl font-bold ${getScoreColor(lead.qualification_score)}`}>
                    {lead.qualification_score?.toFixed(1) ?? '-'}
                  </div>
                  <div className="text-sm text-gray-500">Qualification Score</div>
                </div>
              </div>

              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">AI Reasoning:</h4>
                <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                  {lead.qualification_reasoning || 'No reasoning provided'}
                </p>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Thread ID (for debugging):
                </label>
                <input
                  type="text"
                  value={threadIds[lead.id] || ''}
                  onChange={(e) => handleThreadIdChange(lead.id, e.target.value)}
                  placeholder="Enter thread_id if not auto-populated"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-800"
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => handleDecision(lead.id, 'approve')}
                  disabled={processing[lead.id]}
                  className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                >
                  {processing[lead.id] ? 'Processing...' : 'Approve'}
                </button>
                <button
                  onClick={() => handleDecision(lead.id, 'reject')}
                  disabled={processing[lead.id]}
                  className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
                >
                  {processing[lead.id] ? 'Processing...' : 'Reject'}
                </button>
              </div>

              {results[lead.id] && (
                <div className="mt-3 text-sm text-center text-gray-700">
                  {results[lead.id]}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
