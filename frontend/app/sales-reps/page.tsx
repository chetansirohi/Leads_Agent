'use client';

import { useState, useEffect } from 'react';
import { fetchSalesReps, SalesRep } from '@/lib/api';

export default function SalesRepsPage() {
  const [reps, setReps] = useState<SalesRep[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadReps() {
      try {
        const data = await fetchSalesReps();
        setReps(data);
      } catch (error) {
        console.error('Failed to load sales reps', error);
      } finally {
        setLoading(false);
      }
    }

    loadReps();
    const interval = setInterval(loadReps, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-800">Loading sales reps...</div>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Sales Representatives</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {reps.map((rep) => (
          <div key={rep.id} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">{rep.name}</h3>
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
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Expertise:</span>
                <div className="flex gap-1">
                  {rep.expertise.map((exp) => (
                    <span
                      key={exp}
                      className="bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded"
                    >
                      {exp}
                    </span>
                  ))}
                </div>
              </div>
              
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Current Load:</span>
                <span className="font-medium text-gray-900">
                  {rep.current_load} / {rep.max_capacity}
                </span>
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full"
                  style={{ width: `${(rep.current_load / rep.max_capacity) * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {reps.length === 0 && (
        <div className="text-center py-12 text-gray-600">
          No sales reps found.
        </div>
      )}
    </div>
  );
}
