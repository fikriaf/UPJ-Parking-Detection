// Dashboard Page Component - Professional UI with Analytics
const DashboardPage = {
  refreshInterval: null,

  async render() {
    uiManager.setPageTitle('Dashboard');

    const container = document.getElementById('page-container');
    container.innerHTML = `
      <div class="dashboard-header">
        <div class="dashboard-header-content">
          <h1 class="dashboard-title">Dashboard Overview</h1>
          <p class="dashboard-subtitle">Real-time parking detection monitoring & analytics</p>
        </div>
        <div class="dashboard-header-actions">
          <span class="live-indicator"><span class="live-dot"></span> Live</span>
          <button id="refresh-btn" class="btn btn-icon" title="Refresh">
            <i class="fas fa-sync-alt"></i>
          </button>
        </div>
      </div>

      <!-- Stats Overview -->
      <div class="stats-overview">
        <div class="stat-card stat-card-primary">
          <div class="stat-card-icon"><i class="fas fa-motorcycle"></i></div>
          <div class="stat-card-content">
            <span class="stat-card-value" id="stat-detections">0</span>
            <span class="stat-card-label">Total Detections</span>
          </div>
          <div class="stat-card-trend trend-up">
            <i class="fas fa-arrow-up"></i> <span id="trend-detections">0%</span>
          </div>
        </div>
        <div class="stat-card stat-card-success">
          <div class="stat-card-icon"><i class="fas fa-check-circle"></i></div>
          <div class="stat-card-content">
            <span class="stat-card-value" id="stat-completed">0</span>
            <span class="stat-card-label">Completed Sessions</span>
          </div>
        </div>
        <div class="stat-card stat-card-warning">
          <div class="stat-card-icon"><i class="fas fa-sync-alt"></i></div>
          <div class="stat-card-content">
            <span class="stat-card-value" id="stat-active">0</span>
            <span class="stat-card-label">Active Sessions</span>
          </div>
        </div>
        <div class="stat-card stat-card-info">
          <div class="stat-card-icon"><i class="fas fa-users"></i></div>
          <div class="stat-card-content">
            <span class="stat-card-value" id="stat-users">0</span>
            <span class="stat-card-label">Total Users</span>
          </div>
        </div>
      </div>

      <!-- Main Grid -->
      <div class="dashboard-grid-full">
        <!-- Row 1: Charts -->
        <div class="dashboard-row">
          <!-- Detection Trend Chart -->
          <div class="card card-chart">
            <div class="card-header card-header-flex">
              <h3 class="card-title"><i class="fas fa-chart-line"></i> Detection Trend (7 Days)</h3>
              <div class="chart-legend-inline">
                <span class="legend-dot bg-primary"></span> Detections
                <span class="legend-dot bg-success"></span> Sessions
              </div>
            </div>
            <div class="card-body">
              <div class="chart-container" id="trend-chart">
                <canvas id="trendCanvas"></canvas>
              </div>
            </div>
          </div>

          <!-- Occupancy Rate Chart -->
          <div class="card card-chart-sm">
            <div class="card-header">
              <h3 class="card-title"><i class="fas fa-chart-pie"></i> Parking Occupancy</h3>
            </div>
            <div class="card-body">
              <div class="occupancy-display">
                <div class="occupancy-gauge">
                  <svg viewBox="0 0 36 36" class="circular-chart">
                    <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    <path id="occupancy-circle" class="circle-occupancy" stroke-dasharray="0, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                  </svg>
                  <div class="occupancy-center">
                    <span class="occupancy-value" id="occupancy-rate">0%</span>
                    <span class="occupancy-label">Occupied</span>
                  </div>
                </div>
                <div class="occupancy-stats">
                  <div class="occupancy-stat">
                    <span class="occupancy-stat-value" id="total-parked">0</span>
                    <span class="occupancy-stat-label">Parked</span>
                  </div>
                  <div class="occupancy-stat">
                    <span class="occupancy-stat-value" id="total-empty">0</span>
                    <span class="occupancy-stat-label">Empty</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Row 2: Detection Analysis & Motor Brands -->
        <div class="dashboard-row">
          <!-- Confidence Analysis -->
          <div class="card">
            <div class="card-header card-header-flex">
              <h3 class="card-title"><i class="fas fa-bullseye"></i> Detection Confidence Analysis</h3>
              <span class="badge badge-info">Last Session</span>
            </div>
            <div class="card-body">
              <div id="confidence-analysis">
                <div class="confidence-bars">
                  <div class="confidence-bar-item">
                    <div class="confidence-bar-header">
                      <span>High (90-100%)</span>
                      <span id="conf-high">0</span>
                    </div>
                    <div class="confidence-bar">
                      <div class="confidence-bar-fill bg-success" id="conf-high-bar" style="width: 0%"></div>
                    </div>
                  </div>
                  <div class="confidence-bar-item">
                    <div class="confidence-bar-header">
                      <span>Medium (70-89%)</span>
                      <span id="conf-medium">0</span>
                    </div>
                    <div class="confidence-bar">
                      <div class="confidence-bar-fill bg-warning" id="conf-medium-bar" style="width: 0%"></div>
                    </div>
                  </div>
                  <div class="confidence-bar-item">
                    <div class="confidence-bar-header">
                      <span>Low (50-69%)</span>
                      <span id="conf-low">0</span>
                    </div>
                    <div class="confidence-bar">
                      <div class="confidence-bar-fill bg-error" id="conf-low-bar" style="width: 0%"></div>
                    </div>
                  </div>
                </div>
                <div class="confidence-summary">
                  <div class="confidence-metric">
                    <span class="metric-value" id="avg-confidence">0%</span>
                    <span class="metric-label">Avg Confidence</span>
                  </div>
                  <div class="confidence-metric">
                    <span class="metric-value" id="total-detected">0</span>
                    <span class="metric-label">Total Detected</span>
                  </div>
                  <div class="confidence-metric">
                    <span class="metric-value" id="detection-fps">0</span>
                    <span class="metric-label">Processing FPS</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Motor Brands Distribution -->
          <div class="card">
            <div class="card-header card-header-flex">
              <h3 class="card-title"><i class="fas fa-chart-bar"></i> Registered Motor Brands</h3>
              <a href="#/motorcycles" class="btn btn-sm btn-outline">View All</a>
            </div>
            <div class="card-body">
              <div id="brand-distribution">
                <div class="brand-chart" id="brand-bars"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Row 3: Recent Sessions & Registered Motors -->
        <div class="dashboard-row">
          <!-- Recent Sessions -->
          <div class="card">
            <div class="card-header card-header-flex">
              <h3 class="card-title"><i class="fas fa-history"></i> Recent Sessions</h3>
              <a href="#/sessions" class="btn btn-sm btn-outline">View All</a>
            </div>
            <div class="card-body card-body-table">
              <div id="recent-sessions"></div>
            </div>
          </div>

          <!-- Recent Users -->
          <div class="card">
            <div class="card-header card-header-flex">
              <h3 class="card-title"><i class="fas fa-users"></i> Recent Users</h3>
              <a href="#/users" class="btn btn-sm btn-outline">View All</a>
            </div>
            <div class="card-body card-body-table">
              <div id="recent-users"></div>
            </div>
          </div>
        </div>

        <!-- Row 4: Quick Actions & System Status -->
        <div class="dashboard-row">
          <!-- Quick Actions -->
          <div class="card">
            <div class="card-header">
              <h3 class="card-title"><i class="fas fa-bolt"></i> Quick Actions</h3>
            </div>
            <div class="card-body">
              <div class="quick-actions-grid">
                <a href="#/upload" class="quick-action-item">
                  <div class="quick-action-icon bg-primary"><i class="fas fa-video"></i></div>
                  <span class="quick-action-label">Integrate Camera</span>
                </a>
                <a href="#/calibration" class="quick-action-item">
                  <div class="quick-action-icon bg-success"><i class="fas fa-sliders-h"></i></div>
                  <span class="quick-action-label">Calibration</span>
                </a>
                <a href="#/results" class="quick-action-item">
                  <div class="quick-action-icon bg-info"><i class="fas fa-chart-bar"></i></div>
                  <span class="quick-action-label">View Results</span>
                </a>
                <a href="#/users" class="quick-action-item">
                  <div class="quick-action-icon bg-warning"><i class="fas fa-users"></i></div>
                  <span class="quick-action-label">Manage Users</span>
                </a>
              </div>
            </div>
          </div>

          <!-- System Status & Activity -->
          <div class="card">
            <div class="card-header">
              <h3 class="card-title"><i class="fas fa-server"></i> System Status</h3>
            </div>
            <div class="card-body">
              <div class="system-grid">
                <div class="status-list">
                  <div class="status-item">
                    <span class="status-indicator status-online"></span>
                    <span class="status-label">API Server</span>
                    <span class="status-value">Online</span>
                  </div>
                  <div class="status-item">
                    <span class="status-indicator status-online"></span>
                    <span class="status-label">MongoDB</span>
                    <span class="status-value">Connected</span>
                  </div>
                  <div class="status-item">
                    <span class="status-indicator status-online"></span>
                    <span class="status-label">YOLO Model</span>
                    <span class="status-value">Ready</span>
                  </div>
                  <div class="status-item" id="camera-status">
                    <span class="status-indicator status-offline"></span>
                    <span class="status-label">Camera Feed</span>
                    <span class="status-value">Disconnected</span>
                  </div>
                </div>
                <div class="system-metrics">
                  <div class="system-metric">
                    <i class="fas fa-clock"></i>
                    <span>Uptime: <strong>99.9%</strong></span>
                  </div>
                  <div class="system-metric">
                    <i class="fas fa-tachometer-alt"></i>
                    <span>Latency: <strong id="api-latency">--</strong>ms</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="dashboard-footer">
        <span class="footer-text">Last updated: <span id="last-update">-</span></span>
        <span class="footer-text">Auto-refresh: <span class="text-success">Every 30s</span></span>
      </div>
    `;

    await this.loadData();
    document.getElementById('refresh-btn').addEventListener('click', () => this.loadData());
    this.startAutoRefresh();
  },


  async loadData() {
    const startTime = performance.now();
    try {
      const refreshBtn = document.getElementById('refresh-btn');
      if (refreshBtn) refreshBtn.classList.add('spinning');

      // Load all data in parallel
      const [stats, sessions, motorcycleStats, users, liveResult] = await Promise.all([
        apiClient.getStats().catch(() => ({})),
        apiClient.getSessions({ limit: 10 }).catch(() => ({ sessions: [] })),
        apiClient.getMotorcycleStats().catch(() => ({})),
        apiClient.getUsers({ limit: 5 }).catch(() => ({ users: [] })),
        apiClient.getLiveResults().catch(() => ({}))
      ]);

      // Render all sections
      this.renderStats(stats, motorcycleStats);
      this.renderTrendChart(sessions.sessions || []);
      this.renderOccupancyGauge(liveResult);
      this.renderConfidenceAnalysis(liveResult);
      this.renderBrandDistribution(motorcycleStats);
      this.renderRecentSessions(sessions.sessions || []);
      this.renderRecentUsers(users.users || []);
      this.updateCameraStatus(stats.active_sessions > 0);

      // Update latency
      const latency = Math.round(performance.now() - startTime);
      document.getElementById('api-latency').textContent = latency;
      document.getElementById('last-update').textContent = this.formatTime(new Date());

    } catch (error) {
      console.error('[Dashboard] Load error:', error);
      uiManager.showNotification('Failed to load dashboard data', 'error');
    } finally {
      const refreshBtn = document.getElementById('refresh-btn');
      if (refreshBtn) refreshBtn.classList.remove('spinning');
    }
  },

  renderStats(stats, motorcycleStats) {
    this.animateValue('stat-detections', stats.total_detections || 0);
    this.animateValue('stat-completed', stats.completed_sessions || 0);
    this.animateValue('stat-active', stats.active_sessions || 0);
    this.animateValue('stat-users', stats.total_users || 0);
  },

  animateValue(elementId, endValue) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const startValue = parseInt(el.textContent.replace(/,/g, '')) || 0;
    const duration = 500;
    const startTime = performance.now();

    const animate = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easeOut = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.floor(startValue + (endValue - startValue) * easeOut).toLocaleString();
      if (progress < 1) requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  },

  renderTrendChart(sessions) {
    const canvas = document.getElementById('trendCanvas');
    if (!canvas) return;

    // Group sessions by day (last 7 days)
    const days = [];
    const detectionsPerDay = [];
    const sessionsPerDay = [];

    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dayStr = date.toLocaleDateString('en-US', { weekday: 'short' });
      days.push(dayStr);

      const dayStart = new Date(date.setHours(0, 0, 0, 0));
      const dayEnd = new Date(date.setHours(23, 59, 59, 999));

      const daySessions = sessions.filter(s => {
        const sessionDate = new Date(s.created_at);
        return sessionDate >= dayStart && sessionDate <= dayEnd;
      });

      sessionsPerDay.push(daySessions.length);
      detectionsPerDay.push(daySessions.reduce((sum, s) => sum + (s.max_detection_count || 0), 0));
    }

    // Draw simple bar chart
    const ctx = canvas.getContext('2d');
    const width = canvas.parentElement.clientWidth;
    const height = 200;
    canvas.width = width;
    canvas.height = height;

    const maxDetections = Math.max(...detectionsPerDay, 1);
    const barWidth = (width - 80) / 7;
    const padding = 40;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw grid lines
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
      const y = padding + (height - padding * 2) * (i / 4);
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(width - padding, y);
      ctx.stroke();
    }

    // Draw bars
    days.forEach((day, i) => {
      const x = padding + i * barWidth + barWidth * 0.2;
      const barH = (detectionsPerDay[i] / maxDetections) * (height - padding * 2);
      const y = height - padding - barH;

      // Detection bar
      ctx.fillStyle = '#2563eb';
      ctx.fillRect(x, y, barWidth * 0.3, barH);

      // Session bar
      const sessionBarH = (sessionsPerDay[i] / Math.max(...sessionsPerDay, 1)) * (height - padding * 2) * 0.5;
      ctx.fillStyle = '#10b981';
      ctx.fillRect(x + barWidth * 0.35, height - padding - sessionBarH, barWidth * 0.3, sessionBarH);

      // Day label
      ctx.fillStyle = '#64748b';
      ctx.font = '12px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(day, x + barWidth * 0.3, height - 10);

      // Value label
      ctx.fillStyle = '#0f172a';
      ctx.fillText(detectionsPerDay[i], x + barWidth * 0.3, y - 5);
    });
  },

  renderOccupancyGauge(liveResult) {
    const rate = liveResult.parking_occupancy_rate || 0;
    const parked = liveResult.total_motorcycles || 0;
    const empty = liveResult.total_empty_spaces || 0;

    // Update gauge
    const circle = document.getElementById('occupancy-circle');
    if (circle) {
      circle.style.strokeDasharray = `${rate}, 100`;
      // Color based on occupancy
      if (rate > 80) circle.style.stroke = '#ef4444';
      else if (rate > 60) circle.style.stroke = '#f59e0b';
      else circle.style.stroke = '#10b981';
    }

    document.getElementById('occupancy-rate').textContent = `${Math.round(rate)}%`;
    document.getElementById('total-parked').textContent = parked;
    document.getElementById('total-empty').textContent = empty;
  },

  renderConfidenceAnalysis(liveResult) {
    const detections = liveResult.best_frame?.detections || [];

    let high = 0, medium = 0, low = 0, totalConf = 0;

    detections.forEach(d => {
      const conf = d.confidence * 100;
      totalConf += conf;
      if (conf >= 90) high++;
      else if (conf >= 70) medium++;
      else low++;
    });

    const total = detections.length || 1;
    const avgConf = detections.length > 0 ? (totalConf / total).toFixed(1) : 0;

    // Update bars
    document.getElementById('conf-high').textContent = high;
    document.getElementById('conf-medium').textContent = medium;
    document.getElementById('conf-low').textContent = low;

    document.getElementById('conf-high-bar').style.width = `${(high / total) * 100}%`;
    document.getElementById('conf-medium-bar').style.width = `${(medium / total) * 100}%`;
    document.getElementById('conf-low-bar').style.width = `${(low / total) * 100}%`;

    // Update summary
    document.getElementById('avg-confidence').textContent = `${avgConf}%`;
    document.getElementById('total-detected').textContent = detections.length;
    document.getElementById('detection-fps').textContent = '~15'; // Estimated
  },

  renderBrandDistribution(motorcycleStats) {
    const container = document.getElementById('brand-bars');
    if (!container) return;

    const brands = motorcycleStats.top_brands || [];

    if (brands.length === 0) {
      container.innerHTML = '<div class="empty-state-sm"><i class="fas fa-motorcycle"></i><p>No registered motors yet</p></div>';
      return;
    }

    const maxCount = Math.max(...brands.map(b => b.count), 1);

    let html = '';
    brands.slice(0, 5).forEach(brand => {
      const percent = (brand.count / maxCount) * 100;
      html += `
        <div class="brand-bar-item">
          <div class="brand-bar-header">
            <span class="brand-name">${brand.brand || 'Unknown'}</span>
            <span class="brand-count">${brand.count}</span>
          </div>
          <div class="brand-bar">
            <div class="brand-bar-fill" style="width: ${percent}%"></div>
          </div>
        </div>
      `;
    });

    container.innerHTML = html;
  },

  renderRecentSessions(sessions) {
    const container = document.getElementById('recent-sessions');
    if (!sessions || sessions.length === 0) {
      container.innerHTML = `
        <div class="empty-state empty-state-sm">
          <i class="fas fa-inbox"></i>
          <p>No sessions yet</p>
          <a href="#/upload" class="btn btn-sm btn-primary">Start Detection</a>
        </div>
      `;
      return;
    }

    let html = `<table class="table table-compact">
      <thead><tr><th>Session</th><th>Camera</th><th>Status</th><th>Detections</th><th>Time</th></tr></thead>
      <tbody>`;

    sessions.slice(0, 5).forEach(s => {
      const statusClass = s.status === 'completed' ? 'badge-success' : 'badge-warning';
      html += `
        <tr>
          <td><code>${s.session_id.substring(0, 8)}</code></td>
          <td>${s.camera_id || 'N/A'}</td>
          <td><span class="badge ${statusClass}">${s.status}</span></td>
          <td><strong>${s.max_detection_count || 0}</strong></td>
          <td>${this.timeAgo(s.created_at)}</td>
        </tr>
      `;
    });

    html += '</tbody></table>';
    container.innerHTML = html;
  },

  renderRecentUsers(users) {
    const container = document.getElementById('recent-users');
    if (!users || users.length === 0) {
      container.innerHTML = `
        <div class="empty-state empty-state-sm">
          <i class="fas fa-users"></i>
          <p>No users registered</p>
        </div>
      `;
      return;
    }

    let html = `<table class="table table-compact">
      <thead><tr><th>Username</th><th>Email</th><th>Role</th><th>Status</th></tr></thead>
      <tbody>`;

    users.slice(0, 5).forEach(u => {
      const statusClass = u.is_active ? 'badge-success' : 'badge-error';
      const statusText = u.is_active ? 'Active' : 'Inactive';
      const roleClass = u.is_admin ? 'badge-warning' : 'badge-info';
      const roleText = u.is_admin ? 'Admin' : 'User';
      html += `
        <tr>
          <td><strong>${u.username}</strong></td>
          <td>${u.email || '-'}</td>
          <td><span class="badge ${roleClass}">${roleText}</span></td>
          <td><span class="badge ${statusClass}">${statusText}</span></td>
        </tr>
      `;
    });

    html += '</tbody></table>';
    container.innerHTML = html;
  },

  updateCameraStatus(isActive) {
    const statusEl = document.getElementById('camera-status');
    if (statusEl) {
      const indicator = statusEl.querySelector('.status-indicator');
      const value = statusEl.querySelector('.status-value');
      indicator.className = isActive ? 'status-indicator status-online' : 'status-indicator status-offline';
      value.textContent = isActive ? 'Streaming' : 'Disconnected';
    }
  },

  timeAgo(timestamp) {
    if (!timestamp) return 'N/A';
    const seconds = Math.floor((new Date() - new Date(timestamp)) / 1000);
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  },

  formatTime(date) {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  },

  startAutoRefresh() {
    if (this.refreshInterval) clearInterval(this.refreshInterval);
    this.refreshInterval = setInterval(() => this.loadData(), CONFIG.STATS_REFRESH_INTERVAL);
  },

  cleanup() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
      this.refreshInterval = null;
    }
  }
};
