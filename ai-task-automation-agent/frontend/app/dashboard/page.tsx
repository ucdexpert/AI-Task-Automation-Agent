'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { useToast } from '@/lib/toast';
import { useRouter } from 'next/navigation';
import { getTasks, executeTask } from '@/lib/api';
import Link from 'next/link';
import {
  Bot,
  LogOut,
  BarChart3,
  Menu,
  X,
  Rocket,
  Mail,
  Globe,
  FolderOpen,
  Calendar,
  CheckCircle,
  XCircle,
  Loader2,
  Download,
  Search,
  UserCircle,
} from 'lucide-react';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

interface Task {
  id: number;
  status: 'completed' | 'failed' | 'processing';
  user_input: string;
  result: string | null;
  tools_used: string[];
  created_at: string;
  completed_at: string | null;
}

export default function DashboardPage() {
  const { user, logout, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const { addToast } = useToast();
  const [taskText, setTaskText] = useState('');
  const [runningTask, setRunningTask] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activities, setActivities] = useState<Task[]>([]);
  const [loadingTasks, setLoadingTasks] = useState(true);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'completed' | 'failed'>('all');

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    if (isAuthenticated) {
      loadTasks();
    }
  }, [isAuthenticated]);

  const loadTasks = async () => {
    try {
      setLoadingTasks(true);
      const data = await getTasks(0, 10);
      setActivities(data.tasks || []);
    } catch (error) {
      console.error('Failed to load tasks:', error);
      addToast('Failed to load tasks', 'error');
    } finally {
      setLoadingTasks(false);
    }
  };

  const handleLogout = () => {
    logout();
    addToast('Logged out successfully', 'info');
    router.push('/login');
  };

  const exportToCSV = () => {
    if (filteredTasks.length === 0) {
      addToast('No tasks to export', 'error');
      return;
    }

    const headers = ['ID', 'Status', 'Task', 'Tools Used', 'Created At', 'Completed At'];
    const rows = filteredTasks.map((task) => [
      task.id,
      task.status,
      `"${task.user_input.replace(/"/g, '""')}"`,
      `"${task.tools_used?.join(', ') || ''}"`,
      new Date(task.created_at).toLocaleString(),
      task.completed_at ? new Date(task.completed_at).toLocaleString() : 'N/A',
    ]);

    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `tasks_export_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    URL.revokeObjectURL(url);
    addToast(`Exported ${filteredTasks.length} tasks to CSV`, 'success');
  };

  const handleRunAutomation = async () => {
    if (!taskText.trim()) return;
    
    setRunningTask(true);
    try {
      const result = await executeTask(taskText, sessionId);
      addToast('Task completed successfully!', 'success');
      setTaskText('');
      await loadTasks();
      
      // Navigate to task detail
      router.push(`/task/${result.id}`);
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Task execution failed';
      addToast(message, 'error');
    } finally {
      setRunningTask(false);
    }
  };

  const handleQuickTask = (task: string) => {
    setTaskText(task);
    addToast(`Quick task loaded: "${task}"`, 'info');
  };

  const getFullName = () => {
    if (user?.full_name) return user.full_name;
    if (user?.email) return user.email.split('@')[0];
    return 'User';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  // Filter and search tasks
  const filteredTasks = activities.filter((task) => {
    const matchesSearch = searchQuery
      ? task.user_input.toLowerCase().includes(searchQuery.toLowerCase())
      : true;
    const matchesFilter = filterStatus === 'all' || task.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const quickTasks: Array<{ icons: string[]; text: string }> = [
    { icons: ['globe', 'code'], text: 'Scrape & summarize tech news' },
    { icons: ['doc'], text: 'Create a project report' },
    { icons: ['robot', 'sparkle'], text: 'Market research on AI' },
  ];

  return (
    <>
      {/* Loading State */}
      {isLoading ? (
        <div className="min-h-screen bg-background flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <div className="w-10 h-10 border-4 border-accent-blue border-t-transparent rounded-full animate-spin"></div>
            <p className="text-text-muted text-sm">Loading dashboard...</p>
          </div>
        </div>
      ) : !isAuthenticated ? null : (
        <div className="min-h-screen bg-background">
      {/* Navbar */}
      <nav className="sticky top-0 z-40 h-14 bg-background border-b border-[rgba(255,255,255,0.08)] px-4 md:px-6 flex items-center justify-between">
        {/* Left: Logo */}
        <div className="flex items-center gap-3">
          <div className="w-6 h-6 bg-gradient-to-br from-accent-blue to-accent-blueDark rounded flex items-center justify-center">
            <Bot className="w-4 h-4 text-white" />
          </div>
          <span className="text-base font-bold text-text-primary hidden sm:block">AI Task Automation</span>
        </div>

        {/* Right: Desktop */}
        <div className="hidden md:flex items-center gap-4">
          {/* User Name */}
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
            <span className="text-sm text-text-primary font-medium">{getFullName()}</span>
          </div>

          {/* Profile */}
          <Link
            href="/profile"
            className="flex items-center gap-2 px-3 h-9 border border-[rgba(255,255,255,0.08)] text-text-primary text-sm rounded-md hover:border-accent-blue transition-all"
          >
            <UserCircle className="w-4 h-4" />
            Profile
          </Link>

          {/* Logout */}
          <button
            onClick={handleLogout}
            className="text-sm text-accent-red hover:underline transition-all"
          >
            Logout
          </button>

          {/* Analytics */}
          <Link
            href="/analytics"
            className="flex items-center gap-2 px-3 h-9 border border-text-primary text-text-primary text-sm rounded-md hover:bg-text-primary hover:text-background transition-all"
          >
            <BarChart3 className="w-4 h-4" />
            Analytics
          </Link>
        </div>

        {/* Mobile Menu Toggle */}
        <button
          className="md:hidden p-2 text-text-primary hover:bg-card rounded"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle menu"
        >
          {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </nav>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-card border-b border-[rgba(255,255,255,0.08)] px-4 py-4 animate-slide-down">
          <div className="flex flex-col gap-3">
            <div className="flex items-center gap-2 pb-3 border-b border-[rgba(255,255,255,0.08)]">
              <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
              <span className="text-sm text-text-primary font-medium">{getFullName()}</span>
            </div>
            <Link
              href="/profile"
              className="flex items-center gap-2 px-3 py-2 border border-[rgba(255,255,255,0.08)] text-text-primary text-sm rounded-md hover:border-accent-blue transition-all"
              onClick={() => setMobileMenuOpen(false)}
            >
              <UserCircle className="w-4 h-4" />
              Profile
            </Link>
            <button
              onClick={handleLogout}
              className="text-sm text-accent-red hover:underline text-left py-2"
            >
              Logout
            </button>
            <Link
              href="/analytics"
              className="flex items-center gap-2 px-3 py-2 border border-text-primary text-text-primary text-sm rounded-md hover:bg-text-primary hover:text-background transition-all"
              onClick={() => setMobileMenuOpen(false)}
            >
              <BarChart3 className="w-4 h-4" />
              Analytics
            </Link>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="px-4 md:px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-[65%_35%] gap-6">
          {/* Left Column */}
          <div className="space-y-6">
            {/* Task Input Card */}
            <div className="bg-card rounded-xl border border-[rgba(255,255,255,0.08)] p-5">
              <div className="relative">
                <textarea
                  value={taskText}
                  onChange={(e) => setTaskText(e.target.value)}
                  placeholder="Describe your task here... (e.g. Scrape AI news and summarize)"
                  className="w-full min-h-[120px] p-4 bg-background border-0 rounded-lg text-text-primary placeholder-text-muted text-[15px] resize-none focus:outline-none focus:ring-2 focus:ring-accent-blue"
                  style={{ fontFamily: 'inherit' }}
                />
                <div className="absolute bottom-3 right-3 text-xs text-text-muted">
                  {taskText.length} characters
                </div>
              </div>

              {/* Bottom Bar */}
              <div className="flex items-center justify-between mt-4">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-accent-green animate-pulse-dot"></div>
                  <span className="text-xs text-text-muted">AI Engine Ready</span>
                </div>

                <button
                  onClick={handleRunAutomation}
                  disabled={!taskText.trim() || runningTask}
                  className={`h-11 px-5 rounded-lg font-medium flex items-center gap-2 transition-all duration-200 ${
                    taskText.trim() && !runningTask
                      ? 'bg-gradient-to-r from-accent-blue to-accent-blueDark text-white hover:opacity-90'
                      : 'bg-[#374151] text-text-muted cursor-not-allowed'
                  }`}
                >
                  {runningTask ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Running...</span>
                    </>
                  ) : (
                    <>
                      <Rocket className="w-5 h-5" />
                      <span>Run Automation</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="mt-8">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-text-primary">Recent Activity</h2>
                <div className="flex items-center gap-3">
                  <span className="text-sm text-text-muted">{filteredTasks.length} tasks</span>
                  {filteredTasks.length > 0 && (
                    <button
                      onClick={exportToCSV}
                      className="flex items-center gap-2 px-3 py-1.5 bg-card border border-[rgba(255,255,255,0.08)] rounded-lg text-sm text-text-muted hover:text-text-primary hover:border-accent-blue transition-all"
                      title="Export to CSV"
                    >
                      <Download className="w-4 h-4" />
                      Export
                    </button>
                  )}
                </div>
              </div>

              {/* Search & Filter */}
              {activities.length > 0 && (
                <div className="mb-4 space-y-3">
                  {/* Search Bar */}
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search tasks..."
                    className="w-full px-4 py-2.5 bg-background border border-[rgba(255,255,255,0.08)] rounded-lg text-text-primary placeholder-text-muted text-sm focus:outline-none focus:ring-2 focus:ring-accent-blue"
                  />

                  {/* Filter Buttons */}
                  <div className="flex gap-2">
                    {(['all', 'completed', 'failed'] as const).map((status) => (
                      <button
                        key={status}
                        onClick={() => setFilterStatus(status)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                          filterStatus === status
                            ? 'bg-accent-blue text-white'
                            : 'bg-card border border-[rgba(255,255,255,0.08)] text-text-muted hover:text-text-primary'
                        }`}
                      >
                        {status.charAt(0).toUpperCase() + status.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {loadingTasks ? (
                <div className="flex items-center justify-center py-12">
                  <LoadingSpinner size="md" />
                </div>
              ) : filteredTasks.length === 0 ? (
                <div className="border-2 border-dashed border-[rgba(255,255,255,0.15)] rounded-xl p-8 text-center">
                  <p className="text-text-muted text-sm">
                    No automations yet — run your first task above
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredTasks.map((task) => (
                    <div
                      key={task.id}
                      className="bg-card rounded-xl border border-[rgba(255,255,255,0.08)] p-4"
                    >
                      {/* Top Row */}
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {task.status === 'completed' ? (
                            <>
                              <CheckCircle className="w-4 h-4 text-accent-green" />
                              <span className="text-sm text-accent-green font-medium">Completed</span>
                            </>
                          ) : task.status === 'failed' ? (
                            <>
                              <XCircle className="w-4 h-4 text-accent-red" />
                              <span className="text-sm text-accent-red font-medium">Failed</span>
                            </>
                          ) : (
                            <>
                              <Loader2 className="w-4 h-4 text-yellow-500 animate-spin" />
                              <span className="text-sm text-yellow-500 font-medium">Processing</span>
                            </>
                          )}
                        </div>
                        <span className="text-xs text-text-muted">{formatDate(task.created_at)}</span>
                      </div>

                      {/* Task Description */}
                      <p className="text-sm font-semibold text-text-primary mt-2 line-clamp-2">
                        {task.user_input}
                      </p>

                      {/* Result Preview */}
                      {task.result && (
                        <p className="text-xs text-text-muted mt-1 line-clamp-1 overflow-hidden text-ellipsis">
                          {task.result}
                        </p>
                      )}

                      {/* Bottom Row */}
                      <div className="flex items-center justify-between mt-3">
                        <div className="flex gap-2">
                          {task.tools_used?.slice(0, 2).map((tool, idx) => (
                            <span
                              key={idx}
                              className="inline-block px-3 py-0.5 bg-[#1E3A5F] text-[#60A5FA] text-[11px] rounded-full"
                            >
                              {tool}
                            </span>
                          ))}
                        </div>
                        <Link
                          href={`/task/${task.id}`}
                          className="text-sm text-accent-blue hover:underline"
                        >
                          View Details →
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right Column */}
          <div className="space-y-4">
            {/* Quick Tasks Card */}
            <div className="bg-gradient-to-br from-[#1D4ED8] to-accent-blue rounded-xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <Rocket className="w-5 h-5 text-white" />
                <h3 className="text-lg font-bold text-white">Quick Tasks</h3>
              </div>

              <div className="space-y-3">
                {quickTasks.map((task, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleQuickTask(task.text)}
                    className="w-full px-4 py-3 bg-white/12 hover:bg-white/20 rounded-lg transition-all flex items-center gap-2.5 text-sm text-white text-left"
                  >
                    {task.icons.includes('globe') && <Globe className="w-4 h-4" />}
                    {task.icons.includes('code') && <Rocket className="w-4 h-4" />}
                    {task.icons.includes('doc') && <FolderOpen className="w-4 h-4" />}
                    {task.icons.includes('robot') && <Bot className="w-4 h-4" />}
                    {task.text}
                  </button>
                ))}
              </div>
            </div>

            {/* Toolbelt Card */}
            <div className="bg-card rounded-xl border border-[rgba(255,255,255,0.08)] p-5">
              <h3 className="text-base font-bold text-text-primary mb-4 flex items-center gap-2">
                🔧 Toolbelt
              </h3>

              <div className="grid grid-cols-2 gap-3">
                <button className="bg-background rounded-lg border border-[rgba(255,255,255,0.08)] p-4 flex flex-col items-center gap-2 hover:border-accent-blue transition-all cursor-pointer">
                  <Mail className="w-5 h-5 text-accent-blue" />
                  <span className="text-xs text-text-muted">Email</span>
                </button>

                <button className="bg-background rounded-lg border border-[rgba(255,255,255,0.08)] p-4 flex flex-col items-center gap-2 hover:border-accent-blue transition-all cursor-pointer">
                  <Globe className="w-5 h-5 text-purple-500" />
                  <span className="text-xs text-text-muted">Web</span>
                </button>

                <button className="bg-background rounded-lg border border-[rgba(255,255,255,0.08)] p-4 flex flex-col items-center gap-2 hover:border-accent-blue transition-all cursor-pointer">
                  <FolderOpen className="w-5 h-5 text-yellow-500" />
                  <span className="text-xs text-text-muted">Files</span>
                </button>

                <button className="bg-background rounded-lg border border-[rgba(255,255,255,0.08)] p-4 flex flex-col items-center gap-2 hover:border-accent-blue transition-all cursor-pointer">
                  <Calendar className="w-5 h-5 text-accent-green" />
                  <span className="text-xs text-text-muted">Calendar</span>
                </button>
              </div>
            </div>

            {/* Power User Tip Card */}
            <div className="bg-card rounded-xl border border-[rgba(255,255,255,0.08)] p-5 relative">
              <div className="absolute top-2 right-3 text-5xl font-bold text-[rgba(255,255,255,0.06)] select-none">
                PRO
              </div>
              <h3 className="text-sm font-bold text-text-primary mb-2">Power User Tip</h3>
              <p className="text-xs text-text-muted leading-relaxed">
                You can ask the agent to chain multiple steps together, like "Scrape X, summarize it, and save to Y.txt".
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
      )}
    </>
  );
}
