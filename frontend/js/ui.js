// UI Manager for notifications, loading states, and utilities
class UIManager {
  constructor() {
    this.toastContainer = null;
    this.loadingOverlay = null;
    this.confirmModal = null;
  }

  // Initialize UI elements
  init() {
    this.toastContainer = document.getElementById('toast-container');
    this.loadingOverlay = document.getElementById('loading-overlay');
    this.confirmModal = document.getElementById('confirm-modal');
  }

  // Show toast notification
  showNotification(message, type = 'info') {
    if (!this.toastContainer) this.init();
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icons = {
      success: '<i class="fas fa-check-circle"></i>',
      error: '<i class="fas fa-times-circle"></i>',
      warning: '<i class="fas fa-exclamation-triangle"></i>',
      info: '<i class="fas fa-info-circle"></i>'
    };
    
    toast.innerHTML = `
      <span class="toast-icon">${icons[type] || icons.info}</span>
      <span class="toast-message">${message}</span>
      <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    this.toastContainer.appendChild(toast);
    
    // Auto-dismiss after duration
    setTimeout(() => {
      if (toast.parentElement) {
        toast.remove();
      }
    }, CONFIG.NOTIFICATION_DURATION);
  }

  // Show loading overlay
  showLoading(target = null) {
    if (target) {
      target.style.position = 'relative';
      target.style.opacity = '0.5';
      target.style.pointerEvents = 'none';
    } else if (this.loadingOverlay) {
      this.loadingOverlay.style.display = 'flex';
    }
  }

  // Hide loading overlay
  hideLoading(target = null) {
    if (target) {
      target.style.opacity = '1';
      target.style.pointerEvents = 'auto';
    } else if (this.loadingOverlay) {
      this.loadingOverlay.style.display = 'none';
    }
  }

  // Show confirmation dialog
  async showConfirm(message) {
    if (!this.confirmModal) this.init();
    
    return new Promise((resolve) => {
      const messageEl = document.getElementById('confirm-message');
      const okBtn = document.getElementById('confirm-ok');
      const cancelBtn = document.getElementById('confirm-cancel');
      
      messageEl.textContent = message;
      this.confirmModal.style.display = 'flex';
      
      const handleOk = () => {
        this.confirmModal.style.display = 'none';
        cleanup();
        resolve(true);
      };
      
      const handleCancel = () => {
        this.confirmModal.style.display = 'none';
        cleanup();
        resolve(false);
      };
      
      const cleanup = () => {
        okBtn.removeEventListener('click', handleOk);
        cancelBtn.removeEventListener('click', handleCancel);
      };
      
      okBtn.addEventListener('click', handleOk);
      cancelBtn.addEventListener('click', handleCancel);
    });
  }

  // Update page title
  setPageTitle(title) {
    document.title = `${title} - ParkIt Admin`;
  }

  // Render table with data
  renderTable(container, data, columns) {
    if (!data || data.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">📭</div>
          <div class="empty-state-message">No data available</div>
        </div>
      `;
      return;
    }
    
    let html = '<div class="table-container"><table class="table"><thead><tr>';
    
    // Table headers
    columns.forEach(col => {
      html += `<th>${col.label}</th>`;
    });
    html += '</tr></thead><tbody>';
    
    // Table rows
    data.forEach(row => {
      html += '<tr>';
      columns.forEach(col => {
        const value = col.render ? col.render(row) : row[col.key];
        html += `<td>${value}</td>`;
      });
      html += '</tr>';
    });
    
    html += '</tbody></table></div>';
    container.innerHTML = html;
  }

  // Render pagination
  renderPagination(container, currentPage, totalPages, onPageChange) {
    if (totalPages <= 1) {
      container.innerHTML = '';
      return;
    }
    
    let html = '<div class="pagination">';
    
    // Previous button
    html += `<button ${currentPage === 1 ? 'disabled' : ''} data-page="${currentPage - 1}">Previous</button>`;
    
    // Page numbers
    const maxVisible = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);
    
    if (endPage - startPage < maxVisible - 1) {
      startPage = Math.max(1, endPage - maxVisible + 1);
    }
    
    if (startPage > 1) {
      html += `<button data-page="1">1</button>`;
      if (startPage > 2) {
        html += '<span>...</span>';
      }
    }
    
    for (let i = startPage; i <= endPage; i++) {
      html += `<button class="${i === currentPage ? 'active' : ''}" data-page="${i}">${i}</button>`;
    }
    
    if (endPage < totalPages) {
      if (endPage < totalPages - 1) {
        html += '<span>...</span>';
      }
      html += `<button data-page="${totalPages}">${totalPages}</button>`;
    }
    
    // Next button
    html += `<button ${currentPage === totalPages ? 'disabled' : ''} data-page="${currentPage + 1}">Next</button>`;
    
    html += '</div>';
    container.innerHTML = html;
    
    // Add click handlers
    container.querySelectorAll('button[data-page]').forEach(btn => {
      btn.addEventListener('click', () => {
        const page = parseInt(btn.dataset.page);
        if (page >= 1 && page <= totalPages) {
          onPageChange(page);
        }
      });
    });
  }

  // Format date/time
  formatDateTime(timestamp) {
    if (!timestamp) return 'N/A';
    
    const date = new Date(timestamp);
    if (isNaN(date.getTime())) return 'Invalid Date';
    
    const options = {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    
    return date.toLocaleDateString('en-US', options);
  }

  // Format number with separators
  formatNumber(number) {
    if (typeof number !== 'number') return number;
    return number.toLocaleString('en-US');
  }

  // Generate UUID
  generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  // Escape HTML to prevent XSS
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Create progress bar
  createProgressBar(progress = 0) {
    return `
      <div class="progress">
        <div class="progress-bar" style="width: ${progress}%"></div>
      </div>
    `;
  }

  // Update progress bar
  updateProgressBar(element, progress, status = 'default') {
    const bar = element.querySelector('.progress-bar');
    if (bar) {
      bar.style.width = `${progress}%`;
      bar.className = `progress-bar ${status}`;
    }
  }
}

// Create global instance
const uiManager = new UIManager();

// Initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => uiManager.init());
} else {
  uiManager.init();
}
