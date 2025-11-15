// Sessions Page Component
const SessionsPage = {
  state: {
    sessions: [],
    currentPage: 1,
    totalPages: 1,
    pageSize: 20,
    statusFilter: 'all'
  },

  async render() {
    uiManager.setPageTitle('Sessions');
    
    const container = document.getElementById('page-container');
    container.innerHTML = `
      <div class="page-header">
        <h1 class="page-title">Session Management</h1>
        <p class="page-description">View and manage detection sessions</p>
      </div>
      
      <div class="card">
        <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
          <h2 class="card-title">Sessions</h2>
          <div style="display: flex; gap: var(--spacing-md); align-items: center;">
            <label for="status-filter">Filter:</label>
            <select id="status-filter" class="form-control" style="width: auto;">
              <option value="all">All</option>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
            </select>
          </div>
        </div>
        <div class="card-body">
          <div id="sessions-table"></div>
          <div id="pagination-container"></div>
        </div>
      </div>
    `;
    
    await this.loadSessions();
    this.setupEventListeners();
  },

  setupEventListeners() {
    // Status filter
    document.getElementById('status-filter').addEventListener('change', (e) => {
      this.state.statusFilter = e.target.value;
      this.state.currentPage = 1;
      this.loadSessions();
    });
  },

  async loadSessions() {
    try {
      uiManager.showLoading();
      
      const params = {
        limit: this.state.pageSize,
        skip: (this.state.currentPage - 1) * this.state.pageSize
      };
      
      if (this.state.statusFilter !== 'all') {
        params.status = this.state.statusFilter;
      }
      
      const data = await apiClient.getSessions(params);
      this.state.sessions = data.sessions || [];
      this.state.totalPages = Math.ceil((data.total || 0) / this.state.pageSize);
      
      this.renderSessions();
      this.renderPagination();
      
    } catch (error) {
      console.error('[Sessions] Load error:', error);
      uiManager.showNotification(error.message || 'Failed to load sessions', 'error');
    } finally {
      uiManager.hideLoading();
    }
  },

  renderSessions() {
    const container = document.getElementById('sessions-table');
    
    if (this.state.sessions.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon"><i class="fas fa-inbox"></i></div>
          <div class="empty-state-message">No sessions found</div>
        </div>
      `;
      return;
    }
    
    const columns = [
      { key: 'session_id', label: 'Session ID', render: (row) => row.session_id.substring(0, 12) + '...' },
      { key: 'camera_id', label: 'Camera ID', render: (row) => row.camera_id || 'N/A' },
      { key: 'status', label: 'Status', render: (row) => {
        const badgeClass = row.status === 'completed' ? 'badge-success' : 'badge-warning';
        return `<span class="badge ${badgeClass}">${row.status}</span>`;
      }},
      { key: 'max_detection_count', label: 'Detections', render: (row) => row.max_detection_count || 0 },
      { key: 'total_frames', label: 'Frames', render: (row) => row.total_frames || 0 },
      { key: 'created_at', label: 'Created', render: (row) => uiManager.formatDateTime(row.created_at) },
      { key: 'actions', label: 'Actions', render: (row) => `
        <div class="table-actions">
          <button class="btn btn-sm btn-danger" onclick="SessionsPage.deleteSession('${row.session_id}')">Delete</button>
        </div>
      `}
    ];
    
    uiManager.renderTable(container, this.state.sessions, columns);
  },

  renderPagination() {
    const container = document.getElementById('pagination-container');
    uiManager.renderPagination(container, this.state.currentPage, this.state.totalPages, (page) => {
      this.state.currentPage = page;
      this.loadSessions();
    });
  },

  async deleteSession(sessionId) {
    const confirmed = await uiManager.showConfirm(`Are you sure you want to delete session "${sessionId.substring(0, 12)}..."?`);
    
    if (!confirmed) return;
    
    try {
      uiManager.showLoading();
      await apiClient.deleteSession(sessionId);
      uiManager.showNotification('Session deleted successfully', 'success');
      await this.loadSessions();
    } catch (error) {
      console.error('[Sessions] Delete error:', error);
      uiManager.showNotification(error.message || 'Failed to delete session', 'error');
    } finally {
      uiManager.hideLoading();
    }
  }
};
