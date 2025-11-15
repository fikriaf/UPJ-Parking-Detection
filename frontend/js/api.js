// API Client for ParkIt Backend
class ApiClient {
  constructor(baseUrl, authManager) {
    this.baseUrl = baseUrl;
    this.authManager = authManager;
  }

  // Generic request method with retry logic
  async request(endpoint, options = {}, retryCount = 0) {
    const url = `${this.baseUrl}${endpoint}`;
    const apiKey = this.authManager.getApiKey();
    
    // Default headers
    const headers = {
      ...options.headers
    };
    
    // Add API key if authenticated and not already present
    if (apiKey && !headers['X-API-Key']) {
      headers['X-API-Key'] = apiKey;
    }
    
    // Add Content-Type for JSON if body is present and not FormData
    if (options.body && !(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }
    
    const config = {
      ...options,
      headers,
      signal: AbortSignal.timeout(CONFIG.API_TIMEOUT)
    };
    
    try {
      const response = await fetch(url, config);
      
      // Handle authentication errors
      if (response.status === 401) {
        this.authManager.logout();
        window.location.hash = '#/login';
        throw new Error('Session expired. Please login again.');
      }
      
      // Handle other errors
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }
      
      // Return response for further processing
      return response;
      
    } catch (error) {
      // Retry on network errors
      if (error.name === 'TypeError' && retryCount < CONFIG.MAX_RETRY_ATTEMPTS) {
        await new Promise(resolve => setTimeout(resolve, CONFIG.RETRY_DELAY * (retryCount + 1)));
        return this.request(endpoint, options, retryCount + 1);
      }
      
      // Log error
      console.error(`[ApiClient] Request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Admin Stats
  async getStats() {
    const response = await this.request('/api/admin/stats');
    return response.json();
  }

  // Calibration endpoints
  async getCalibrations() {
    const response = await this.request('/api/admin/calibration');
    return response.json();
  }

  async getCalibration(cameraId) {
    const response = await this.request(`/api/admin/calibration/${cameraId}`);
    return response.json();
  }

  async createCalibration(data) {
    const response = await this.request('/api/admin/calibration', {
      method: 'POST',
      body: JSON.stringify(data)
    });
    return response.json();
  }

  async updateCalibration(cameraId, data) {
    const response = await this.request(`/api/admin/calibration/${cameraId}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
    return response.json();
  }

  async deleteCalibration(cameraId) {
    const response = await this.request(`/api/admin/calibration/${cameraId}`, {
      method: 'DELETE'
    });
    return response.json();
  }

  // Frame upload endpoints
  async uploadFrame(file, sessionId, cameraId = null) {
    const formData = new FormData();
    formData.append('file', file);
    
    let url = `/api/frames/upload?session_id=${sessionId}`;
    if (cameraId) {
      url += `&camera_id=${cameraId}`;
    }
    
    const response = await this.request(url, {
      method: 'POST',
      body: formData
    });
    return response.json();
  }

  async completeSession(sessionId) {
    const response = await this.request(`/api/frames/complete/${sessionId}`, {
      method: 'POST'
    });
    return response.json();
  }

  // Results endpoints (public)
  async getLiveResults() {
    const response = await this.request('/api/results/live');
    return response.json();
  }

  async getResult(sessionId) {
    const response = await this.request(`/api/results/${sessionId}`);
    return response.json();
  }

  async getLatestResults(limit = 10, skip = 0) {
    const response = await this.request(`/api/results/latest?limit=${limit}&skip=${skip}`);
    return response.json();
  }

  async getResultImage(sessionId) {
    const response = await this.request(`/api/results/${sessionId}/image`);
    return response.blob();
  }

  // Session management endpoints
  async getSessions(params = {}) {
    const queryParams = new URLSearchParams();
    if (params.limit) queryParams.append('limit', params.limit);
    if (params.skip) queryParams.append('skip', params.skip);
    if (params.status) queryParams.append('status', params.status);
    
    const response = await this.request(`/api/admin/sessions?${queryParams.toString()}`);
    return response.json();
  }

  async deleteSession(sessionId) {
    const response = await this.request(`/api/admin/sessions/${sessionId}`, {
      method: 'DELETE'
    });
    return response.json();
  }

  // User management endpoints
  async getUsers(params = {}) {
    const queryParams = new URLSearchParams();
    if (params.limit) queryParams.append('limit', params.limit);
    if (params.skip) queryParams.append('skip', params.skip);
    
    const response = await this.request(`/api/admin/users?${queryParams.toString()}`);
    return response.json();
  }

  async toggleUserActive(username) {
    const response = await this.request(`/api/admin/users/${username}/toggle-active`, {
      method: 'PUT'
    });
    return response.json();
  }
}

// Create global instance
const apiClient = new ApiClient(CONFIG.API_BASE_URL, authManager);
