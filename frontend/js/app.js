// Main Application Entry Point
class App {
  constructor() {
    this.currentPage = null;
  }

  init() {
    console.log('[ParkIt Admin] Initializing application...');
    
    // Check authentication and show appropriate view
    this.checkAuth();
    
    // Setup router
    this.setupRouter();
    
    // Setup global event listeners
    this.setupEventListeners();
    
    // Initialize router
    router.init();
    
    console.log('[ParkIt Admin] Application initialized');
  }

  checkAuth() {
    const loginPage = document.getElementById('login-page');
    const appContainer = document.getElementById('app');
    
    if (authManager.isAuthenticated()) {
      loginPage.style.display = 'none';
      appContainer.style.display = 'block';
    } else {
      loginPage.style.display = 'flex';
      appContainer.style.display = 'none';
    }
  }

  setupRouter() {
    // Register routes
    router.addRoute('/login', () => this.showLoginPage());
    router.addRoute('/', () => this.showPage(DashboardPage));
    router.addRoute('/upload', () => this.showPage(UploadPage));
    router.addRoute('/calibration', () => this.showPage(CalibrationPage));
    router.addRoute('/results', () => this.showPage(ResultsPage));
    router.addRoute('/sessions', () => this.showPage(SessionsPage));
    router.addRoute('/users', () => this.showPage(UsersPage));
  }

  setupEventListeners() {
    // Login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
      loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await this.handleLogin();
      });
    }
    
    // Logout button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', () => {
        this.handleLogout();
      });
    }
    
    // Mobile menu toggle
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    
    if (menuToggle && sidebar) {
      menuToggle.addEventListener('click', () => {
        sidebar.classList.toggle('active');
        
        // Add overlay for mobile
        let overlay = document.querySelector('.sidebar-overlay');
        if (!overlay) {
          overlay = document.createElement('div');
          overlay.className = 'sidebar-overlay';
          document.body.appendChild(overlay);
          
          overlay.addEventListener('click', () => {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
          });
        }
        overlay.classList.toggle('active');
      });
    }
    
    // Close mobile menu on navigation
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', () => {
        if (window.innerWidth <= 768) {
          sidebar.classList.remove('active');
          const overlay = document.querySelector('.sidebar-overlay');
          if (overlay) {
            overlay.classList.remove('active');
          }
        }
      });
    });
  }

  async handleLogin() {
    const apiKeyInput = document.getElementById('api-key-input');
    const apiKey = apiKeyInput.value.trim();
    
    if (!apiKey) {
      uiManager.showNotification('Please enter an API key', 'error');
      return;
    }
    
    try {
      uiManager.showLoading();
      
      // Validate API key with backend
      const isValid = await authManager.validateApiKey(apiKey);
      
      if (isValid) {
        // Save API key
        authManager.login(apiKey);
        
        // Show app
        document.getElementById('login-page').style.display = 'none';
        document.getElementById('app').style.display = 'block';
        
        // Navigate to dashboard
        router.navigate('/');
        
        uiManager.showNotification('Login successful', 'success');
      } else {
        uiManager.showNotification('Invalid API key', 'error');
      }
      
    } catch (error) {
      console.error('[App] Login error:', error);
      uiManager.showNotification('Login failed. Please check your connection.', 'error');
    } finally {
      uiManager.hideLoading();
    }
  }

  handleLogout() {
    // Clear auth
    authManager.logout();
    
    // Cleanup current page
    if (this.currentPage && this.currentPage.cleanup) {
      this.currentPage.cleanup();
    }
    
    // Show login page
    document.getElementById('app').style.display = 'none';
    document.getElementById('login-page').style.display = 'flex';
    
    // Clear form
    document.getElementById('api-key-input').value = '';
    
    uiManager.showNotification('Logged out successfully', 'success');
  }

  showLoginPage() {
    document.getElementById('app').style.display = 'none';
    document.getElementById('login-page').style.display = 'flex';
  }

  async showPage(pageComponent) {
    // Cleanup previous page
    if (this.currentPage && this.currentPage.cleanup) {
      this.currentPage.cleanup();
    }
    
    // Set current page
    this.currentPage = pageComponent;
    
    // Render new page
    try {
      await pageComponent.render();
    } catch (error) {
      console.error('[App] Page render error:', error);
      uiManager.showNotification('Failed to load page', 'error');
    }
  }
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    const app = new App();
    app.init();
  });
} else {
  const app = new App();
  app.init();
}
