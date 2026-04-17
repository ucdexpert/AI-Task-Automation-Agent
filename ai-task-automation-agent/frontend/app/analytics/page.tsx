'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { getAnalytics } from '@/lib/api';
import { 
  ArrowLeft, 
  BarChart3, 
  Zap, 
  Target, 
  TrendingUp, 
  Clock, 
  Activity,
  Box
} from 'lucide-react';
import Link from 'next/link';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area
} from 'recharts';

interface AnalyticsData {
  total_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  success_rate: number;
  avg_execution_time_ms: number | null;
  most_used_tools: Array<{ tool: string; count: number }>;
  tasks_by_date: Array<{ date: string; count: number }>;
}

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

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

  const pieData = analytics ? [
    { name: 'Completed', value: analytics.completed_tasks },
    { name: 'Failed', value: analytics.failed_tasks },
  ] : [];

  return (
    <div className="min-h-screen bg-background px-4 md:px-6 py-8">
      <div className="max-w-[1000px] mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-accent-blue/10 rounded-2xl flex items-center justify-center">
              <BarChart3 className="w-7 h-7 text-accent-blue" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-text-primary">Analytics Insight</h1>
              <p className="text-sm text-text-muted">Real-time performance and agent metrics</p>
            </div>
          </div>
          <Link
            href="/dashboard"
            className="flex items-center gap-2 px-5 h-11 bg-card border border-white/10 text-text-primary text-sm font-bold rounded-xl hover:bg-white/5 transition-all"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
        </div>

        {isLoading || loading || !analytics ? (
          <div className="flex flex-col items-center justify-center py-32 gap-4">
            <div className="animate-spin w-10 h-10 border-4 border-accent-blue border-t-transparent rounded-full"></div>
            <p className="text-text-muted animate-pulse">Calculating metrics...</p>
          </div>
        ) : (
          <>
            {/* Top Stats Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              <div className="bg-card rounded-2xl border border-white/5 p-6 relative overflow-hidden group">
                <div className="absolute -right-2 -bottom-2 opacity-5 group-hover:scale-110 transition-transform">
                  <Activity className="w-20 h-20" />
                </div>
                <p className="text-[10px] font-bold text-text-muted uppercase tracking-widest mb-1">Total Tasks</p>
                <p className="text-3xl font-bold text-text-primary">{analytics.total_tasks}</p>
                <div className="mt-2 flex items-center gap-1 text-[10px] text-accent-green font-bold">
                  <TrendingUp className="w-3 h-3" />
                  <span>All Time</span>
                </div>
              </div>

              <div className="bg-card rounded-2xl border border-white/5 p-6 relative overflow-hidden group">
                <div className="absolute -right-2 -bottom-2 opacity-5 group-hover:scale-110 transition-transform text-accent-green">
                  <Target className="w-20 h-20" />
                </div>
                <p className="text-[10px] font-bold text-text-muted uppercase tracking-widest mb-1">Success Rate</p>
                <p className="text-3xl font-bold text-accent-green">{analytics.success_rate.toFixed(1)}%</p>
                <div className="mt-2 h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                   <div className="h-full bg-accent-green rounded-full" style={{ width: `${analytics.success_rate}%` }}></div>
                </div>
              </div>

              <div className="bg-card rounded-2xl border border-white/5 p-6 relative overflow-hidden group">
                <div className="absolute -right-2 -bottom-2 opacity-5 group-hover:scale-110 transition-transform text-accent-blue">
                  <Clock className="w-20 h-20" />
                </div>
                <p className="text-[10px] font-bold text-text-muted uppercase tracking-widest mb-1">Avg Speed</p>
                <p className="text-3xl font-bold text-accent-blue">
                  {analytics.avg_execution_time_ms ? (analytics.avg_execution_time_ms / 1000).toFixed(1) : '0'}s
                </p>
                <p className="text-[10px] text-text-muted mt-2 font-bold uppercase tracking-tighter">Per Step Average</p>
              </div>

              <div className="bg-card rounded-2xl border border-white/5 p-6 relative overflow-hidden group">
                <div className="absolute -right-2 -bottom-2 opacity-5 group-hover:scale-110 transition-transform text-yellow-500">
                  <Zap className="w-20 h-20" />
                </div>
                <p className="text-[10px] font-bold text-text-muted uppercase tracking-widest mb-1">Efficiency</p>
                <p className="text-3xl font-bold text-yellow-500">OPTIMAL</p>
                <p className="text-[10px] text-text-muted mt-2 font-bold uppercase tracking-tighter">Engine Status</p>
              </div>
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {/* Task Activity Chart */}
              <div className="bg-card rounded-2xl border border-white/5 p-6">
                <h2 className="text-sm font-bold text-text-primary uppercase tracking-wider mb-6 flex items-center gap-2">
                  <Activity className="w-4 h-4 text-accent-blue" />
                  Task Activity (Last 7 Days)
                </h2>
                <div className="h-[250px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={analytics.tasks_by_date}>
                      <defs>
                        <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                      <XAxis 
                        dataKey="date" 
                        axisLine={false} 
                        tickLine={false} 
                        tick={{ fill: '#64748B', fontSize: 10 }}
                        tickFormatter={(val) => new Date(val).toLocaleDateString('en-US', { weekday: 'short' })}
                      />
                      <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748B', fontSize: 10 }} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#1A1D27', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '12px' }}
                        itemStyle={{ color: '#F1F5F9' }}
                      />
                      <Area type="monotone" dataKey="count" stroke="#3B82F6" strokeWidth={3} fillOpacity={1} fill="url(#colorCount)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Success Ratio (Pie Chart) */}
              <div className="bg-card rounded-2xl border border-white/5 p-6">
                <h2 className="text-sm font-bold text-text-primary uppercase tracking-wider mb-6 flex items-center gap-2">
                  <Target className="w-4 h-4 text-accent-green" />
                  Execution Success Ratio
                </h2>
                <div className="h-[250px] w-full flex items-center justify-center relative">
                   <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <p className="text-2xl font-bold text-text-primary">{analytics.success_rate.toFixed(0)}%</p>
                      <p className="text-[10px] text-text-muted font-bold uppercase">Success</p>
                   </div>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        <Cell key="completed" fill="#10B981" />
                        <Cell key="failed" fill="#EF4444" />
                      </Pie>
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#1A1D27', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '12px' }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Bottom Row: Tool Usage */}
            <div className="bg-card rounded-2xl border border-white/5 p-6">
              <h2 className="text-sm font-bold text-text-primary uppercase tracking-wider mb-6 flex items-center gap-2">
                <Box className="w-4 h-4 text-yellow-500" />
                Tool Popularity Ranking
              </h2>
              <div className="h-[300px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={analytics.most_used_tools} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                    <XAxis type="number" axisLine={false} tickLine={false} tick={{ fill: '#64748B', fontSize: 10 }} />
                    <YAxis dataKey="tool" type="category" axisLine={false} tickLine={false} tick={{ fill: '#F1F5F9', fontSize: 11 }} width={100} />
                    <Tooltip 
                      cursor={{ fill: 'rgba(255,255,255,0.02)' }}
                      contentStyle={{ backgroundColor: '#1A1D27', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '12px' }}
                    />
                    <Bar dataKey="count" radius={[0, 4, 4, 0]} barSize={20}>
                      {analytics.most_used_tools.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
