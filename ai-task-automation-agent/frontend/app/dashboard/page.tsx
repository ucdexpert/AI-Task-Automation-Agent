'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { useToast } from '@/lib/toast';
import { useRouter } from 'next/navigation';
import { getTasks, executeTask } from '@/lib/api';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
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
  Sparkles,
  Zap,
  ArrowRight,
  Activity,
  Target,
  TrendingUp,
  Clock
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
  const { user, logout, isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const { addToast } = useToast();
  const queryClient = useQueryClient();
  
  const [taskText, setTaskText] = useState('');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'completed' | 'failed'>('all');

  // TanStack Query for fetching tasks
  const { data: tasksData, isLoading: tasksLoading } = useQuery({
    queryKey: ['tasks'],
    queryFn: () => getTasks(0, 50),
    enabled: isAuthenticated,
    refetchInterval: 5000,
  });

  const activities = (tasksData?.tasks || []).sort((a: Task, b: Task) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  // TanStack Mutation for executing task
  const executeMutation = useMutation({
    mutationFn: (text: string) => executeTask(text, sessionId),
    onSuccess: (result) => {
      addToast('Automation sequence initiated!', 'success');
      setTaskText('');
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      router.push(`/task/${result.id}`);
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Task execution failed';
      addToast(message, 'error');
    }
  });

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, authLoading, router]);

  const handleLogout = () => {
    logout();
    addToast('Logged out successfully', 'info');
    router.push('/login');
  };

  const handleRunAutomation = () => {
    if (!taskText.trim()) return;
    executeMutation.mutate(taskText);
  };

  const handleQuickAction = (prompt: string) => {
    setTaskText(prompt);
    addToast('Prompt loaded! Ready to run.', 'info');
  };

  const getFullName = () => {
    if (user?.full_name) return user.full_name;
    if (user?.email) return user.email.split('@')[0];
    return 'User';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const filteredTasks = activities.filter((task: Task) => {
    const matchesSearch = searchQuery
      ? task.user_input.toLowerCase().includes(searchQuery.toLowerCase())
      : true;
    const matchesFilter = filterStatus === 'all' || task.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  return (
    <>
      {authLoading ? (
        <div className="min-h-screen bg-[#0A0C10] flex items-center justify-center">
          <LoadingSpinner size="lg" />
        </div>
      ) : !isAuthenticated ? null : (
        <div className="min-h-screen bg-[#0A0C10] text-slate-200 selection:bg-accent-blue/30 font-sans">
          {/* Animated Background Blob */}
          <div className="fixed inset-0 overflow-hidden pointer-events-none">
            <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-accent-blue/5 blur-[120px] rounded-full animate-pulse"></div>
            <div className="absolute top-[20%] -right-[5%] w-[30%] h-[30%] bg-purple-600/5 blur-[100px] rounded-full animate-pulse delay-700"></div>
          </div>

          {/* Navbar */}
          <nav className="sticky top-0 z-50 backdrop-blur-xl bg-[#0A0C10]/70 border-b border-white/5 px-6 h-16 flex items-center justify-between">
            <div className="flex items-center gap-3 group cursor-pointer">
              <div className="w-8 h-8 bg-gradient-to-tr from-accent-blue to-purple-500 rounded-lg flex items-center justify-center shadow-lg shadow-accent-blue/20 group-hover:scale-110 transition-transform">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-black tracking-tight text-white uppercase italic">Agent<span className="text-accent-blue">X</span></span>
            </div>

            <div className="hidden md:flex items-center gap-6">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-white/5 rounded-full border border-white/5">
                <div className="w-2 h-2 rounded-full bg-accent-green animate-pulse"></div>
                <span className="text-xs font-bold text-slate-300">{getFullName()}</span>
              </div>
              <Link href="/analytics" className="text-sm font-bold text-slate-400 hover:text-white transition-colors flex items-center gap-2">
                <BarChart3 className="w-4 h-4" /> Analytics
              </Link>
              <Link href="/profile" className="text-sm font-bold text-slate-400 hover:text-white transition-colors flex items-center gap-2">
                <UserCircle className="w-4 h-4" /> Profile
              </Link>
              <button onClick={handleLogout} className="text-sm font-bold text-accent-red/80 hover:text-accent-red transition-colors">
                Logout
              </button>
            </div>
            
            <button className="md:hidden p-2 text-slate-300" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
              {mobileMenuOpen ? <X /> : <Menu />}
            </button>
          </nav>

          {/* Mobile Menu Dropdown */}
          {mobileMenuOpen && (
            <div className="md:hidden fixed inset-0 z-40 bg-[#0A0C10]/95 backdrop-blur-2xl animate-in fade-in duration-300">
               <div className="flex flex-col items-center justify-center h-full gap-8">
                  <Link href="/analytics" onClick={() => setMobileMenuOpen(false)} className="text-2xl font-black text-white flex items-center gap-3">
                    <BarChart3 className="w-6 h-6 text-accent-blue" /> Analytics
                  </Link>
                  <Link href="/profile" onClick={() => setMobileMenuOpen(false)} className="text-2xl font-black text-white flex items-center gap-3">
                    <UserCircle className="w-6 h-6 text-accent-blue" /> Profile
                  </Link>
                  <button onClick={handleLogout} className="text-2xl font-black text-accent-red flex items-center gap-3">
                    <LogOut className="w-6 h-6" /> Logout
                  </button>
                  <button onClick={() => setMobileMenuOpen(false)} className="mt-10 w-14 h-14 bg-white/5 rounded-full flex items-center justify-center border border-white/10">
                    <X className="w-6 h-6 text-white" />
                  </button>
               </div>
            </div>
          )}

          {/* Main Content */}
          <main className="relative z-10 max-w-7xl mx-auto px-6 py-8">
            
            {/* Stats Header */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
              {[
                { label: 'Total Executions', value: activities.length, icon: Activity, color: 'text-accent-blue' },
                { label: 'Success Rate', value: `${activities.length > 0 ? Math.round((activities.filter(t => t.status === 'completed').length / activities.length) * 100) : 0}%`, icon: Target, color: 'text-accent-green' },
                { label: 'Active Pipeline', value: activities.filter(t => t.status === 'processing').length, icon: Zap, color: 'text-yellow-500' },
                { label: 'System Status', value: 'Healthy', icon: CheckCircle, color: 'text-accent-blue' },
              ].map((stat, i) => (
                <div key={i} className="bg-white/[0.03] backdrop-blur-md border border-white/5 rounded-2xl p-4 transition-all hover:bg-white/[0.05]">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">{stat.label}</p>
                    <stat.icon className={`w-4 h-4 ${stat.color}`} />
                  </div>
                  <p className="text-2xl font-bold text-white">{stat.value}</p>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              {/* Left: Input & History (8 Cols) */}
              <div className="lg:col-span-8 space-y-8">
                
                {/* Command Center */}
                <div className="relative group">
                  <div className="absolute -inset-1 bg-gradient-to-r from-accent-blue to-purple-600 rounded-3xl blur opacity-10 group-hover:opacity-20 transition duration-1000"></div>
                  <div className="relative bg-[#11141B] border border-white/10 rounded-3xl p-6 shadow-2xl">
                    <div className="flex items-center gap-2 mb-4">
                      <Sparkles className="w-5 h-5 text-accent-blue" />
                      <h2 className="text-sm font-bold text-white uppercase tracking-tighter">Command Center</h2>
                    </div>
                    
                    <textarea
                      value={taskText}
                      onChange={(e) => setTaskText(e.target.value)}
                      placeholder="What should the agent do next? (e.g., 'Research latest AI trends and WhatsApp me')"
                      className="w-full min-h-[140px] bg-transparent border-0 text-white placeholder-slate-600 text-lg resize-none focus:ring-0"
                    />

                    <div className="flex items-center justify-between pt-4 border-t border-white/5">
                      <div className="flex items-center gap-4">
                        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                          {taskText.length} characters
                        </span>
                      </div>
                      
                      <button
                        onClick={handleRunAutomation}
                        disabled={!taskText.trim() || executeMutation.isPending}
                        className="group flex items-center gap-2 bg-accent-blue hover:bg-accent-blueDark disabled:bg-slate-800 text-white px-6 py-3 rounded-2xl font-black text-sm transition-all shadow-xl shadow-accent-blue/20"
                      >
                        {executeMutation.isPending ? (
                          <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                          <>Execute <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" /></>
                        )}
                      </button>
                    </div>
                  </div>
                </div>

                {/* History Section */}
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                      Recent Activity <span className="text-xs bg-white/5 px-2 py-0.5 rounded text-slate-500">{filteredTasks.length}</span>
                    </h2>
                    
                    <div className="flex gap-2">
                      {['all', 'completed', 'failed'].map((s) => (
                        <button
                          key={s}
                          onClick={() => setFilterStatus(s as any)}
                          className={`px-3 py-1.5 rounded-lg text-[10px] font-black uppercase transition-all ${
                            filterStatus === s ? 'bg-white/10 text-white border border-white/10' : 'text-slate-500 hover:text-slate-300'
                          }`}
                        >
                          {s}
                        </button>
                      ))}
                    </div>
                  </div>

                  {tasksLoading ? (
                    <div className="grid grid-cols-1 gap-4">
                       {[1,2,3].map(i => <div key={i} className="h-32 bg-white/[0.02] rounded-2xl animate-pulse border border-white/5"></div>)}
                    </div>
                  ) : filteredTasks.length === 0 ? (
                    <div className="bg-white/[0.01] border-2 border-dashed border-white/5 rounded-[40px] p-20 text-center">
                        <Rocket className="w-12 h-12 text-slate-700 mx-auto mb-4" />
                        <p className="text-slate-500 font-medium">No commands in history. System ready for input.</p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 gap-4">
                      {filteredTasks.map((task: Task) => (
                        <Link 
                          href={`/task/${task.id}`} 
                          key={task.id}
                          className="group relative bg-[#11141B] border border-white/5 rounded-2xl p-5 hover:border-white/10 hover:bg-[#161A23] transition-all overflow-hidden"
                        >
                          {task.status === 'processing' && (
                            <div className="absolute top-0 left-0 right-0 h-[2px] bg-accent-blue/20 overflow-hidden">
                              <div className="h-full bg-accent-blue animate-progress-indefinite"></div>
                            </div>
                          )}
                          
                          <div className="flex items-start justify-between">
                            <div className="space-y-3 flex-1">
                              <div className="flex items-center gap-2">
                                <div className={`w-1.5 h-1.5 rounded-full ${
                                  task.status === 'completed' ? 'bg-accent-green' : task.status === 'failed' ? 'bg-accent-red' : 'bg-yellow-500 animate-pulse'
                                }`}></div>
                                <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">{task.status}</span>
                                <span className="text-[10px] font-mono text-slate-600">ID-{task.id}</span>
                              </div>
                              <p className="text-sm font-bold text-slate-200 line-clamp-1 group-hover:text-white transition-colors">{task.user_input}</p>
                              
                              <div className="flex items-center gap-2">
                                {task.tools_used?.map(t => (
                                  <span key={t} className="px-2 py-0.5 bg-white/5 text-[9px] font-black text-slate-400 rounded uppercase border border-white/5">{t}</span>
                                ))}
                              </div>
                            </div>
                            
                            <div className="text-right">
                              <p className="text-[10px] font-bold text-slate-600">{formatDate(task.created_at)}</p>
                              <ArrowRight className="w-4 h-4 text-slate-700 mt-4 ml-auto group-hover:text-accent-blue transition-colors" />
                            </div>
                          </div>
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Right: Tools & Tips (4 Cols) */}
              <div className="lg:col-span-4 space-y-6">
                
                {/* Interactive Toolbelt */}
                <div className="bg-[#11141B] border border-white/5 rounded-3xl p-6">
                  <h3 className="text-xs font-black text-white uppercase tracking-widest mb-6">Smart Toolbelt</h3>
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      { name: 'WhatsApp', icon: Mail, color: 'text-accent-green', prompt: 'Send a WhatsApp to 923170219387: ' },
                      { name: 'Web Search', icon: Globe, color: 'text-accent-blue', prompt: 'Research about ' },
                      { name: 'Calendar', icon: Calendar, color: 'text-purple-500', prompt: 'Schedule a meeting for tomorrow at 10 AM: ' },
                      { name: 'Data Scrape', icon: FolderOpen, color: 'text-yellow-500', prompt: 'Scrape this URL and summarize: ' },
                    ].map((tool) => (
                      <button
                        key={tool.name}
                        onClick={() => handleQuickAction(tool.prompt)}
                        className="flex flex-col items-center gap-3 p-4 rounded-2xl bg-white/5 border border-white/5 hover:border-white/20 hover:bg-white/[0.08] transition-all group"
                      >
                        <tool.icon className={`w-6 h-6 ${tool.color} group-hover:scale-110 transition-transform`} />
                        <span className="text-[10px] font-black text-slate-400 uppercase tracking-tighter">{tool.name}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Quick Prompts */}
                <div className="bg-gradient-to-br from-accent-blue/10 to-purple-600/10 border border-white/5 rounded-3xl p-6">
                   <h3 className="text-xs font-black text-white uppercase tracking-widest mb-4">Quick Templates</h3>
                   <div className="space-y-2">
                     {[
                       "Research latest cricket news and WhatsApp me",
                       "Check my calendar for today",
                       "Scrape tech news and email a summary",
                     ].map((p, i) => (
                       <button
                        key={i}
                        onClick={() => handleQuickAction(p)}
                        className="w-full text-left p-3 rounded-xl bg-black/20 hover:bg-black/40 text-[11px] font-medium text-slate-400 border border-white/5 transition-all"
                       >
                         {p}
                       </button>
                     ))}
                   </div>
                </div>

                {/* System Tip */}
                <div className="p-6 bg-white/[0.02] rounded-3xl border border-white/5">
                  <div className="flex items-center gap-2 mb-2 text-accent-blue">
                    <Sparkles className="w-4 h-4" />
                    <span className="text-[10px] font-black uppercase tracking-widest">Pro Tip</span>
                  </div>
                  <p className="text-xs text-slate-500 leading-relaxed italic">
                    "You can ask the agent to chain tools, like 'Search for X, then WhatsApp the summary to me'."
                  </p>
                </div>

              </div>
            </div>
          </main>
        </div>
      )}
    </>
  );
}
