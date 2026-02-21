import axios from 'axios';
import type { Applicant, Payment, User, DashboardStats, CriticalCase } from '@/types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:6789';

const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authApi = {
  login: async (username: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },
  register: async (userData: { username: string; email: string; password: string; full_name?: string }) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
  getMe: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Applicants API
export const applicantsApi = {
  getAll: async (params?: { page?: number; page_size?: number; status?: string; search?: string }) => {
    const response = await api.get('/applicants', { params });
    return response.data;
  },
  getById: async (id: number) => {
    const response = await api.get(`/applicants/${id}`);
    return response.data;
  },
  create: async (data: Partial<Applicant>) => {
    const response = await api.post('/applicants', data);
    return response.data;
  },
  update: async (id: number, data: Partial<Applicant>) => {
    const response = await api.patch(`/applicants/${id}`, data);
    return response.data;
  },
  assess: async (id: number) => {
    const response = await api.post(`/applicants/${id}/assess`);
    return response.data;
  },
  updateStatus: async (id: number, status: string) => {
    const response = await api.post(`/applicants/${id}/status?status=${status}`);
    return response.data;
  },
};

// Payments API
export const paymentsApi = {
  getAll: async (params?: { page?: number; page_size?: number; status?: string }) => {
    const response = await api.get('/payments', { params });
    return response.data;
  },
  getById: async (id: number) => {
    const response = await api.get(`/payments/${id}`);
    return response.data;
  },
  create: async (data: Partial<Payment>) => {
    const response = await api.post('/payments', data);
    return response.data;
  },
  update: async (id: number, data: Partial<Payment>) => {
    const response = await api.patch(`/payments/${id}`, data);
    return response.data;
  },
  approve: async (id: number, approved: boolean, notes?: string) => {
    const response = await api.post(`/payments/${id}/approve?approved=${approved}&notes=${notes || ''}`);
    return response.data;
  },
  checkAnomaly: async (id: number) => {
    const response = await api.get(`/payments/${id}/anomaly`);
    return response.data;
  },
  getSummary: async () => {
    const response = await api.get('/payments/stats/summary');
    return response.data;
  },
};

// Chatbot API
export const chatbotApi = {
  chat: async (message: string, conversationId?: string) => {
    const response = await api.post('/chatbot/chat', { message, conversation_id: conversationId });
    return response.data;
  },
  getFaq: async () => {
    const response = await api.get('/chatbot/faq');
    return response.data;
  },
};

// Dashboard API
export const dashboardApi = {
  getStats: async (): Promise<DashboardStats> => {
    const response = await api.get('/dashboard/stats');
    return response.data;
  },
  getCriticalCases: async (): Promise<CriticalCase[]> => {
    const response = await api.get('/dashboard/critical-cases');
    return response.data;
  },
};

// Audit API
export const auditApi = {
  getLogs: async (params?: { page?: number; page_size?: number; entity_type?: string }) => {
    const response = await api.get('/audit', { params });
    return response.data;
  },
  getSummary: async () => {
    const response = await api.get('/audit/stats/summary');
    return response.data;
  },
};

export default api;