// Results Page Component
const ResultsPage = {
  state: {
    autoRefresh: true,
    refreshInterval: null,
    history: [],
    // Live image streaming
    liveImageInterval: null,
    liveImageDelay: 1000, // Default 1 second
    currentSessionId: null
  },

  async render() {
    uiManager.setPageTitle('Results');
    
    // Load saved settings
    this.state.liveImageDelay = parseInt(localStorage.getItem('parkit_result_delay') || '1000');
    
    const container = document.getElementById('page-container');
    container.innerHTML = `
      <div class="page-header">
        <h1 class="page-title">Detection Results</h1>
        <p class="page-description">Monitor live detection and view history</p>
      </div>
      
      <!-- Auto-Capture Status Banner -->
      <div id="auto-capture-banner" class="card" style="display: none; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
        <div class="card-body" style="padding: var(--spacing-md);">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: var(--spacing-md);">
            <div>
              <strong><i class="fas fa-video"></i> Auto-Capture Running</strong>
              <span id="banner-session-id" style="margin-left: var(--spacing-md);"></span>
            </div>
            <div>
              Captured: <strong id="banner-capture-count">0</strong> frames
            </div>
            <button id="stop-auto-capture-btn" class="btn btn-sm" style="background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3);">
              <i class="fas fa-stop"></i> Stop
            </button>
          </div>
        </div>
      </div>
      
      <!-- Live Image Stream -->
      <div class="card">
        <div class="card-header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: var(--spacing-md);">
          <h2 class="card-title"><i class="fas fa-broadcast-tower"></i> Live Result Stream</h2>
          <div style="display: flex; align-items: center; gap: var(--spacing-md); flex-wrap: wrap;">
            <div class="form-group" style="margin-bottom: 0; display: flex; align-items: center; gap: var(--spacing-sm);">
              <label for="live-session-id" style="white-space: nowrap;">Session ID:</label>
              <input type="text" id="live-session-id" class="form-control" placeholder="Enter session ID" style="width: 200px;" value="${localStorage.getItem('parkit_auto_session_id') || ''}">
            </div>
            <div class="form-group" style="margin-bottom: 0; display: flex; align-items: center; gap: var(--spacing-sm);">
              <label for="result-delay" style="white-space: nowrap;">Refresh (s):</label>
              <input type="number" id="result-delay" class="form-control" min="1" max="60" value="${this.state.liveImageDelay / 1000}" style="width: 70px;">
            </div>
            <button id="start-live-stream-btn" class="btn btn-success btn-sm">
              <i class="fas fa-play"></i> Start
            </button>
            <button id="stop-live-stream-btn" class="btn btn-danger btn-sm" style="display: none;">
              <i class="fas fa-stop"></i> Stop
            </button>
          </div>
        </div>
        <div class="card-body">
          <div id="live-image-container" style="text-align: center;">
            <div class="empty-state">
              <div class="empty-state-icon"><i class="fas fa-image"></i></div>
              <div class="empty-state-message">Enter Session ID and click Start to view live results</div>
            </div>
          </div>
        </div>
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

    // Live image stream controls
    document.getElementById('start-live-stream-btn').addEventListener('click', () => {
      this.startLiveImageStream();
    });

    document.getElementById('stop-live-stream-btn').addEventListener('click', () => {
      this.stopLiveImageStream();
    });

    // Save delay on change
    document.getElementById('result-delay').addEventListener('change', (e) => {
      const delay = parseInt(e.target.value) * 1000;
      if (delay >= 1000 && delay <= 60000) {
        this.state.liveImageDelay = delay;
        localStorage.setItem('parkit_result_delay', delay.toString());
        uiManager.showNotification(`Refresh delay saved: ${e.target.value}s`, 'success');
      }
    });

    // Stop auto-capture from banner
    document.getElementById('stop-auto-capture-btn').addEventListener('click', () => {
      if (typeof AutoCaptureManager !== 'undefined') {
        AutoCaptureManager.stop();
        this.updateAutoCaptureStatus();
      }
    });

    // Update auto-capture status
    this.updateAutoCaptureStatus();
    
    // Listen for auto-capture status changes
    if (typeof AutoCaptureManager !== 'undefined') {
      AutoCaptureManager.onStatusChange((status) => {
        this.updateAutoCaptureStatus(status);
      });
    }
  },

  updateAutoCaptureStatus(status) {
    if (typeof AutoCaptureManager === 'undefined') return;
    
    const s = status || AutoCaptureManager.getStatus();
    const banner = document.getElementById('auto-capture-banner');
    
    if (s.isRunning) {
      banner.style.display = 'block';
      document.getElementById('banner-session-id').textContent = `Session: ${s.sessionId}`;
      document.getElementById('banner-capture-count').textContent = s.captureCount;
      
      // Auto-fill session ID
      const sessionInput = document.getElementById('live-session-id');
      if (sessionInput && !sessionInput.value) {
        sessionInput.value = s.sessionId;
      }
    } else {
      banner.style.display = 'none';
    }
  },

  startLiveImageStream() {
    const sessionId = document.getElementById('live-session-id').value.trim();
    
    if (!sessionId) {
      uiManager.showNotification('Please enter Session ID', 'error');
      return;
    }

    this.state.currentSessionId = sessionId;
    
    // Update UI
    document.getElementById('start-live-stream-btn').style.display = 'none';
    document.getElementById('stop-live-stream-btn').style.display = 'inline-block';
    
    // Start fetching
    this.fetchLiveImage();
    
    uiManager.showNotification(`Live stream started (refresh: ${this.state.liveImageDelay / 1000}s)`, 'success');
  },

  stopLiveImageStream() {
    if (this.state.liveImageInterval) {
      clearTimeout(this.state.liveImageInterval);
      this.state.liveImageInterval = null;
    }
    
    this.state.currentSessionId = null;
    
    // Update UI
    document.getElementById('start-live-stream-btn').style.display = 'inline-block';
    document.getElementById('stop-live-stream-btn').style.display = 'none';
    
    uiManager.showNotification('Live stream stopped', 'info');
  },

  async fetchLiveImage() {
    if (!this.state.currentSessionId) return;

    const container = document.getElementById('live-image-container');
    
    try {
      const imageUrl = `${CONFIG.API_BASE_URL}/api/results/${this.state.currentSessionId}/image?t=${Date.now()}`;
      
      // Fetch with ngrok header
      const response = await fetch(imageUrl, {
        headers: {
          'ngrok-skip-browser-warning': 'true'
        }
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const objectUrl = URL.createObjectURL(blob);
        
        container.innerHTML = `
          <div style="position: relative; display: inline-block;">
            <img src="${objectUrl}" style="max-width: 100%; max-height: 70vh; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" alt="Live Result">
            <div style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.7); color: #0f0; padding: 5px 10px; border-radius: 4px; font-family: monospace; font-size: 12px;">
              <i class="fas fa-circle" style="color: #0f0; animation: blink 1s infinite;"></i> LIVE
            </div>
          </div>
          <div style="margin-top: var(--spacing-md); color: var(--text-secondary); font-size: var(--font-size-sm);">
            Session: ${this.state.currentSessionId} | Last update: ${new Date().toLocaleTimeString()}
          </div>
          <style>
            @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
          </style>
        `;
      } else {
        container.innerHTML = `
          <div class="empty-state">
            <div class="empty-state-icon"><i class="fas fa-exclamation-triangle"></i></div>
            <div class="empty-state-message">No image available for this session</div>
            <div class="empty-state-description">Session may not have completed detection yet</div>
          </div>
        `;
      }
    } catch (error) {
      console.error('[Results] Fetch live image error:', error);
    }

    // Schedule next fetch
    if (this.state.currentSessionId) {
      this.state.liveImageInterval = setTimeout(() => this.fetchLiveImage(), this.state.liveImageDelay);
    }
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
    this.stopLiveImageStream();
  }
};
