'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';
import { fetchPendingReviews } from '@/lib/api';

export default function Sidebar() {
  const pathname = usePathname();
  const [pendingCount, setPendingCount] = useState(0);

  useEffect(() => {
    async function loadPendingCount() {
      try {
        const leads = await fetchPendingReviews();
        setPendingCount(leads.length);
      } catch (error) {
        console.error('Failed to load pending count', error);
      }
    }

    loadPendingCount();
    const interval = setInterval(loadPendingCount, 30000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { href: '/', label: 'Dashboard', icon: '📊' },
    { href: '/leads', label: 'Leads', icon: '👥' },
    { href: '/sales-reps', label: 'Sales Reps', icon: '👤' },
    { href: '/pending-reviews', label: 'Pending Reviews', icon: '⏳', badge: pendingCount },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-white min-h-screen p-4">
      <div className="mb-8">
        <h1 className="text-xl font-bold text-white">Lead Qualification</h1>
        <p className="text-sm text-gray-400">AI-Powered Routing</p>
      </div>

      <nav className="space-y-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center justify-between px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-slate-800'
              }`}
            >
              <span className="flex items-center gap-3">
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </span>
              {item.badge !== undefined && item.badge > 0 && (
                <span className="bg-yellow-500 text-black text-xs font-bold px-2 py-1 rounded-full">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      <div className="mt-8 pt-4 border-t border-slate-700">
        <div className="text-xs text-gray-400">
          <p>Backend: localhost:8000</p>
          <p>Status: Connected</p>
        </div>
      </div>
    </aside>
  );
}
