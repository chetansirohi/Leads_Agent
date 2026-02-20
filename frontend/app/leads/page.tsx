'use client';

import { useState, useEffect } from 'react';
import { fetchLeads, qualifyLead, Lead } from '@/lib/api';
import Link from 'next/link';

export default function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [qualifying, setQualifying] = useState<number | null>(null);
  const [interruptedThreads, setInterruptedThreads] = useState<Record<number, string>>({});
  const [notifications, setNotifications] = useState<Record<number, string>>({});
  const [loading, setLoading] = useState(true);

  async function loadLeads() {
    try {
      const data = await fetchLeads();
      setLeads(data);
    } catch (error) {
      console.error('Failed to load leads', error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadLeads();
    const interval = setInterval(loadLeads, 30000);
    return () => clearInterval(interval);
  }, []);

  async function handleQualify(leadId: number) {
    setQualifying(leadId);
    setNotifications((prev) => ({ ...prev, [leadId]: '' }));

    try {
      const result = await qualifyLead(leadId);

      if (result.status === 'needs_review' && result.thread_id) {
        setInterruptedThreads((prev) => ({
          ...prev,
          [leadId]: result.thread_id,
        }));
        setNotifications((prev) => ({
          ...prev,
          [leadId]: `Lead needs human review (Score: ${result.score})`,
        }));
      } else if (result.status === 'assigned') {
        const repId = result.assigned_rep_id;
        setNotifications((prev) => ({
          ...prev,
          [leadId]: repId ? `Lead assigned to rep ${repId}` : 'Lead assigned',
        }));
      } else if (result.status === 'rejected') {
        setNotifications((prev) => ({
          ...prev,
          [leadId]: 'Lead rejected (low score)',
        }));
      }

      setTimeout(loadLeads, 1500);
    } catch (error) {
      console.error('Failed to qualify lead', error);
      setNotifications((prev) => ({
        ...prev,
        [leadId]: 'Error during qualification',
      }));
    } finally {
      setQualifying(null);
    }
  }

  const getStatusBadge = (status: Lead['status']) => {
    const styles: Record<string, string> = {
      new: 'bg-slate-100 text-slate-700',
      analyzing: 'bg-blue-100 text-blue-700',
      needs_review: 'bg-yellow-100 text-yellow-700',
      qualified: 'bg-green-100 text-green-700',
      assigned: 'bg-emerald-100 text-emerald-700',
      rejected: 'bg-red-100 text-red-700',
    };
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${styles[status] || styles.new}`}>
        {status.replace('_', ' ').toUpperCase()}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-800">Loading leads...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Leads</h1>
        <button
          onClick={loadLeads}
          className="px-4 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400 transition-colors"
        >
          Refresh
        </button>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-200">
            <tr>
              <th className="text-left px-4 py-3 text-gray-800">ID</th>
              <th className="text-left px-4 py-3 text-gray-800">Name</th>
              <th className="text-left px-4 py-3 text-gray-800">Company</th>
              <th className="text-left px-4 py-3 text-gray-800">Industry</th>
              <th className="text-right px-4 py-3 text-gray-800">Budget</th>
              <th className="text-center px-4 py-3 text-gray-800">Status</th>
              <th className="text-center px-4 py-3 text-gray-800">Score</th>
              <th className="text-center px-4 py-3 text-gray-800">Actions</th>
            </tr>
          </thead>
          <tbody>
            {leads.map((lead) => (
              <tr key={lead.id} className="border-t border-gray-200">
                <td className="px-4 py-3 text-gray-500">#{lead.id}</td>
                <td className="px-4 py-3 font-medium text-gray-900">{lead.name}</td>
                <td className="px-4 py-3 text-gray-800">{lead.company}</td>
                <td className="px-4 py-3 text-gray-800">{lead.industry}</td>
                <td className="px-4 py-3 text-right text-gray-800">${lead.budget.toLocaleString()}</td>
                <td className="px-4 py-3 text-center">{getStatusBadge(lead.status)}</td>
                <td className="px-4 py-3 text-center">
                  {lead.qualification_score !== null && lead.qualification_score !== undefined ? (
                    <span
                      className={`inline-block px-2 py-1 rounded text-sm ${
                        lead.qualification_score >= 8
                          ? 'bg-green-100 text-green-700'
                          : lead.qualification_score >= 5
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-red-100 text-red-700'
                      }`}
                    >
                      {lead.qualification_score.toFixed(1)}
                    </span>
                  ) : (
                    <span className="text-gray-400">-</span>
                  )}
                </td>
                <td className="px-4 py-3">
                  <div className="flex justify-center gap-2">
                    {lead.status === 'new' ? (
                      <button
                        onClick={() => handleQualify(lead.id)}
                        disabled={qualifying === lead.id}
                        className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors disabled:opacity-50"
                      >
                        {qualifying === lead.id ? 'Processing...' : 'Qualify'}
                      </button>
                    ) : lead.status === 'needs_review' ? (
                      <Link
                        href="/pending-reviews"
                        className="px-3 py-1 bg-yellow-500 text-white text-sm rounded hover:bg-yellow-600 transition-colors"
                      >
                        Review
                      </Link>
                    ) : lead.status === 'assigned' ? (
                      <span className="text-green-600 text-sm font-medium">
                        Assigned
                      </span>
                    ) : lead.status === 'rejected' ? (
                      <span className="text-red-600 text-sm font-medium">
                        Rejected
                      </span>
                    ) : lead.status === 'analyzing' ? (
                      <span className="text-blue-600 text-sm font-medium">
                        Analyzing...
                      </span>
                    ) : null}
                  </div>
                  {notifications[lead.id] && (
                    <div className="text-xs text-gray-600 mt-1 text-center">
                      {notifications[lead.id]}
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {leads.length === 0 && (
        <div className="text-center py-12 text-gray-600">
          No leads found. Reset the database to seed sample data.
        </div>
      )}
    </div>
  );
}
