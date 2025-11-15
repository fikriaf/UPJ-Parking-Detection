// Dashboard Page Component
const DashboardPage = {
  refreshInterval: null,

  async render() {
    uiManager.setPageTitle('Dashboard');
    
    const container = document.getElementById('page-container');
    container.innerHTML = `
      <div class="page-header">
        <h1 class="page-title">Dashboard</h1>
        <p class="page-description">System overview and statistics</p>
      </div>
      
      <div id="stats-container" class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon"><i class="fas fa-users"></i></div>
          <div class="stat-content">
            <div class="stat-label">Total Users</div>
            <div class="stat-value">-</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon"><i class="fas fa-folder"></i></div>
          <div class="stat-content">
            <div class="stat-label">Total Sessions</div>
            <div class="stat-value">-</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon"><i class="fas fa-sync-alt"></i></div>
          <div class="stat-content">
            <div class="stat-label">Active Sessions</div>
            <div class="stat-value">-</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon"><i class="fas fa-check-circle"></i></div>
          <div class="stat-content">
            <div class="stat-label">Completed Sessions</div>
            <div class="stat-value">-</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon"><i class="fas fa-motorcycle"></i></div>
          <div class="stat-content">
            <div class="stat-label">Total Detections</div>
            <div class="stat-value">-</div>
          </div>
        </div>
      </div>
      
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Recent Sessions</h2>
          <button id="refresh-btn" class="btn btn-sm btn-secondary">Refresh</button>
        </div>
        <div class="card-body">
          <div id="recent-sessions"></div>
        </div>
      </div>
      
      <div class="mt-2" style="text-align: center; color: var(--text-secondary); font-size: var(--font-size-sm);">
        Last updated: <span id="last-update">-</span>
      </div>
    `;
    
    // Load data
    await this.loadData();
    
    // Setup refresh button
    document.getElementById('refresh-btn').addEventListener('click', () => {
      this.loadData();
    });
    
    // Setup auto-refresh
    this.startAutoRefresh();
  },

  async loadData() {
    try {
      uiManager.showLoading();
      
      // Load stats
      const stats = await apiClient.getStats();
      this.renderStats(stats);
      
      // Load recent sessions
      const sessions = await apiClient.getSessions({ limit: 10, skip: 0 });
      this.renderRecentSessions(sessions.sessions || []);
      
      // Update timestamp
      document.getElementById('last-update').textContent = uiManager.formatDateTime(new Date());
      
    } catch (error) {
      console.error('[Dashboard] Load error:', error);
      uiManager.showNotification(error.message || 'Failed to load dashboard data', 'error');
    } finally {
      uiManager.hideLoading();
    }
  },

  renderStats(stats) {
    const statCards = document.querySelectorAll('.stat-card .stat-value');
    if (statCards.length >= 5) {
      statCards[0].textContent = uiManager.formatNumber(stats.total_users || 0);
      statCards[1].textContent = uiManager.formatNumber(stats.total_sessions || 0);
      statCards[2].textContent = uiManager.formatNumber(stats.active_sessions || 0);
      statCards[3].textContent = uiManager.formatNumber(stats.completed_sessions || 0);
      statCards[4].textContent = uiManager.formatNumber(stats.total_detections || 0);
    }
  },

  renderRecentSessions(sessions) {
    const container = document.getElementById('recent-sessions');
    
    if (!sessions || sessions.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon"><i class="fas fa-inbox"></i></div>
          <div class="empty-state-message">No recent sessions</div>
        </div>
      `;
      return;
    }
    
    const columns = [
      { key: 'session_id', label: 'Session ID', render: (row) => row.session_id.substring(0, 8) + '...' },
      { key: 'camera_id', label: 'Camera ID', render: (row) => row.camera_id || 'N/A' },
      { key: 'status', label: 'Status', render: (row) => {
        const badgeClass = row.status === 'completed' ? 'badge-success' : 'badge-warning';
        return `<span class="badge ${badgeClass}">${row.status}</span>`;
      }},
      { key: 'max_detection_count', label: 'Detections', render: (row) => row.max_detection_count || 0 },
      { key: 'total_frames', label: 'Frames', render: (row) => row.total_frames || 0 },
      { key: 'created_at', label: 'Created', render: (row) => uiManager.formatDateTime(row.created_at) }
    ];
    
    uiManager.renderTable(container, sessions, columns);
  },

  startAutoRefresh() {
    // Clear existing interval
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
    
    // Start new interval
    this.refreshInterval = setInterval(() => {
      this.loadData();
    }, CONFIG.STATS_REFRESH_INTERVAL);
  },

  cleanup() {
    // Clear interval when leaving page
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
      this.refreshInterval = null;
    }
  }
};
