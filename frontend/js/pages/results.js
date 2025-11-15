// Results Page Component
const ResultsPage = {
  state: {
    autoRefresh: true,
    refreshInterval: null,
    history: []
  },

  async render() {
    uiManager.setPageTitle('Results');
    
    const container = document.getElementById('page-container');
    container.innerHTML = `
      <div class="page-header">
        <h1 class="page-title">Detection Results</h1>
        <p class="page-description">Monitor live detection and view history</p>
      </div>
      
      <div class="card">
        <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
          <h2 class="card-title">Live Detection</h2>
          <div style="display: flex; align-items: center; gap: var(--spacing-md);">
            <label class="toggle-switch">
              <input type="checkbox" id="auto-refresh-toggle" checked>
              <span class="toggle-slider"></span>
            </label>
            <span>Auto-refresh</span>
          </div>
        </div>
        <div class="card-body">
          <div id="live-detection"></div>
        </div>
      </div>
      
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">History</h2>
          <button id="refresh-history-btn" class="btn btn-sm btn-secondary">Refresh</button>
        </div>
        <div class="card-body">
          <div id="history-table"></div>
        </div>
      </div>
      
      <!-- Detail Modal -->
      <div id="result-detail-modal" class="modal" style="display: none;">
        <div class="modal-content" style="max-width: 900px;">
          <div class="modal-header">
            <h3>Detection Result Details</h3>
          </div>
          <div class="modal-body" id="result-detail-content"></div>
          <div class="modal-footer">
            <button id="close-result-detail-btn" class="btn btn-secondary">Close</button>
          </div>
        </div>
      </div>
    `;
    
    await this.loadLiveDetection();
    await this.loadHistory();
    this.setupEventListeners();
    this.startAutoRefresh();
  },

  setupEventListeners() {
    // Auto-refresh toggle
    document.getElementById('auto-refresh-toggle').addEventListener('change', (e) => {
      this.state.autoRefresh = e.target.checked;
      if (this.state.autoRefresh) {
        this.startAutoRefresh();
      } else {
        this.stopAutoRefresh();
      }
    });
    
    // Refresh history button
    document.getElementById('refresh-history-btn').addEventListener('click', () => {
      this.loadHistory();
    });
    
    // Close detail modal
    document.getElementById('close-result-detail-btn').addEventListener('click', () => {
      document.getElementById('result-detail-modal').style.display = 'none';
    });
  },

  async loadLiveDetection() {
    try {
      const result = await apiClient.getLiveResults();
      this.renderLiveDetection(result);
    } catch (error) {
      console.error('[Results] Load live error:', error);
      const container = document.getElementById('live-detection');
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon"><i class="fas fa-inbox"></i></div>
          <div class="empty-state-message">No live detection available</div>
          <div class="empty-state-description">${error.message}</div>
        </div>
      `;
    }
  },

  renderLiveDetection(result) {
    const container = document.getElementById('live-detection');
    
    if (!result || !result.best_frame) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon"><i class="fas fa-inbox"></i></div>
          <div class="empty-state-message">No live detection available</div>
        </div>
      `;
      return;
    }
    
    const frame = result.best_frame;
    const imageUrl = `${CONFIG.API_BASE_URL}/api/results/${result.session_id}/image`;
    
    container.innerHTML = `
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-lg);">
        <div>
          <img src="${imageUrl}" style="width: 100%; border-radius: 6px; border: 1px solid var(--border-color);" alt="Detection Result">
        </div>
        <div>
          <h3 style="margin-bottom: var(--spacing-md);">Statistics</h3>
          <div style="display: grid; gap: var(--spacing-md);">
            <div class="stat-card">
              <div class="stat-icon"><i class="fas fa-motorcycle"></i></div>
              <div class="stat-content">
                <div class="stat-label">Total Motorcycles</div>
                <div class="stat-value">${frame.total_motorcycles || frame.detection_count || 0}</div>
              </div>
            </div>
            ${frame.total_empty_spaces !== undefined ? `
              <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-parking"></i></div>
                <div class="stat-content">
                  <div class="stat-label">Empty Spaces</div>
                  <div class="stat-value">${frame.total_empty_spaces}</div>
                </div>
              </div>
            ` : ''}
            ${frame.parking_occupancy_rate !== undefined ? `
              <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-chart-pie"></i></div>
                <div class="stat-content">
                  <div class="stat-label">Occupancy Rate</div>
                  <div class="stat-value">${frame.parking_occupancy_rate.toFixed(1)}%</div>
                </div>
              </div>
            ` : ''}
          </div>
          
          ${frame.empty_spaces_per_row ? `
            <div style="margin-top: var(--spacing-lg);">
              <h4 style="margin-bottom: var(--spacing-md);">Empty Spaces per Row</h4>
              <div style="display: grid; gap: var(--spacing-sm);">
                ${Object.entries(frame.empty_spaces_per_row).map(([row, count]) => `
                  <div style="display: flex; justify-content: space-between; padding: var(--spacing-sm); background: var(--bg-secondary); border-radius: 4px;">
                    <span>Row ${row}</span>
                    <span style="font-weight: 600;">${count} spaces</span>
                  </div>
                `).join('')}
              </div>
            </div>
          ` : ''}
          
          <div style="margin-top: var(--spacing-lg);">
            <button class="btn btn-primary btn-block" onclick="ResultsPage.viewDetail('${result.session_id}')">View Full Details</button>
          </div>
        </div>
      </div>
    `;
  },

  async loadHistory() {
    try {
      const data = await apiClient.getLatestResults(20, 0);
      this.state.history = data.results || [];
      this.renderHistory();
    } catch (error) {
      console.error('[Results] Load history error:', error);
      uiManager.showNotification(error.message || 'Failed to load history', 'error');
    }
  },

  renderHistory() {
    const container = document.getElementById('history-table');
    
    if (this.state.history.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon"><i class="fas fa-inbox"></i></div>
          <div class="empty-state-message">No history available</div>
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
      { key: 'detection_count', label: 'Detections', render: (row) => row.max_detection_count || 0 },
      { key: 'created_at', label: 'Created', render: (row) => uiManager.formatDateTime(row.created_at) },
      { key: 'actions', label: 'Actions', render: (row) => `
        <button class="btn btn-sm btn-primary" onclick="ResultsPage.viewDetail('${row.session_id}')">View</button>
      `}
    ];
    
    uiManager.renderTable(container, this.state.history, columns);
  },

  async viewDetail(sessionId) {
    try {
      uiManager.showLoading();
      const result = await apiClient.getResult(sessionId);
      
      const frame = result.best_frame;
      const imageUrl = `${CONFIG.API_BASE_URL}/api/results/${sessionId}/image`;
      
      const content = document.getElementById('result-detail-content');
      content.innerHTML = `
        <div style="margin-bottom: var(--spacing-lg);">
          <img src="${imageUrl}" style="width: 100%; border-radius: 6px; border: 1px solid var(--border-color);" alt="Detection Result">
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--spacing-md); margin-bottom: var(--spacing-lg);">
          <div>
            <strong>Session ID:</strong><br>
            ${result.session_id}
          </div>
          <div>
            <strong>Camera ID:</strong><br>
            ${result.camera_id || 'N/A'}
          </div>
          <div>
            <strong>Status:</strong><br>
            <span class="badge ${result.status === 'completed' ? 'badge-success' : 'badge-warning'}">${result.status}</span>
          </div>
          <div>
            <strong>Total Frames:</strong><br>
            ${result.total_frames}
          </div>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: var(--spacing-md); margin-bottom: var(--spacing-lg);">
          <div class="stat-card">
            <div class="stat-icon"><i class="fas fa-motorcycle"></i></div>
            <div class="stat-content">
              <div class="stat-label">Motorcycles</div>
              <div class="stat-value">${frame.total_motorcycles || frame.detection_count || 0}</div>
            </div>
          </div>
          ${frame.total_empty_spaces !== undefined ? `
            <div class="stat-card">
              <div class="stat-icon"><i class="fas fa-parking"></i></div>
              <div class="stat-content">
                <div class="stat-label">Empty Spaces</div>
                <div class="stat-value">${frame.total_empty_spaces}</div>
              </div>
            </div>
          ` : ''}
          ${frame.parking_occupancy_rate !== undefined ? `
            <div class="stat-card">
              <div class="stat-icon"><i class="fas fa-chart-pie"></i></div>
              <div class="stat-content">
                <div class="stat-label">Occupancy</div>
                <div class="stat-value">${frame.parking_occupancy_rate.toFixed(1)}%</div>
              </div>
            </div>
          ` : ''}
        </div>
        
        ${frame.empty_spaces && frame.empty_spaces.length > 0 ? `
          <div style="margin-bottom: var(--spacing-lg);">
            <h4 style="margin-bottom: var(--spacing-md);">Empty Spaces Details</h4>
            <div class="table-container">
              <table class="table">
                <thead>
                  <tr>
                    <th>Space ID</th>
                    <th>Row</th>
                    <th>Width</th>
                    <th>Coordinates</th>
                    <th>Can Fit</th>
                  </tr>
                </thead>
                <tbody>
                  ${frame.empty_spaces.map(space => `
                    <tr>
                      <td>${space.space_id}</td>
                      <td>Row ${space.row_index}</td>
                      <td>${space.width.toFixed(1)}px</td>
                      <td>(${space.x1}, ${space.y1}) - (${space.x2}, ${space.y2})</td>
                      <td>${space.can_fit_motorcycle ? '✓ Yes' : '✕ No'}</td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          </div>
        ` : ''}
        
        ${frame.detections && frame.detections.length > 0 ? `
          <div>
            <h4 style="margin-bottom: var(--spacing-md);">Detections (${frame.detections.length})</h4>
            <div style="max-height: 300px; overflow-y: auto;">
              <div class="table-container">
                <table class="table">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Confidence</th>
                      <th>Coordinates</th>
                      <th>Assigned Row</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${frame.detections.map((det, i) => `
                      <tr>
                        <td>${i + 1}</td>
                        <td>${(det.confidence * 100).toFixed(1)}%</td>
                        <td>(${det.bbox.x1}, ${det.bbox.y1}) - (${det.bbox.x2}, ${det.bbox.y2})</td>
                        <td>${det.assigned_row !== undefined ? `Row ${det.assigned_row}` : 'N/A'}</td>
                      </tr>
                    `).join('')}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ` : ''}
      `;
      
      document.getElementById('result-detail-modal').style.display = 'flex';
      
    } catch (error) {
      console.error('[Results] Load detail error:', error);
      uiManager.showNotification(error.message || 'Failed to load result details', 'error');
    } finally {
      uiManager.hideLoading();
    }
  },

  startAutoRefresh() {
    if (this.state.refreshInterval) {
      clearInterval(this.state.refreshInterval);
    }
    
    this.state.refreshInterval = setInterval(() => {
      if (this.state.autoRefresh) {
        this.loadLiveDetection();
      }
    }, CONFIG.AUTO_REFRESH_INTERVAL);
  },

  stopAutoRefresh() {
    if (this.state.refreshInterval) {
      clearInterval(this.state.refreshInterval);
      this.state.refreshInterval = null;
    }
  },

  cleanup() {
    this.stopAutoRefresh();
  }
};
