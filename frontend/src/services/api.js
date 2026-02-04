import axios from 'axios';

// Determine API URL based on environment
// Frontend runs in browser, so use localhost or production domain
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for better error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Enhanced error handling with user-friendly messages
    let errorMessage = 'An unexpected error occurred';
    
    if (error.code === 'ECONNABORTED') {
      errorMessage = 'Request timeout - The server is taking too long to respond';
    } else if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
      errorMessage = `Unable to connect to backend server at ${API_URL}.\n\n` +
        'Please ensure:\n' +
        '1. The backend server is running\n' +
        '2. The backend is accessible at the configured URL\n' +
        '3. Check REACT_APP_API_URL environment variable\n\n' +
        'To start backend:\n' +
        '• Docker: docker-compose up -d backend\n' +
        '• Local dev: ./start-dev.sh\n\n' +
        'Default API URL: http://localhost:8000';
    } else if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      if (status === 404) {
        errorMessage = 'Resource not found';
      } else if (status === 500) {
        errorMessage = 'Server error - Please try again later';
      } else if (status === 401) {
        errorMessage = 'Unauthorized - Please log in';
      } else {
        errorMessage = error.response.data?.detail || 
                      error.response.data?.message || 
                      `Server error: ${status}`;
      }
    } else if (error.request) {
      errorMessage = 'No response from server - Please check if the backend is running';
    }
    
    // Attach user-friendly message to error
    error.userMessage = errorMessage;
    
    console.error('API Error:', {
      message: error.message,
      userMessage: errorMessage,
      code: error.code,
      response: error.response?.data
    });
    
    return Promise.reject(error);
  }
);

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
  
  importFromSpotify: async (url, matchLocal = true) => {
    const response = await apiClient.post('/api/tracks/import/spotify', {
      url,
      match_local: matchLocal,
    });
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
