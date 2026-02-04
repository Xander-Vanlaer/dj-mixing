import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const tracksAPI = {
  upload: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/api/tracks/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  list: async () => {
    const response = await apiClient.get('/api/tracks/');
    return response.data;
  },
  
  get: async (id) => {
    const response = await apiClient.get(`/api/tracks/${id}`);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await apiClient.delete(`/api/tracks/${id}`);
    return response.data;
  },
  
  addCuePoint: async (trackId, cuePoint) => {
    const response = await apiClient.post(`/api/tracks/${trackId}/cue-points`, cuePoint);
    return response.data;
  },
  
  getCuePoints: async (trackId) => {
    const response = await apiClient.get(`/api/tracks/${trackId}/cue-points`);
    return response.data;
  },
};

export const analysisAPI = {
  get: async (trackId) => {
    const response = await apiClient.get(`/api/analysis/${trackId}`);
    return response.data;
  },
  
  reanalyze: async (trackId) => {
    const response = await apiClient.post(`/api/analysis/${trackId}/reanalyze`);
    return response.data;
  },
  
  getCompatible: async (trackId, params = {}) => {
    const response = await apiClient.get(`/api/analysis/${trackId}/compatible`, { params });
    return response.data;
  },
};

export const mixerAPI = {
  createMix: async (mixData) => {
    const response = await apiClient.post('/api/mixer/mixes', mixData);
    return response.data;
  },
  
  listMixes: async () => {
    const response = await apiClient.get('/api/mixer/mixes');
    return response.data;
  },
  
  getMix: async (mixId) => {
    const response = await apiClient.get(`/api/mixer/mixes/${mixId}`);
    return response.data;
  },
  
  generateAutoMix: async (params) => {
    const response = await apiClient.post('/api/mixer/auto-mix', params);
    return response.data;
  },
};

export default apiClient;
