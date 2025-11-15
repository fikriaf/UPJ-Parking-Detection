// Client-side Router for SPA navigation
class Router {
  constructor() {
    this.routes = {};
    this.currentRoute = null;
  }

  // Register a route handler
  addRoute(path, handler) {
    this.routes[path] = handler;
  }

  // Navigate to a route
  navigate(path) {
    // Update URL hash
    window.location.hash = `#${path}`;
  }

  // Get current route
  getCurrentRoute() {
    return this.currentRoute;
  }

  // Handle route change
  async handleRoute() {
    // Get path from hash
    let path = window.location.hash.slice(1) || '/';
    
    // Remove trailing slash except for root
    if (path !== '/' && path.endsWith('/')) {
      path = path.slice(0, -1);
    }
    
    // Check authentication for protected routes
    if (path !== '/login' && !authManager.isAuthenticated()) {
      path = '/login';
      window.location.hash = '#/login';
    }
    
    // If authenticated and trying to access login, redirect to dashboard
    if (path === '/login' && authManager.isAuthenticated()) {
      path = '/';
      window.location.hash = '#/';
    }
    
    this.currentRoute = path;
    
    // Find and execute route handler
    const handler = this.routes[path];
    
    if (handler) {
      try {
        await handler();
        this.updateActiveNav(path);
      } catch (error) {
        console.error('[Router] Route handler error:', error);
        uiManager.showNotification('Failed to load page', 'error');
      }
    } else {
      // 404 - Route not found
      console.warn('[Router] Route not found:', path);
      this.navigate('/');
    }
  }

  // Update active navigation item
  updateActiveNav(path) {
    document.querySelectorAll('.nav-item').forEach(item => {
      const route = item.dataset.route;
      if (route === path) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });
  }

  // Initialize router
  init() {
    // Handle hash change
    window.addEventListener('hashchange', () => this.handleRoute());
    
    // Handle initial load
    this.handleRoute();
    
    // Handle navigation clicks
    document.addEventListener('click', (e) => {
      const link = e.target.closest('a[href^="#"]');
      if (link) {
        e.preventDefault();
        const path = link.getAttribute('href').slice(1);
        this.navigate(path);
      }
    });
  }
}

// Create global instance
const router = new Router();
