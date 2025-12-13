// Motorcycles Management Page
const MotorcyclesPage = {
  currentPage: 1,
  pageSize: 20,
  searchQuery: '',

  async render() {
    uiManager.setPageTitle('Motorcycles');
    
    const container = document.getElementById('page-container');
    container.innerHTML = `
      <div class="page-header">
        <div>
          <h1 class="page-title">Registered Motorcycles</h1>
          <p class="page-description">Manage all registered motorcycles in the system</p>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="stats-grid stats-grid-4">
        <div class="stat-card stat-card-primary">
          <div class="stat-card-icon"><i class="fas fa-motorcycle"></i></div>
          <div class="stat-card-content">
            <span class="stat-card-value" id="total-motors">0</span>
            <span class="stat-card-label">Total Registered</span>
          </div>
        </div>
        <div class="stat-card stat-card-success">
          <div class="stat-card-icon"><i class="fas fa-check-circle"></i></div>
          <div class="stat-card-content">
            <span class="stat-card-value" id="active-motors">0</span>
            <span class="stat-card-label">Active</span>
          </div>
        </div>
        <div class="stat-card stat-card-warning">
          <div class="stat-card-icon"><i class="fas fa-ban"></i></div>
          <div class="stat-card-content">
            <span class="stat-card-value" id="inactive-motors">0</span>
            <span class="stat-card-label">Inactive</span>
          </div>
        </div>
        <div class="stat-card stat-card-info">
          <div class="stat-card-icon"><i class="fas fa-trophy"></i></div>
          <div class="stat-card-content">
            <span class="stat-card-value" id="top-brand">-</span>
            <span class="stat-card-label">Top Brand</span>
          </div>
        </div>
      </div>

      <!-- Search & Filter -->
      <div class="card">
        <div class="card-body">
          <div class="filter-bar">
            <div class="search-box">
              <i class="fas fa-search"></i>
              <input type="text" id="search-input" placeholder="Search by code or owner name..." class="form-control">
            </div>
            <button id="search-btn" class="btn btn-primary">
              <i class="fas fa-search"></i> Search
            </button>
            <button id="refresh-btn" class="btn btn-secondary">
              <i class="fas fa-sync-alt"></i> Refresh
            </button>
          </div>
        </div>
      </div>

      <!-- Motorcycles Table -->
      <div class="card">
        <div class="card-header card-header-flex">
          <h3 class="card-title"><i class="fas fa-list"></i> Motorcycle List</h3>
          <span class="badge badge-info" id="result-count">0 results</span>
        </div>
        <div class="card-body card-body-table">
          <div id="motorcycles-table"></div>
        </div>
        <div class="card-footer">
          <div id="pagination"></div>
        </div>
      </div>

      <!-- Brand Distribution -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title"><i class="fas fa-chart-bar"></i> Brand Distribution</h3>
        </div>
        <div class="card-body">
          <div id="brand-chart" class="brand-chart-large"></div>
        </div>
      </div>
    `;

    // Event listeners
    document.getElementById('search-btn').addEventListener('click', () => this.search());
    document.getElementById('refresh-btn').addEventListener('click', () => this.loadData());
    document.getElementById('search-input').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.search();
    });

    await this.loadData();
  },

  async loadData() {
    try {
      uiManager.showLoading();

      const [stats, motorcycles] = await Promise.all([
        apiClient.getMotorcycleStats(),
        apiClient.getMotorcycles({ 
          limit: this.pageSize, 
          skip: (this.currentPage - 1) * this.pageSize,
          search: this.searchQuery 
        })
      ]);

      this.renderStats(stats);
      this.renderTable(motorcycles);
      this.renderBrandChart(stats.top_brands || []);

    } catch (error) {
      console.error('[Motorcycles] Load error:', error);
      uiManager.showNotification(error.message || 'Failed to load data', 'error');
    } finally {
      uiManager.hideLoading();
    }
  },

  renderStats(stats) {
    document.getElementById('total-motors').textContent = (stats.total_registered || 0).toLocaleString();
    document.getElementById('active-motors').textContent = (stats.active || 0).toLocaleString();
    document.getElementById('inactive-motors').textContent = (stats.inactive || 0).toLocaleString();
    
    const topBrand = stats.top_brands?.[0];
    document.getElementById('top-brand').textContent = topBrand ? topBrand.brand : '-';
  },

  renderTable(motorcycles) {
    const container = document.getElementById('motorcycles-table');
    document.getElementById('result-count').textContent = `${motorcycles.length} results`;

    if (!motorcycles || motorcycles.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon"><i class="fas fa-motorcycle"></i></div>
          <div class="empty-state-message">No motorcycles found</div>
        </div>
      `;
      return;
    }

    let html = `
      <table class="table table-hover">
        <thead>
          <tr>
            <th>Code</th>
            <th>Owner</th>
            <th>Brand / Model</th>
            <th>Color</th>
            <th>Size (LxW)</th>
            <th>Status</th>
            <th>Registered</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
    `;

    motorcycles.forEach(m => {
      const statusClass = m.is_active ? 'badge-success' : 'badge-error';
      const statusText = m.is_active ? 'Active' : 'Inactive';
      const toggleIcon = m.is_active ? 'ban' : 'check';
      const toggleTitle = m.is_active ? 'Deactivate' : 'Activate';

      const sizeText = m.length_cm && m.width_cm 
        ? `${m.length_cm} x ${m.width_cm} cm` 
        : (m.length_cm ? `${m.length_cm} cm` : (m.width_cm ? `${m.width_cm} cm` : '-'));

      html += `
        <tr>
          <td><code class="code-badge">${m.code}</code></td>
          <td><strong>${m.owner_name}</strong></td>
          <td>${m.brand || '-'} ${m.model || ''}</td>
          <td>
            <span class="color-badge" style="background: ${this.getColorCode(m.color)}">${m.color || '-'}</span>
          </td>
          <td>${sizeText}</td>
          <td><span class="badge ${statusClass}">${statusText}</span></td>
          <td>${this.formatDate(m.created_at)}</td>
          <td>
            <div class="table-actions">
              <button class="btn btn-sm btn-icon" onclick="MotorcyclesPage.toggleActive('${m.code}')" title="${toggleTitle}">
                <i class="fas fa-${toggleIcon}"></i>
              </button>
              <button class="btn btn-sm btn-icon btn-danger" onclick="MotorcyclesPage.deleteMotorcycle('${m.code}')" title="Delete">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </td>
        </tr>
      `;
    });

    html += '</tbody></table>';
    container.innerHTML = html;
  },

  renderBrandChart(brands) {
    const container = document.getElementById('brand-chart');
    if (!brands || brands.length === 0) {
      container.innerHTML = '<div class="empty-state-sm"><p>No brand data available</p></div>';
      return;
    }

    const maxCount = Math.max(...brands.map(b => b.count), 1);
    let html = '';

    brands.forEach((brand, index) => {
      const percent = (brand.count / maxCount) * 100;
      const colors = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'];
      const color = colors[index % colors.length];

      html += `
        <div class="brand-bar-item-large">
          <div class="brand-bar-header">
            <span class="brand-rank">#${index + 1}</span>
            <span class="brand-name">${brand.brand || 'Unknown'}</span>
            <span class="brand-count">${brand.count} motors</span>
          </div>
          <div class="brand-bar-large">
            <div class="brand-bar-fill-large" style="width: ${percent}%; background: ${color}"></div>
          </div>
        </div>
      `;
    });

    container.innerHTML = html;
  },

  async search() {
    this.searchQuery = document.getElementById('search-input').value.trim();
    this.currentPage = 1;
    await this.loadData();
  },

  async toggleActive(code) {
    try {
      await apiClient.toggleMotorcycleActive(code);
      uiManager.showNotification('Status updated successfully', 'success');
      await this.loadData();
    } catch (error) {
      uiManager.showNotification(error.message || 'Failed to update status', 'error');
    }
  },

  async deleteMotorcycle(code) {
    const confirmed = await uiManager.showConfirm(`Are you sure you want to delete motorcycle ${code}?`);
    if (!confirmed) return;

    try {
      await apiClient.deleteMotorcycle(code);
      uiManager.showNotification('Motorcycle deleted successfully', 'success');
      await this.loadData();
    } catch (error) {
      uiManager.showNotification(error.message || 'Failed to delete', 'error');
    }
  },

  getColorCode(colorName) {
    const colors = {
      'hitam': '#1a1a1a', 'black': '#1a1a1a',
      'putih': '#f5f5f5', 'white': '#f5f5f5',
      'merah': '#ef4444', 'red': '#ef4444',
      'biru': '#3b82f6', 'blue': '#3b82f6',
      'hijau': '#22c55e', 'green': '#22c55e',
      'kuning': '#eab308', 'yellow': '#eab308',
      'orange': '#f97316', 'oranye': '#f97316',
      'silver': '#9ca3af', 'abu-abu': '#6b7280', 'gray': '#6b7280',
      'coklat': '#92400e', 'brown': '#92400e',
    };
    return colors[(colorName || '').toLowerCase()] || '#6b7280';
  },

  formatDate(timestamp) {
    if (!timestamp) return '-';
    return new Date(timestamp).toLocaleDateString('en-US', {
      year: 'numeric', month: 'short', day: 'numeric'
    });
  },

  cleanup() {}
};
