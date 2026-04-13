import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ==========================================
// AUTH API
// ==========================================
export const loginApi = async (email: string, password: string) => {
  const response = await api.post('/api/auth/login', { email, password });
  return response.data;
};

export const registerApi = async (email: string, password: string, fullName?: string) => {
  const response = await api.post('/api/auth/register', { email, password, full_name: fullName });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get('/api/auth/me');
  return response.data;
};

// ==========================================
// TASKS API
// ==========================================
export const executeTask = async (userInput: string, sessionId?: string) => {
  const response = await api.post('/api/tasks/execute', {
    user_input: userInput,
    session_id: sessionId,
  });
  return response.data;
};

export const getTasks = async (skip = 0, limit = 20) => {
  const response = await api.get(`/api/tasks/?skip=${skip}&limit=${limit}`);
  return response.data;
};

export const getTask = async (taskId: number) => {
  const response = await api.get(`/api/tasks/${taskId}`);
  return response.data;
};

export const deleteTask = async (taskId: number) => {
  const response = await api.delete(`/api/tasks/${taskId}`);
  return response.data;
};

// ==========================================
// ANALYTICS API
// ==========================================
export const getAnalytics = async () => {
  const response = await api.get('/api/analytics/dashboard');
  return response.data;
};

export const getLogs = async (skip = 0, limit = 50) => {
  const response = await api.get(`/api/analytics/logs?skip=${skip}&limit=${limit}`);
  return response.data;
};

export const getTaskLogs = async (taskId: number) => {
  const response = await api.get(`/api/analytics/logs/${taskId}`);
  return response.data;
};

// ==========================================
// CONVERSATIONS API
// ==========================================
export const getConversationHistory = async (sessionId: string, skip = 0, limit = 50) => {
  const response = await api.get(`/api/conversations/${sessionId}?skip=${skip}&limit=${limit}`);
  return response.data;
};

export const createConversation = async (sessionId: string, role: string, message: string, extraData?: any) => {
  const response = await api.post('/api/conversations/', {
    session_id: sessionId,
    role,
    message,
    extra_data: extraData,
  });
  return response.data;
};
