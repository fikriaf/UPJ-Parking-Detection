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
      
      <!-- Session Detail Modal -->
      <div id="session-detail-modal" class="modal" style="display: none;">
        <div class="modal-content" style="max-width: 95%; max-height: 90vh; overflow-y: auto;">
          <div class="modal-header">
            <h3>Session Detail</h3>
          </div>
          <div class="modal-body" id="session-detail-content"></div>
          <div class="modal-footer">
            <button id="copy-session-json-btn" class="btn btn-secondary">Copy JSON</button>
            <button id="close-session-detail-btn" class="btn btn-primary">Close</button>
          </div>
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
    
    // Close session detail modal
    document.getElementById('close-session-detail-btn').addEventListener('click', () => {
      document.getElementById('session-detail-modal').style.display = 'none';
    });
    
    // Copy JSON button
    document.getElementById('copy-session-json-btn').addEventListener('click', () => {
      this.copySessionJson();
    });
  },
  
  currentSessionData: null,
  
  copySessionJson() {
    if (this.currentSessionData) {
      navigator.clipboard.writeText(JSON.stringify(this.currentSessionData, null, 2))
        .then(() => uiManager.showNotification('JSON copied to clipboard', 'success'))
        .catch(() => uiManager.showNotification('Failed to copy', 'error'));
    }
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
          <button class="btn btn-sm btn-primary" onclick="SessionsPage.viewSession('${row.session_id}')">Open</button>
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
  },
  
  async viewSession(sessionId) {
    try {
      uiManager.showLoading();
      
      // Fetch full session data from results endpoint
      const response = await fetch(`${CONFIG.API_BASE_URL}/api/results/${sessionId}`, {
        headers: {
          'ngrok-skip-browser-warning': 'true'
        }
      });
      
      if (!response.ok) {
        throw new Error(`Failed to load session: ${response.status}`);
      }
      
      const data = await response.json();
      this.currentSessionData = data;
      
      // Build detail HTML
      const content = document.getElementById('session-detail-content');
      const imageUrl = `${CONFIG.API_BASE_URL}/api/results/${sessionId}/image`;
      
      content.innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-lg);">
          <!-- Left: Image -->
          <div>
            <h4 style="margin-bottom: var(--spacing-md);">Detection Image</h4>
            <img src="${imageUrl}" style="width: 100%; border-radius: 8px; border: 1px solid var(--border-color);" 
                 onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22400%22 height=%22300%22><rect fill=%22%23ddd%22 width=%22400%22 height=%22300%22/><text fill=%22%23999%22 x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22>No Image</text></svg>'">
          </div>
          
          <!-- Right: Info -->
          <div>
            <h4 style="margin-bottom: var(--spacing-md);">Session Info</h4>
            <table class="table">
              <tr><td><strong>Session ID</strong></td><td style="word-break: break-all;">${data.session_id}</td></tr>
              <tr><td><strong>Camera ID</strong></td><td>${data.camera_id || 'N/A'}</td></tr>
              <tr><td><strong>Status</strong></td><td><span class="badge ${data.status === 'completed' ? 'badge-success' : 'badge-warning'}">${data.status}</span></td></tr>
              <tr><td><strong>Total Frames</strong></td><td>${data.total_frames || 0}</td></tr>
              <tr><td><strong>Max Detections</strong></td><td>${data.max_detection_count || 0}</td></tr>
              <tr><td><strong>Total Motorcycles</strong></td><td>${data.total_motorcycles || data.max_detection_count || 0}</td></tr>
              <tr><td><strong>Total Empty Spaces</strong></td><td>${data.total_empty_spaces || 0}</td></tr>
              <tr><td><strong>Occupancy Rate</strong></td><td>${data.parking_occupancy_rate || 0}%</td></tr>
              <tr><td><strong>Created</strong></td><td>${uiManager.formatDateTime(data.created_at)}</td></tr>
              <tr><td><strong>Updated</strong></td><td>${uiManager.formatDateTime(data.updated_at)}</td></tr>
            </table>
            
            ${data.empty_spaces_per_row ? `
              <h4 style="margin: var(--spacing-lg) 0 var(--spacing-md);">Empty Spaces per Row</h4>
              <table class="table">
                <thead><tr><th>Row</th><th>Empty Spaces</th></tr></thead>
                <tbody>
                  ${Object.entries(data.empty_spaces_per_row).map(([row, count]) => `
                    <tr><td>Row ${row}</td><td>${count}</td></tr>
                  `).join('')}
                </tbody>
              </table>
            ` : ''}
          </div>
        </div>
        
        <!-- Raw JSON -->
        <div style="margin-top: var(--spacing-lg);">
          <h4 style="margin-bottom: var(--spacing-md);">Raw JSON Data</h4>
          <pre style="background: var(--bg-tertiary); padding: var(--spacing-md); border-radius: 6px; overflow-x: auto; max-height: 400px; font-size: 11px;">${JSON.stringify(data, null, 2)}</pre>
        </div>
      `;
      
      document.getElementById('session-detail-modal').style.display = 'flex';
      
    } catch (error) {
      console.error('[Sessions] View error:', error);
      uiManager.showNotification(error.message || 'Failed to load session details', 'error');
    } finally {
      uiManager.hideLoading();
    }
  }
};
