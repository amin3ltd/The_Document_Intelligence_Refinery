import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      console.error('Network Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// Document API
export const documentApi = {
  upload: async (file: File, strategy: string = 'auto') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('strategy', strategy);
    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getStatus: async (documentId: string) => {
    const response = await api.get(`/documents/${documentId}/status`);
    return response.data;
  },

  getResults: async (documentId: string) => {
    const response = await api.get(`/documents/${documentId}/results`);
    return response.data;
  },

  list: async () => {
    const response = await api.get('/documents');
    return response.data;
  },
};

// Query API
export const queryApi = {
  ask: async (question: string, docId: string = '') => {
    const response = await api.post('/query', {
      question,
      doc_id: docId,
    });
    return response.data;
  },
};

// Settings API
export const settingsApi = {
  get: async () => {
    const response = await api.get('/settings');
    return response.data;
  },

  update: async (settings: Record<string, unknown>) => {
    const response = await api.put('/settings', settings);
    return response.data;
  },
};

// Health Check API
export const healthApi = {
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

// Safety Limits API
export const safetyLimitsApi = {
  get: async () => {
    const response = await api.get('/config/safety-limits');
    return response.data;
  },

  update: async (limits: Record<string, number>) => {
    const response = await api.put('/config/safety-limits', limits);
    return response.data;
  },
};

export default api;
