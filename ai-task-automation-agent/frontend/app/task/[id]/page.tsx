'use client';

import { useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useToast } from '@/lib/toast';
import { getTask, deleteTask, getTaskLogs } from '@/lib/api';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  CheckCircle,
  XCircle,
  ArrowLeft,
  Trash2,
  ChevronDown,
  ChevronRight,
  Loader2,
  Clock,
  Terminal,
  Activity,
  FileText,
  AlertCircle,
  Rocket
} from 'lucide-react';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

interface TaskData {
  id: number;
  status: 'completed' | 'failed' | 'processing';
  user_input: string;
  result: string | null;
  tools_used: string[];
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
}

interface LogEntry {
  id: number;
  task_id: number;
  step_number: number;
  action: string;
  input_data: any;
  output_data: any;
  status: string;
  execution_time_ms: number | null;
  created_at: string;
}

export default function TaskDetailPage() {
  const router = useRouter();
  const params = useParams();
  const { addToast } = useToast();
  const queryClient = useQueryClient();
  const taskId = Number(params.id);

  const [expandedSections, setExpandedSections] = useState<{ [key: string]: boolean }>({});

  // 1. Fetch Task Details with automatic polling if processing
  const { data: task, isLoading: taskLoading, error: taskError } = useQuery({
    queryKey: ['task', taskId],
    queryFn: () => getTask(taskId),
    refetchInterval: (query) => {
      // @ts-ignore
      return query.state.data?.status === 'processing' ? 3000 : false;
    },
    enabled: !!taskId,
  });

  // 2. Fetch Task Logs
  const { data: logs = [], isLoading: logsLoading } = useQuery({
    queryKey: ['logs', taskId],
    queryFn: () => getTaskLogs(taskId),
    enabled: !!taskId,
    refetchInterval: (query) => {
      return task?.status === 'processing' ? 3000 : false;
    },
  });

  // 3. Delete Mutation
  const deleteMutation = useMutation({
    mutationFn: () => deleteTask(taskId),
    onSuccess: () => {
      addToast('Task deleted successfully', 'success');
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      router.push('/dashboard');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to delete task';
      addToast(message, 'error');
    }
  });

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  const handleBack = () => {
    router.push('/dashboard');
  };

  if (taskLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <LoadingSpinner size="lg" />
          <p className="text-text-muted text-sm">Fetching task details...</p>
        </div>
      </div>
    );
  }

  if (taskError || !task) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4 text-center">
        <div className="max-w-md">
          <AlertCircle className="w-12 h-12 text-accent-red mx-auto mb-4" />
          <h2 className="text-xl font-bold text-text-primary mb-2">Task Not Found</h2>
          <p className="text-text-muted mb-6">The task you're looking for doesn't exist or has been deleted.</p>
          <button
            onClick={handleBack}
            className="px-6 py-2.5 bg-accent-blue text-white rounded-lg font-medium hover:opacity-90 transition-all"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background px-4 md:px-6 py-8">
      <div className="max-w-[900px] mx-auto">
        {/* Breadcrumbs & Navigation */}
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={handleBack}
            className="flex items-center gap-2 text-text-muted hover:text-text-primary transition-colors text-sm font-medium group"
          >
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            Back to Dashboard
          </button>

          <div className="flex items-center gap-3">
            <button
              onClick={() => deleteMutation.mutate()}
              disabled={deleteMutation.isPending}
              className="flex items-center gap-2 px-4 py-2 bg-accent-red/10 text-accent-red hover:bg-accent-red/20 disabled:opacity-50 text-sm font-bold rounded-lg transition-all"
            >
              {deleteMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
              Delete Task
            </button>
          </div>
        </div>

        {/* Task Title & Status Header */}
        <div className="bg-card rounded-2xl border border-[rgba(255,255,255,0.08)] p-6 mb-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-2xl font-bold text-text-primary">Task #{task.id}</h1>
                <div className={`px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1.5 ${
                  task.status === 'completed' ? 'bg-accent-green/10 text-accent-green' :
                  task.status === 'failed' ? 'bg-accent-red/10 text-accent-red' :
                  'bg-yellow-500/10 text-yellow-500'
                }`}>
                  {task.status === 'completed' && <CheckCircle className="w-3.5 h-3.5" />}
                  {task.status === 'failed' && <XCircle className="w-3.5 h-3.5" />}
                  {task.status === 'processing' && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  {task.status.toUpperCase()}
                </div>
              </div>
              <p className="text-sm text-text-muted flex items-center gap-2">
                <Clock className="w-3.5 h-3.5" />
                Started on {new Date(task.created_at).toLocaleString()}
              </p>
            </div>
            
            {task.completed_at && (
              <div className="text-left md:text-right">
                <p className="text-xs text-text-muted mb-1 uppercase tracking-wider font-semibold">Completed in</p>
                <p className="text-sm text-text-primary font-mono">
                  {Math.round((new Date(task.completed_at).getTime() - new Date(task.created_at).getTime()) / 1000)}s
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Main Content (2/3) */}
          <div className="md:col-span-2 space-y-6">
            {/* Task Description */}
            <div className="bg-card rounded-2xl border border-[rgba(255,255,255,0.08)] overflow-hidden">
              <div className="px-6 py-4 border-b border-[rgba(255,255,255,0.08)] bg-white/[0.02] flex items-center gap-2">
                <FileText className="w-4 h-4 text-accent-blue" />
                <h2 className="text-sm font-bold text-text-primary uppercase tracking-wider">Instruction</h2>
              </div>
              <div className="p-6">
                <p className="text-text-primary text-[15px] leading-relaxed whitespace-pre-wrap">
                  {task.user_input}
                </p>
              </div>
            </div>

            {/* Final Result */}
            {(task.result || task.error_message) && (
              <div className={`bg-card rounded-2xl border overflow-hidden ${
                task.status === 'failed' ? 'border-accent-red/30' : 'border-[rgba(255,255,255,0.08)]'
              }`}>
                <div className="px-6 py-4 border-b border-[rgba(255,255,255,0.08)] bg-white/[0.02] flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Activity className="w-4 h-4 text-accent-green" />
                    <h2 className="text-sm font-bold text-text-primary uppercase tracking-wider">Output</h2>
                  </div>
                  {task.status === 'completed' && (
                    <span className="text-[10px] bg-accent-green/20 text-accent-green px-2 py-0.5 rounded font-bold">FINAL</span>
                  )}
                </div>
                <div className="p-6">
                  {task.error_message ? (
                    <div className="bg-accent-red/5 rounded-xl p-4 border border-accent-red/10 text-accent-red text-sm">
                      <p className="font-bold mb-1 flex items-center gap-2">
                        <AlertCircle className="w-4 h-4" />
                        Execution Error
                      </p>
                      {task.error_message}
                    </div>
                  ) : (
                    <div className="bg-background/50 rounded-xl p-5 border border-[rgba(255,255,255,0.05)]">
                      <p className="text-text-primary text-[15px] leading-relaxed whitespace-pre-wrap">
                        {task.result}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Execution Logs */}
            <div className="bg-card rounded-2xl border border-[rgba(255,255,255,0.08)] overflow-hidden">
              <div className="px-6 py-4 border-b border-[rgba(255,255,255,0.08)] bg-white/[0.02] flex items-center gap-2">
                <Terminal className="w-4 h-4 text-yellow-500" />
                <h2 className="text-sm font-bold text-text-primary uppercase tracking-wider">Execution Logs</h2>
              </div>
              <div className="p-6">
                {logsLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="w-6 h-6 text-accent-blue animate-spin" />
                  </div>
                ) : logs.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-sm text-text-muted italic">No step logs recorded yet...</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {logs.map((log: LogEntry) => (
                      <div key={log.id} className="group border border-[rgba(255,255,255,0.05)] bg-background/30 rounded-xl overflow-hidden transition-all hover:border-[rgba(255,255,255,0.12)]">
                        {/* Log Step Header */}
                        <div className="px-4 py-3 flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="w-7 h-7 rounded-full bg-accent-blue/10 text-accent-blue flex items-center justify-center text-xs font-bold">
                              {log.step_number}
                            </div>
                            <div>
                              <p className="text-sm font-bold text-text-primary">{log.action}</p>
                              <p className="text-[10px] text-text-muted uppercase tracking-tighter">
                                {log.status} {log.execution_time_ms ? `• ${(log.execution_time_ms / 1000).toFixed(1)}s` : ''}
                              </p>
                            </div>
                          </div>
                          
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => toggleSection(`output-${log.id}`)}
                              className="p-1.5 hover:bg-white/5 rounded-md text-text-muted transition-colors"
                              title="Toggle Details"
                            >
                              {expandedSections[`output-${log.id}`] ? (
                                <ChevronDown className="w-4 h-4" />
                              ) : (
                                <ChevronRight className="w-4 h-4" />
                              )}
                            </button>
                          </div>
                        </div>

                        {/* Collapsible Content */}
                        {expandedSections[`output-${log.id}`] && (
                          <div className="px-4 pb-4 animate-in slide-in-from-top-2 duration-200">
                            <div className="grid grid-cols-1 gap-3">
                              {log.input_data && (
                                <div>
                                  <p className="text-[10px] font-bold text-text-muted mb-1.5 uppercase">Input Parameters</p>
                                  <div className="bg-black/40 rounded-lg p-3 border border-white/[0.03]">
                                    <pre className="text-[11px] text-accent-blue font-mono overflow-x-auto whitespace-pre-wrap">
                                      {JSON.stringify(log.input_data, null, 2)}
                                    </pre>
                                  </div>
                                </div>
                              )}
                              {log.output_data && (
                                <div>
                                  <p className="text-[10px] font-bold text-text-muted mb-1.5 uppercase">Result Data</p>
                                  <div className="bg-black/40 rounded-lg p-3 border border-white/[0.03]">
                                    <pre className="text-[11px] text-text-muted font-mono overflow-x-auto whitespace-pre-wrap">
                                      {JSON.stringify(log.output_data, null, 2)}
                                    </pre>
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Sidebar Info (1/3) */}
          <div className="space-y-6">
            {/* Metadata Card */}
            <div className="bg-card rounded-2xl border border-[rgba(255,255,255,0.08)] p-6">
              <h3 className="text-xs font-bold text-text-muted uppercase tracking-widest mb-4">Task Info</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="text-[10px] text-text-muted uppercase font-bold block mb-1">Session</label>
                  <p className="text-sm text-text-primary font-mono bg-background/50 px-2 py-1 rounded border border-white/5 truncate">
                    {task.id}
                  </p>
                </div>
                
                <div>
                  <label className="text-[10px] text-text-muted uppercase font-bold block mb-1">Tools Invoked</label>
                  <div className="flex flex-wrap gap-1.5 mt-1">
                    {task.tools_used && task.tools_used.length > 0 ? (
                      task.tools_used.map((tool: string) => (
                        <span
                          key={tool}
                          className="px-2 py-0.5 bg-accent-blue/10 text-accent-blue text-[10px] font-bold rounded border border-accent-blue/20"
                        >
                          {tool}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-text-muted italic">None yet</span>
                    )}
                  </div>
                </div>

                <div>
                  <label className="text-[10px] text-text-muted uppercase font-bold block mb-1">Last Sync</label>
                  <p className="text-xs text-text-primary">
                    {new Date().toLocaleTimeString()}
                  </p>
                </div>
              </div>
            </div>

            {/* Quick Actions Card */}
            <div className="bg-gradient-to-br from-accent-blue/10 to-purple-500/10 rounded-2xl border border-white/5 p-6">
              <h3 className="text-sm font-bold text-text-primary mb-3 flex items-center gap-2">
                <Rocket className="w-4 h-4" />
                Quick Action
              </h3>
              <p className="text-xs text-text-muted mb-4 leading-relaxed">
                If the agent gets stuck, you can try re-running the command from the dashboard with more context.
              </p>
              <button 
                onClick={handleBack}
                className="w-full py-2 bg-white/5 hover:bg-white/10 rounded-lg text-xs font-bold text-text-primary transition-all border border-white/10"
              >
                Create Similar Task
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
