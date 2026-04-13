'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { getAnalytics } from '@/lib/api';
import { ArrowLeft, BarChart3 } from 'lucide-react';
import Link from 'next/link';

interface AnalyticsData {
  total_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  success_rate: number;
  avg_execution_time_ms: number | null;
  most_used_tools: Array<{ tool: string; count: number }>;
  tasks_by_date: Array<{ date: string; count: number }>;
}

export default function AnalyticsPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    } else if (!isLoading && isAuthenticated) {
      loadAnalytics();
    }
  }, [isAuthenticated, isLoading, router]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const data = await getAnalytics();
      setAnalytics(data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background px-4 md:px-6 py-6">
      <div className="max-w-[860px] mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <BarChart3 className="w-6 h-6 text-accent-blue" />
            <h1 className="text-2xl font-bold text-text-primary">Analytics Dashboard</h1>
          </div>
          <Link
            href="/dashboard"
            className="flex items-center gap-2 px-3 h-9 border border-text-primary text-text-primary text-sm rounded-md hover:bg-text-primary hover:text-background transition-all"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
        </div>

        {isLoading || loading || !analytics ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin w-8 h-8 border-4 border-accent-blue border-t-transparent rounded-full"></div>
          </div>
        ) : (
          <>
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-card rounded-xl border border-[rgba(255,255,255,0.08)] p-5">
                <p className="text-sm text-text-muted mb-1">Total Tasks</p>
                <p className="text-3xl font-bold text-text-primary">{analytics.total_tasks}</p>
              </div>
              <div className="bg-card rounded-xl border border-[rgba(255,255,255,0.08)] p-5">
                <p className="text-sm text-text-muted mb-1">Completed</p>
                <p className="text-3xl font-bold text-accent-green">{analytics.completed_tasks}</p>
              </div>
              <div className="bg-card rounded-xl border border-[rgba(255,255,255,0.08)] p-5">
                <p className="text-sm text-text-muted mb-1">Failed</p>
                <p className="text-3xl font-bold text-accent-red">{analytics.failed_tasks}</p>
              </div>
              <div className="bg-card rounded-xl border border-[rgba(255,255,255,0.08)] p-5">
                <p className="text-sm text-text-muted mb-1">Success Rate</p>
                <p className="text-3xl font-bold text-text-primary">{analytics.success_rate.toFixed(1)}%</p>
              </div>
            </div>

            {/* Avg Execution Time */}
            {analytics.avg_execution_time_ms && (
              <div className="bg-card rounded-xl border border-[rgba(255,255,255,0.08)] p-5 mb-6">
                <h2 className="text-lg font-bold text-text-primary mb-2">Average Execution Time</h2>
                <p className="text-2xl font-bold text-accent-blue">
                  {(analytics.avg_execution_time_ms / 1000).toFixed(2)}s
                </p>
              </div>
            )}

            {/* Most Used Tools */}
            <div className="bg-card rounded-xl border border-[rgba(255,255,255,0.08)] p-5 mb-6">
              <h2 className="text-lg font-bold text-text-primary mb-4">Most Used Tools</h2>
              <div className="space-y-3">
                {analytics.most_used_tools.slice(0, 10).map((toolData, idx) => (
                  <div key={idx} className="flex items-center justify-between">
                    <span className="px-4 py-2 bg-[#1E3A5F] text-[#60A5FA] text-sm rounded-full">
                      {toolData.tool}
                    </span>
                    <span className="text-sm text-text-muted">{toolData.count} uses</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Tasks by Date Chart */}
            <div className="bg-card rounded-xl border border-[rgba(255,255,255,0.08)] p-5">
              <h2 className="text-lg font-bold text-text-primary mb-4">Tasks (Last 7 Days)</h2>
              {analytics.tasks_by_date.length > 0 ? (
                <div className="flex items-end gap-2 h-48">
                  {analytics.tasks_by_date.slice(-7).map((data, idx) => {
                    const date = new Date(data.date);
                    const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
                    const maxCount = Math.max(...analytics.tasks_by_date.map((d) => d.count));
                    const height = maxCount > 0 ? (data.count / maxCount) * 100 : 0;
                    
                    return (
                      <div key={idx} className="flex-1 flex flex-col items-center gap-2">
                        <div
                          className="w-full bg-accent-blue rounded-t transition-all hover:opacity-80"
                          style={{ height: `${height}%` }}
                        ></div>
                        <span className="text-xs text-text-muted">{dayName}</span>
                        <span className="text-xs text-text-primary font-medium">{data.count}</span>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="text-center text-text-muted py-8">No task data available</p>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
