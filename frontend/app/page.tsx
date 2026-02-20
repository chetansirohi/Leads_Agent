'use client';

import { useState, useEffect } from 'react';
import { fetchDashboardStats, fetchWorkflowMetrics, fetchSalesReps, fetchLeads, resetDatabase, DashboardStats, WorkflowMetrics, SalesRep, Lead } from '@/lib/api';
import Link from 'next/link';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [metrics, setMetrics] = useState<WorkflowMetrics | null>(null);
  const [reps, setReps] = useState<SalesRep[]>([]);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [resetting, setResetting] = useState(false);

  async function handleReset() {
    if (!confirm('Are you sure you want to reset the database? All data will be lost.')) return;
    setResetting(true);
    try {
      await resetDatabase();
      window.location.reload();
    } catch (error) {
      console.error('Failed to reset database', error);
      alert('Failed to reset database');
    } finally {
      setResetting(false);
    }
  }

  useEffect(() => {
    async function loadData() {
      try {
        const [statsData, metricsData, repsData, leadsData] = await Promise.all([
          fetchDashboardStats(),
          fetchWorkflowMetrics(),
          fetchSalesReps(),
          fetchLeads(),
        ]);
        setStats(statsData);
        setMetrics(metricsData);
        setReps(repsData);
        setLeads(leadsData);
      } catch (error) {
        console.error('Failed to load dashboard data', error);
      } finally {
        setLoading(false);
      }
    }

    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-800">Loading dashboard...</div>
      </div>
    );
  }

  // Calculate additional metrics
  const totalLeads = stats?.total_leads ?? 0;
  const qualifiedLeads = stats?.qualified_leads ?? 0;
  const assignedLeads = stats?.assigned_leads ?? 0;
  const rejectedLeads = stats?.rejected_leads ?? 0;
  const conversionRate = totalLeads > 0 ? ((qualifiedLeads + assignedLeads) / totalLeads * 100).toFixed(1) : '0.0';
  const failureRate = totalLeads > 0 ? ((rejectedLeads / totalLeads) * 100).toFixed(1) : '0.0';
  const avgBudget = leads.length > 0 
    ? (leads.reduce((sum, l) => sum + (l.budget || 0), 0) / leads.length).toFixed(0)
    : '0';

  const statCards = [
    { name: 'Total Leads', value: totalLeads, color: 'bg-blue-500' },
    { name: 'New Leads', value: stats?.new_leads ?? 0, color: 'bg-gray-500' },
    { name: 'Qualified', value: qualifiedLeads, color: 'bg-green-500' },
    { name: 'Assigned', value: assignedLeads, color: 'bg-emerald-500' },
    { name: 'Pending Review', value: stats?.pending_reviews ?? 0, color: 'bg-yellow-500' },
    { name: 'Rejected', value: rejectedLeads, color: 'bg-red-500' },
    { name: 'Avg Budget', value: `$${avgBudget}`, color: 'bg-purple-500' },
    { name: 'Conversion Rate', value: `${conversionRate}%`, color: 'bg-indigo-500' },
    { name: 'Failure Rate', value: `${failureRate}%`, color: 'bg-orange-500' },
  ];

  const workflowStatCards = [
    { name: 'Active', value: metrics?.active_workflows ?? 0, color: 'bg-blue-500' },
    { name: 'Interrupted (HITL)', value: metrics?.interrupted_workflows ?? 0, color: 'bg-yellow-500' },
    { name: 'Completed', value: metrics?.completed_workflows ?? 0, color: 'bg-green-500' },
    { name: 'Failed', value: metrics?.failed_workflows ?? 0, color: 'bg-red-500' },
  ];

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <button
          onClick={handleReset}
          disabled={resetting}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
        >
          {resetting ? 'Resetting...' : 'Reset Database'}
        </button>
      </div>

      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-4 text-gray-900">Lead Statistics</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {statCards.map((card) => (
            <div key={card.name} className={`${card.color} text-white rounded-lg p-4 shadow-md`}>
              <div className="text-sm opacity-80">{card.name}</div>
              <div className="text-2xl font-bold">{card.value}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-4 text-gray-900">Workflow Metrics</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {workflowStatCards.map((card) => (
            <div key={card.name} className={`${card.color} text-white rounded-lg p-4 shadow-md`}>
              <div className="text-sm opacity-80">{card.name}</div>
              <div className="text-2xl font-bold">{card.value}</div>
            </div>
          ))}
        </div>
        {(metrics?.interrupted_workflows ?? 0) > 0 && (
          <div className="mt-4">
            <Link
              href="/pending-reviews"
              className="inline-block bg-yellow-500 text-white px-4 py-2 rounded-lg hover:bg-yellow-600 transition-colors"
            >
              Review {metrics?.interrupted_workflows} Interrupted Workflows →
            </Link>
          </div>
        )}
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-4 text-gray-900">Sales Rep Performance</h2>
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-100">
              <tr>
                <th className="text-left px-4 py-3 text-gray-800">Name</th>
                <th className="text-left px-4 py-3 text-gray-800">Expertise</th>
                <th className="text-center px-4 py-3 text-gray-800">Load</th>
                <th className="text-center px-4 py-3 text-gray-800">Capacity</th>
                <th className="text-center px-4 py-3 text-gray-800">Performance</th>
              </tr>
            </thead>
            <tbody>
              {reps.map((rep) => (
                <tr key={rep.id} className="border-t border-gray-200">
                  <td className="px-4 py-3 font-medium text-gray-900">{rep.name}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-1 flex-wrap">
                      {rep.expertise.map((exp) => (
                        <span
                          key={exp}
                          className="bg-gray-200 text-gray-700 text-xs px-2 py-1 rounded"
                        >
                          {exp}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-center text-gray-800">{rep.current_load}</td>
                  <td className="px-4 py-3 text-center text-gray-800">{rep.max_capacity}</td>
                  <td className="px-4 py-3 text-center">
                    <span
                      className={`inline-block px-2 py-1 rounded text-sm ${
                        rep.performance_score >= 4
                          ? 'bg-green-100 text-green-700'
                          : rep.performance_score >= 3
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-red-100 text-red-700'
                      }`}
                    >
                      {rep.performance_score.toFixed(1)}/5
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
