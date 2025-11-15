// Calibration Page Component
const CalibrationPage = {
  state: {
    calibrations: [],
    editingCalibration: null,
    rows: []
  },

  async render() {
    uiManager.setPageTitle('Calibration');
    
    const container = document.getElementById('page-container');
    container.innerHTML = `
      <div class="page-header">
        <h1 class="page-title">Camera Calibration</h1>
        <p class="page-description">Configure camera parameters for empty space detection</p>
      </div>
      
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Calibration List</h2>
          <button id="new-calibration-btn" class="btn btn-primary">New Calibration</button>
        </div>
        <div class="card-body">
          <div id="calibration-list"></div>
        </div>
      </div>
      
      <div id="calibration-form-section" class="card" style="display: none;">
        <div class="card-header">
          <h2 class="card-title" id="form-title">New Calibration</h2>
        </div>
        <div class="card-body">
          <form id="calibration-form">
            <div class="form-group">
              <label for="camera-id-input">Camera ID *</label>
              <input type="text" id="camera-id-input" class="form-control" required>
            </div>
            
            <div class="form-group">
              <label>Parking Rows *</label>
              <div id="rows-container"></div>
              <button type="button" id="add-row-btn" class="btn btn-sm btn-secondary mt-1">Add Row</button>
              <small class="form-error" style="color: var(--text-secondary); display: block; margin-top: var(--spacing-xs);">
                Y coordinates must be in descending order (bottom to top). Row 0 = bottom (largest Y), Row 1, 2... = going up (smaller Y)
              </small>
            </div>
            
            <div class="form-group">
              <label for="min-space-width-input">Min Space Width (pixels) *</label>
              <input type="number" id="min-space-width-input" class="form-control" min="10" max="500" required>
              <small class="form-error" style="color: var(--text-secondary); display: block; margin-top: var(--spacing-xs);">
                Range: 10-500 pixels
              </small>
            </div>
            
            <div class="form-group">
              <label for="space-coefficient-input">Space Coefficient *</label>
              <input type="number" id="space-coefficient-input" class="form-control" min="0.1" max="1.0" step="0.1" required>
              <small class="form-error" style="color: var(--text-secondary); display: block; margin-top: var(--spacing-xs);">
                Range: 0.1-1.0 (perspective reduction factor)
              </small>
            </div>
            
            <div class="form-group">
              <label for="row-start-x-input">Row Start X (pixels)</label>
              <input type="number" id="row-start-x-input" class="form-control" value="0">
            </div>
            
            <div class="form-group">
              <label for="row-end-x-input">Row End X (pixels)</label>
              <input type="number" id="row-end-x-input" class="form-control" value="1920">
            </div>
            
            <div id="form-errors" class="form-error" style="display: none;"></div>
          </form>
        </div>
        <div class="card-footer">
          <button id="save-calibration-btn" class="btn btn-primary">Save Calibration</button>
          <button id="cancel-form-btn" class="btn btn-secondary">Cancel</button>
        </div>
      </div>
      
      <!-- Detail Modal -->
      <div id="detail-modal" class="modal" style="display: none;">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Calibration Details</h3>
          </div>
          <div class="modal-body" id="detail-content"></div>
          <div class="modal-footer">
            <button id="close-detail-btn" class="btn btn-secondary">Close</button>
          </div>
        </div>
      </div>
    `;
    
    await this.loadCalibrations();
    this.setupEventListeners();
  },

  setupEventListeners() {
    // New calibration button
    document.getElementById('new-calibration-btn').addEventListener('click', () => {
      this.showForm();
    });
    
    // Add row button
    document.getElementById('add-row-btn').addEventListener('click', () => {
      this.addRow();
    });
    
    // Save button
    document.getElementById('save-calibration-btn').addEventListener('click', () => {
      this.saveCalibration();
    });
    
    // Cancel button
    document.getElementById('cancel-form-btn').addEventListener('click', () => {
      this.hideForm();
    });
    
    // Close detail modal
    document.getElementById('close-detail-btn').addEventListener('click', () => {
      document.getElementById('detail-modal').style.display = 'none';
    });
  },

  async loadCalibrations() {
    try {
      uiManager.showLoading();
      const data = await apiClient.getCalibrations();
      // Backend returns array directly, not wrapped in object
      this.state.calibrations = Array.isArray(data) ? data : (data.calibrations || []);
      console.log('[Calibration] Loaded calibrations:', this.state.calibrations);
      this.renderCalibrationList();
    } catch (error) {
      console.error('[Calibration] Load error:', error);
      uiManager.showNotification(error.message || 'Failed to load calibrations', 'error');
    } finally {
      uiManager.hideLoading();
    }
  },

  renderCalibrationList() {
    const container = document.getElementById('calibration-list');
    
    if (this.state.calibrations.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon"><i class="fas fa-cog"></i></div>
          <div class="empty-state-message">No calibrations found</div>
          <div class="empty-state-description">Create a new calibration to get started</div>
        </div>
      `;
      return;
    }
    
    const columns = [
      { key: 'camera_id', label: 'Camera ID' },
      { key: 'rows', label: 'Rows', render: (row) => row.rows?.length || 0 },
      { key: 'min_space_width', label: 'Min Space Width', render: (row) => `${row.min_space_width}px` },
      { key: 'space_coefficient', label: 'Coefficient', render: (row) => row.space_coefficient },
      { key: 'actions', label: 'Actions', render: (row) => `
        <div class="table-actions">
          <button class="btn btn-sm btn-secondary" onclick="CalibrationPage.viewDetail('${row.camera_id}')">View</button>
          <button class="btn btn-sm btn-primary" onclick="CalibrationPage.editCalibration('${row.camera_id}')">Edit</button>
          <button class="btn btn-sm btn-danger" onclick="CalibrationPage.deleteCalibration('${row.camera_id}')">Delete</button>
        </div>
      `}
    ];
    
    uiManager.renderTable(container, this.state.calibrations, columns);
  },

  showForm(calibration = null) {
    this.state.editingCalibration = calibration;
    this.state.rows = calibration?.rows || [];
    
    const formSection = document.getElementById('calibration-form-section');
    const formTitle = document.getElementById('form-title');
    
    formTitle.textContent = calibration ? 'Edit Calibration' : 'New Calibration';
    formSection.style.display = 'block';
    
    // Fill form if editing
    if (calibration) {
      document.getElementById('camera-id-input').value = calibration.camera_id;
      document.getElementById('camera-id-input').disabled = true;
      document.getElementById('min-space-width-input').value = calibration.min_space_width;
      document.getElementById('space-coefficient-input').value = calibration.space_coefficient;
      document.getElementById('row-start-x-input').value = calibration.row_start_x || 0;
      document.getElementById('row-end-x-input').value = calibration.row_end_x || 1920;
    } else {
      document.getElementById('calibration-form').reset();
      document.getElementById('camera-id-input').disabled = false;
      this.state.rows = [];
    }
    
    // Render rows
    this.renderRows();
    
    // Add initial row if none
    if (this.state.rows.length === 0) {
      this.addRow();
    }
    
    // Scroll to form
    formSection.scrollIntoView({ behavior: 'smooth' });
  },

  hideForm() {
    document.getElementById('calibration-form-section').style.display = 'none';
    document.getElementById('calibration-form').reset();
    document.getElementById('form-errors').style.display = 'none';
    this.state.editingCalibration = null;
    this.state.rows = [];
  },

  addRow() {
    const rowIndex = this.state.rows.length;
    this.state.rows.push({
      row_index: rowIndex,
      y_coordinate: '',
      label: `Row ${rowIndex + 1}`
    });
    this.renderRows();
  },

  removeRow(index) {
    this.state.rows.splice(index, 1);
    // Re-index rows
    this.state.rows.forEach((row, i) => {
      row.row_index = i;
    });
    this.renderRows();
  },

  renderRows() {
    const container = document.getElementById('rows-container');
    container.innerHTML = '';
    
    this.state.rows.forEach((row, index) => {
      const rowEl = document.createElement('div');
      rowEl.style.cssText = 'display: grid; grid-template-columns: 80px 1fr 1fr 40px; gap: var(--spacing-sm); margin-bottom: var(--spacing-sm); align-items: center;';
      rowEl.innerHTML = `
        <input type="number" value="${row.row_index}" disabled class="form-control" style="background: var(--bg-tertiary);">
        <input type="number" id="row-y-${index}" value="${row.y_coordinate}" placeholder="Y Coordinate" class="form-control" required>
        <input type="text" id="row-label-${index}" value="${row.label}" placeholder="Label" class="form-control">
        <button type="button" class="btn btn-sm btn-danger" onclick="CalibrationPage.removeRow(${index})">×</button>
      `;
      container.appendChild(rowEl);
    });
  },

  validateForm() {
    const errors = [];
    
    // Validate camera ID
    const cameraId = document.getElementById('camera-id-input').value.trim();
    if (!cameraId) {
      errors.push('Camera ID is required');
    }
    
    // Validate rows
    if (this.state.rows.length === 0) {
      errors.push('At least one row is required');
    }
    
    if (this.state.rows.length > 10) {
      errors.push('Maximum 10 rows allowed');
    }
    
    // Get Y coordinates
    const yCoordinates = [];
    this.state.rows.forEach((row, index) => {
      const yInput = document.getElementById(`row-y-${index}`);
      const y = parseFloat(yInput.value);
      
      if (isNaN(y) || y < 0) {
        errors.push(`Row ${index}: Invalid Y coordinate`);
      } else {
        yCoordinates.push(y);
      }
    });
    
    // Check descending order (bottom to top)
    // Row 0 should have largest Y (bottom), Row 1, 2... smaller Y (going up)
    for (let i = 1; i < yCoordinates.length; i++) {
      if (yCoordinates[i] >= yCoordinates[i - 1]) {
        errors.push('Y coordinates must be in descending order (bottom to top). Row 0 = largest Y, Row 1, 2... smaller Y');
        break;
      }
    }
    
    // Validate min space width
    const minSpaceWidth = parseFloat(document.getElementById('min-space-width-input').value);
    if (isNaN(minSpaceWidth) || minSpaceWidth < 10 || minSpaceWidth > 500) {
      errors.push('Min space width must be between 10 and 500');
    }
    
    // Validate space coefficient
    const spaceCoefficient = parseFloat(document.getElementById('space-coefficient-input').value);
    if (isNaN(spaceCoefficient) || spaceCoefficient < 0.1 || spaceCoefficient > 1.0) {
      errors.push('Space coefficient must be between 0.1 and 1.0');
    }
    
    return errors;
  },

  async saveCalibration() {
    // Validate form
    const errors = this.validateForm();
    const errorContainer = document.getElementById('form-errors');
    
    if (errors.length > 0) {
      errorContainer.innerHTML = errors.join('<br>');
      errorContainer.style.display = 'block';
      uiManager.showNotification('Please fix form errors', 'error');
      return;
    }
    
    errorContainer.style.display = 'none';
    
    // Collect form data
    const rows = this.state.rows.map((row, index) => ({
      row_index: index,
      y_coordinate: parseFloat(document.getElementById(`row-y-${index}`).value),
      label: document.getElementById(`row-label-${index}`).value.trim()
    }));
    
    const data = {
      camera_id: document.getElementById('camera-id-input').value.trim(),
      rows: rows,
      min_space_width: parseFloat(document.getElementById('min-space-width-input').value),
      space_coefficient: parseFloat(document.getElementById('space-coefficient-input').value),
      row_start_x: parseInt(document.getElementById('row-start-x-input').value) || 0,
      row_end_x: parseInt(document.getElementById('row-end-x-input').value) || 1920
    };
    
    try {
      uiManager.showLoading();
      
      if (this.state.editingCalibration) {
        await apiClient.updateCalibration(data.camera_id, data);
        uiManager.showNotification('Calibration updated successfully', 'success');
      } else {
        await apiClient.createCalibration(data);
        uiManager.showNotification('Calibration created successfully', 'success');
      }
      
      this.hideForm();
      await this.loadCalibrations();
      
      // Scroll to top to show the list
      window.scrollTo({ top: 0, behavior: 'smooth' });
      
    } catch (error) {
      console.error('[Calibration] Save error:', error);
      uiManager.showNotification(error.message || 'Failed to save calibration', 'error');
    } finally {
      uiManager.hideLoading();
    }
  },

  async editCalibration(cameraId) {
    try {
      uiManager.showLoading();
      const calibration = await apiClient.getCalibration(cameraId);
      this.showForm(calibration);
    } catch (error) {
      console.error('[Calibration] Load error:', error);
      uiManager.showNotification(error.message || 'Failed to load calibration', 'error');
    } finally {
      uiManager.hideLoading();
    }
  },

  async deleteCalibration(cameraId) {
    const confirmed = await uiManager.showConfirm(`Are you sure you want to delete calibration for camera "${cameraId}"?`);
    
    if (!confirmed) return;
    
    try {
      uiManager.showLoading();
      await apiClient.deleteCalibration(cameraId);
      uiManager.showNotification('Calibration deleted successfully', 'success');
      await this.loadCalibrations();
    } catch (error) {
      console.error('[Calibration] Delete error:', error);
      uiManager.showNotification(error.message || 'Failed to delete calibration', 'error');
    } finally {
      uiManager.hideLoading();
    }
  },

  async viewDetail(cameraId) {
    try {
      uiManager.showLoading();
      const calibration = await apiClient.getCalibration(cameraId);
      
      const content = document.getElementById('detail-content');
      content.innerHTML = `
        <div style="margin-bottom: var(--spacing-md);">
          <strong>Camera ID:</strong> ${calibration.camera_id}
        </div>
        <div style="margin-bottom: var(--spacing-md);">
          <strong>Min Space Width:</strong> ${calibration.min_space_width} pixels
        </div>
        <div style="margin-bottom: var(--spacing-md);">
          <strong>Space Coefficient:</strong> ${calibration.space_coefficient}
        </div>
        <div style="margin-bottom: var(--spacing-md);">
          <strong>Row Boundaries:</strong> X: ${calibration.row_start_x || 0} - ${calibration.row_end_x || 1920}
        </div>
        <div style="margin-bottom: var(--spacing-md);">
          <strong>Rows:</strong>
          <table class="table" style="margin-top: var(--spacing-sm);">
            <thead>
              <tr>
                <th>Index</th>
                <th>Y Coordinate</th>
                <th>Label</th>
              </tr>
            </thead>
            <tbody>
              ${calibration.rows.map(row => `
                <tr>
                  <td>${row.row_index}</td>
                  <td>${row.y_coordinate}</td>
                  <td>${row.label || 'N/A'}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
        <div style="margin-bottom: var(--spacing-md);">
          <strong>Created:</strong> ${uiManager.formatDateTime(calibration.created_at)}
        </div>
        <div>
          <strong>Updated:</strong> ${uiManager.formatDateTime(calibration.updated_at)}
        </div>
      `;
      
      document.getElementById('detail-modal').style.display = 'flex';
      
    } catch (error) {
      console.error('[Calibration] Load detail error:', error);
      uiManager.showNotification(error.message || 'Failed to load calibration details', 'error');
    } finally {
      uiManager.hideLoading();
    }
  }
};
