// Users Page Component
const UsersPage = {
  state: {
    users: [],
    filteredUsers: [],
    currentPage: 1,
    totalPages: 1,
    pageSize: 20,
    searchQuery: ''
  },

  async render() {
    uiManager.setPageTitle('Users');
    
    const container = document.getElementById('page-container');
    container.innerHTML = `
      <div class="page-header">
        <h1 class="page-title">User Management</h1>
        <p class="page-description">Manage system users and permissions</p>
      </div>
      
      <div class="card">
        <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
          <h2 class="card-title">Users</h2>
          <div style="display: flex; gap: var(--spacing-md); align-items: center;">
            <input type="text" id="search-input" class="form-control" placeholder="Search by username or email..." style="width: 300px;">
          </div>
        </div>
        <div class="card-body">
          <div id="users-table"></div>
          <div id="pagination-container"></div>
        </div>
      </div>
    `;
    
    await this.loadUsers();
    this.setupEventListeners();
  },

  setupEventListeners() {
    // Search input
    const searchInput = document.getElementById('search-input');
    let searchTimeout;
    
    searchInput.addEventListener('input', (e) => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        this.state.searchQuery = e.target.value.toLowerCase();
        this.filterUsers();
      }, 300);
    });
  },

  async loadUsers() {
    try {
      uiManager.showLoading();
      
      const params = {
        limit: 1000, // Load all users for client-side filtering
        skip: 0
      };
      
      const data = await apiClient.getUsers(params);
      this.state.users = data.users || [];
      this.filterUsers();
      
    } catch (error) {
      console.error('[Users] Load error:', error);
      uiManager.showNotification(error.message || 'Failed to load users', 'error');
    } finally {
      uiManager.hideLoading();
    }
  },

  filterUsers() {
    if (!this.state.searchQuery) {
      this.state.filteredUsers = this.state.users;
    } else {
      this.state.filteredUsers = this.state.users.filter(user => 
        user.username.toLowerCase().includes(this.state.searchQuery) ||
        (user.email && user.email.toLowerCase().includes(this.state.searchQuery))
      );
    }
    
    this.state.totalPages = Math.ceil(this.state.filteredUsers.length / this.state.pageSize);
    this.state.currentPage = 1;
    
    this.renderUsers();
    this.renderPagination();
  },

  renderUsers() {
    const container = document.getElementById('users-table');
    
    const startIndex = (this.state.currentPage - 1) * this.state.pageSize;
    const endIndex = startIndex + this.state.pageSize;
    const pageUsers = this.state.filteredUsers.slice(startIndex, endIndex);
    
    if (pageUsers.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon"><i class="fas fa-users"></i></div>
          <div class="empty-state-message">No users found</div>
        </div>
      `;
      return;
    }
    
    const columns = [
      { key: 'username', label: 'Username' },
      { key: 'email', label: 'Email', render: (row) => row.email || 'N/A' },
      { key: 'is_active', label: 'Status', render: (row) => {
        const badgeClass = row.is_active ? 'badge-success' : 'badge-error';
        return `<span class="badge ${badgeClass}">${row.is_active ? 'Active' : 'Inactive'}</span>`;
      }},
      { key: 'is_admin', label: 'Admin', render: (row) => row.is_admin ? '✓' : '✕' },
      { key: 'created_at', label: 'Created', render: (row) => uiManager.formatDateTime(row.created_at) },
      { key: 'actions', label: 'Actions', render: (row) => `
        <div class="table-actions">
          <label class="toggle-switch">
            <input type="checkbox" ${row.is_active ? 'checked' : ''} onchange="UsersPage.toggleUserActive('${row.username}', this.checked)">
            <span class="toggle-slider"></span>
          </label>
        </div>
      `}
    ];
    
    uiManager.renderTable(container, pageUsers, columns);
  },

  renderPagination() {
    const container = document.getElementById('pagination-container');
    uiManager.renderPagination(container, this.state.currentPage, this.state.totalPages, (page) => {
      this.state.currentPage = page;
      this.renderUsers();
    });
  },

  async toggleUserActive(username, isActive) {
    try {
      await apiClient.toggleUserActive(username);
      
      // Update local state
      const user = this.state.users.find(u => u.username === username);
      if (user) {
        user.is_active = !user.is_active;
      }
      
      uiManager.showNotification(`User ${username} ${user.is_active ? 'activated' : 'deactivated'}`, 'success');
      this.filterUsers();
      
    } catch (error) {
      console.error('[Users] Toggle active error:', error);
      uiManager.showNotification(error.message || 'Failed to update user status', 'error');
      // Reload to revert UI
      await this.loadUsers();
    }
  }
};
