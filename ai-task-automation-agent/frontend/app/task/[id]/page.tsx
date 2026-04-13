'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useToast } from '@/lib/toast';
import { getTask, deleteTask, getTaskLogs } from '@/lib/api';
import {
  CheckCircle,
  XCircle,
  ArrowLeft,
  Trash2,
  ChevronDown,
  ChevronRight,
  Loader2,
} from 'lucide-react';

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
  const [task, setTask] = useState<TaskData | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedLogs, setExpandedLogs] = useState<{ [key: number]: boolean }>({});
  const [expandedSections, setExpandedSections] = useState<{ [key: string]: boolean }>({});

  const taskId = Number(params.id);

  useEffect(() => {
    if (taskId) {
      loadTaskData();
    }
  }, [taskId]);

  const loadTaskData = async () => {
    try {
      setLoading(true);
      const [taskData, logsData] = await Promise.all([
        getTask(taskId),
        getTaskLogs(taskId).catch(() => []),
      ]);
      setTask(taskData);
      setLogs(logsData || []);
    } catch (error: any) {
      if (error.response?.status === 404) {
        addToast('Task not found', 'error');
        router.push('/dashboard');
      } else {
        addToast('Failed to load task data', 'error');
      }
    } finally {
      setLoading(false);
    }
  };

  const toggleLog = (step: number) => {
    setExpandedLogs((prev) => ({ ...prev, [step]: !prev[step] }));
  };

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  const handleDelete = async () => {
    try {
      await deleteTask(taskId);
      addToast('Task deleted successfully', 'success');
      router.push('/dashboard');
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to delete task';
      addToast(message, 'error');
    }
  };

  const handleBack = () => {
    router.push('/dashboard');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-10 h-10 text-accent-blue animate-spin" />
          <p className="text-text-muted text-sm">Loading task...</p>
        </div>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <p className="text-text-muted">Task not found</p>
          <button
            onClick={handleBack}
            className="mt-4 px-4 py-2 bg-accent-blue text-white rounded-lg hover:opacity-90"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background px-4 md:px-6 py-6">
      <div className="max-w-[860px] mx-auto">
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-text-primary">Task #{task.id}</h1>
            <p className="text-sm text-text-muted mt-1">{new Date(task.created_at).toLocaleString()}</p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleBack}
              className="flex items-center gap-2 px-3 h-9 border border-text-primary text-text-primary text-sm rounded-md hover:bg-text-primary hover:text-background transition-all"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </button>
            <button
              onClick={handleDelete}
              className="flex items-center gap-2 px-3 h-9 bg-accent-red text-white text-sm rounded-md hover:opacity-90 transition-all"
            >
              <Trash2 className="w-4 h-4" />
              Delete
            </button>
          </div>
        </div>

        {/* Card 1: Status */}
        <div className="bg-card rounded-xl border border-[rgba(255,255,255,0.08)] p-5 mb-4">
          <div className="flex items-center gap-2">
            {task.status === 'completed' ? (
              <>
                <CheckCircle className="w-5 h-5 text-accent-green" />
                <span className="text-[15px] font-medium text-accent-green">Completed</span>
              </>
            ) : task.status === 'failed' ? (
              <>
                <XCircle className="w-5 h-5 text-accent-red" />
                <span className="text-[15px] font-medium text-accent-red">Failed</span>
              </>
            ) : (
              <>
                <Loader2 className="w-5 h-5 text-yellow-500 animate-spin" />
                <span className="text-[15px] font-medium text-yellow-500">Processing</span>
              </>
            )}
          </div>
        </div>

        {/* Card 2: Task Description */}
        <div className="bg-card rounded-xl border border-[rgba(255,255,255,0.08)] p-5 mb-4">
          <h2 className="text-[15px] font-medium text-text-primary mb-3">Task Description</h2>
          <div className="border-t border-[rgba(255,255,255,0.08)] pt-3">
            <p className="text-sm text-text-muted leading-[1.7]">{task.user_input}</p>
          </div>
        </div>

        {/* Card 3: Result */}
        {task.result && (
          <div className="bg-card rounded-xl border border-[rgba(255,255,255,0.08)] p-5 mb-4">
            <h2 className="text-[15px] font-medium text-text-primary mb-3">Result</h2>
            <div className="border-t border-[rgba(255,255,255,0.08)] pt-3">
              <div className="bg-background rounded-lg p-4 overflow-x-auto">
                <pre className="text-[13px] text-[#94A3B8] font-mono leading-[1.6] whitespace-pre-wrap">
                  {task.result}
                </pre>
              </div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {task.error_message && (
          <div className="bg-card rounded-xl border border-accent-red p-5 mb-4">
            <h2 className="text-[15px] font-medium text-accent-red mb-3">Error</h2>
            <div className="border-t border-accent-red pt-3">
              <p className="text-sm text-text-muted">{task.error_message}</p>
            </div>
          </div>
        )}

        {/* Card 4: Task Details */}
        <div className="bg-card rounded-xl border border-[rgba(255,255,255,0.08)] p-5 mb-4">
          <h2 className="text-[15px] font-medium text-text-primary mb-3">Task Details</h2>
          <div className="border-t border-[rgba(255,255,255,0.08)] pt-3">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-xs text-text-muted mb-1">Created</p>
                <p className="text-sm text-text-primary">{new Date(task.created_at).toLocaleString()}</p>
              </div>
              {task.completed_at && (
                <div>
                  <p className="text-xs text-text-muted mb-1">Completed</p>
                  <p className="text-sm text-text-primary">{new Date(task.completed_at).toLocaleString()}</p>
                </div>
              )}
              <div>
                <p className="text-xs text-text-muted mb-1">Session ID</p>
                <p className="text-sm text-text-primary">{task.id || 'N/A'}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Card 5: Tools Used */}
        {task.tools_used && task.tools_used.length > 0 && (
          <div className="bg-card rounded-xl border border-[rgba(255,255,255,0.08)] p-5 mb-4">
            <h2 className="text-[15px] font-medium text-text-primary mb-3">Tools Used</h2>
            <div className="border-t border-[rgba(255,255,255,0.08)] pt-3">
              <div className="flex flex-wrap gap-2">
                {task.tools_used.map((tool) => (
                  <span
                    key={tool}
                    className="inline-block px-3 py-1 bg-[#1E3A5F] text-[#60A5FA] text-xs rounded-full"
                  >
                    {tool}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Card 6: Execution Logs */}
        <div className="bg-card rounded-xl border border-[rgba(255,255,255,0.08)] p-5 mb-4">
          <h2 className="text-[15px] font-medium text-text-primary mb-3">Execution Logs</h2>
          <div className="border-t border-[rgba(255,255,255,0.08)] pt-3">
            {logs.length === 0 ? (
              <p className="text-sm text-text-muted text-center py-8">No execution logs available</p>
            ) : (
              <div className="space-y-3">
                {logs.map((log) => (
                  <div key={log.id} className="bg-background rounded-lg p-4">
                    {/* Step Header */}
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold text-text-primary">Step #{log.step_number}</span>
                        <span className="px-2 py-0.5 bg-[#14532D] text-[#4ADE80] text-[11px] rounded-full">
                          {log.status}
                        </span>
                      </div>
                    </div>

                    <p className="text-sm text-text-muted mb-3">
                      Action: <span className="text-text-primary">{log.action}</span>
                    </p>

                    {/* Collapsible Input Data */}
                    {log.input_data && (
                      <div className="mb-2">
                        <button
                          onClick={() => toggleSection(`input-${log.id}`)}
                          className="flex items-center gap-2 text-sm text-text-muted hover:text-text-primary transition-colors w-full"
                        >
                          {expandedSections[`input-${log.id}`] ? (
                            <ChevronDown className="w-4 h-4" />
                          ) : (
                            <ChevronRight className="w-4 h-4" />
                          )}
                          Input Data
                        </button>
                        {expandedSections[`input-${log.id}`] && (
                          <div className="mt-2 bg-card rounded-lg p-3 overflow-x-auto">
                            <pre className="text-xs text-[#94A3B8] font-mono">
                              {JSON.stringify(log.input_data, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Collapsible Output Data */}
                    {log.output_data && (
                      <div className="mb-2">
                        <button
                          onClick={() => toggleSection(`output-${log.id}`)}
                          className="flex items-center gap-2 text-sm text-text-muted hover:text-text-primary transition-colors w-full"
                        >
                          {expandedSections[`output-${log.id}`] ? (
                            <ChevronDown className="w-4 h-4" />
                          ) : (
                            <ChevronRight className="w-4 h-4" />
                          )}
                          Output Data
                        </button>
                        {expandedSections[`output-${log.id}`] && (
                          <div className="mt-2 bg-card rounded-lg p-3 overflow-x-auto">
                            <pre className="text-xs text-[#94A3B8] font-mono">
                              {JSON.stringify(log.output_data, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    )}

                    {log.execution_time_ms && (
                      <p className="text-xs text-text-muted mt-3">
                        Execution time: {(log.execution_time_ms / 1000).toFixed(1)}s
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
