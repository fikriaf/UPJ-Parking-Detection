// Configuration for ParkIt Admin Dashboard
const CONFIG = {
  // API Configuration
  API_BASE_URL: window.ENV?.BACKEND_API_URL || 'http://localhost:8000',
  API_TIMEOUT: 30000, // 30 seconds
  
  // Auto-refresh intervals
  AUTO_REFRESH_INTERVAL: 5000, // 5 seconds for live results
  STATS_REFRESH_INTERVAL: 30000, // 30 seconds for dashboard stats
  
  // File upload constraints
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_FILE_TYPES: ['image/jpeg', 'image/jpg', 'image/png'],
  
  // Pagination
  DEFAULT_PAGE_SIZE: 20,
  
  // LocalStorage keys
  STORAGE_KEY_API_KEY: 'parkit_admin_api_key',
  
  // Retry configuration
  MAX_RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
  
  // Notification duration
  NOTIFICATION_DURATION: 5000 // 5 seconds
};
