// Authentication Manager
class AuthManager {
  constructor() {
    this.apiKey = null;
    this.loadFromStorage();
  }

  // Load API key from localStorage
  loadFromStorage() {
    const stored = localStorage.getItem(CONFIG.STORAGE_KEY_API_KEY);
    if (stored) {
      this.apiKey = stored;
    }
  }

  // Check if user is authenticated
  isAuthenticated() {
    return this.apiKey !== null && this.apiKey.length > 0;
  }

  // Save API key and login
  login(apiKey) {
    if (!apiKey || apiKey.trim().length === 0) {
      throw new Error('API key cannot be empty');
    }
    
    this.apiKey = apiKey.trim();
    localStorage.setItem(CONFIG.STORAGE_KEY_API_KEY, this.apiKey);
  }

  // Remove API key and logout
  logout() {
    this.apiKey = null;
    localStorage.removeItem(CONFIG.STORAGE_KEY_API_KEY);
  }

  // Get stored API key
  getApiKey() {
    return this.apiKey;
  }

  // Validate API key with backend
  async validateApiKey(apiKey) {
    try {
      const response = await fetch(`${CONFIG.API_BASE_URL}/api/admin/stats`, {
        method: 'GET',
        headers: {
          'X-API-Key': apiKey
        },
        signal: AbortSignal.timeout(CONFIG.API_TIMEOUT)
      });

      return response.ok;
    } catch (error) {
      console.error('[AuthManager] Validation error:', error);
      return false;
    }
  }
}

// Create global instance
const authManager = new AuthManager();
