// Upload Page Component
const UploadPage = {
  state: {
    sessionId: '',
    cameraId: '',
    files: [],
    uploadProgress: {},
    isUploading: false,
    allUploaded: false,
    cameraUrl: '',
    cameraConnected: false,
    refreshInterval: null,
    rotation: 90 // Default 90° for portrait camera (724x1280)
  },

  async render() {
    uiManager.setPageTitle('Integrate Camera');

    // Load saved camera URL from localStorage
    const savedCameraUrl = localStorage.getItem('parkit_camera_url') || '';

    const container = document.getElementById('page-container');
    container.innerHTML = `
      <div class="page-header">
        <h1 class="page-title">Integrate Camera</h1>
        <p class="page-description">Connect to camera stream or upload frames manually</p>
      </div>
      
      <div class="card" overflow-x: hidden;">
        <div class="card-header">
          <h2 class="card-title">Camera Stream</h2>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label for="camera-url">Camera URL (DroidCam/IP Camera)</label>
            <div style="display: flex; gap: var(--spacing-sm);">
              <input type="text" id="camera-url" class="form-control" placeholder="http://192.168.1.100:4747/video" value="${savedCameraUrl}">
              <button id="connect-camera-btn" class="btn btn-primary">Connect</button>
              <button id="disconnect-camera-btn" class="btn btn-secondary" style="display: none;">Disconnect</button>
            </div>
            <small style="color: var(--text-secondary); display: block; margin-top: var(--spacing-xs);">
              Example: http://192.168.1.100:4747/video (DroidCam) - URL will be saved automatically
            </small>
          </div>
          
          <div id="camera-preview-container" style="display: none; margin-top: var(--spacing-lg); margin-bottom: var(--spacing-lg); position: relative;">
            <div id="preview-wrapper" style="background: var(--bg-tertiary); border-radius: 8px; padding: var(--spacing-md); display: flex; justify-content: center; align-items: center; position: relative; margin: 0 auto; min-height: 100vh;">
              <div id="coordinate-display" style="position: absolute; background: rgba(0,0,0,0.9); color: white; padding: 8px 12px; border-radius: 6px; font-family: monospace; font-size: 14px; font-weight: bold; z-index: 100; box-shadow: 0 2px 8px rgba(0,0,0,0.3); pointer-events: none; display: none;">
                X: 0, Y: 0
              </div>
              <div style="position: relative; display: inline-block;">
                <img id="camera-preview" style="max-width: 100%; max-height: 50vh; width: auto; height: auto; display: block; transition: transform 0.3s ease;" alt="Camera Preview">
                <canvas id="coordinate-overlay" style="position: absolute; top: 0; left: 0; pointer-events: none;"></canvas>
              </div>
            </div>
            <div style="margin-top: var(--spacing-md); display: flex; gap: var(--spacing-sm); align-items: center; flex-wrap: wrap;">
              <button id="capture-frame-btn" class="btn btn-success">
                <i class="fas fa-camera"></i> Capture Frame
              </button>
              <small style="color: var(--text-secondary);">
                Camera in portrait mode (724x1280) - Click to mark coordinates
              </small>
            </div>
          </div>
        </div>
      </div>
      
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Session Configuration</h2>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label for="session-id">Session ID *</label>
            <div style="display: flex; gap: var(--spacing-sm);">
              <input type="text" id="session-id" class="form-control" placeholder="Enter session ID" required value="${localStorage.getItem('parkit_last_session_id') || ''}">
              <button id="generate-uuid-btn" class="btn btn-secondary">Generate UUID</button>
            </div>
          </div>
          
          <div class="form-group">
            <label for="camera-id">Camera ID (Optional)</label>
            <input type="text" id="camera-id" class="form-control" placeholder="Enter camera ID for calibration" value="${localStorage.getItem('parkit_last_camera_id') || ''}">
            <small class="form-error" style="color: var(--text-secondary);">Required for empty space detection - will be saved automatically</small>
          </div>
        </div>
      </div>
      
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Select Files</h2>
        </div>
        <div class="card-body">
          <div class="form-group">
            <input type="file" id="file-input" multiple accept="image/jpeg,image/jpg,image/png" style="display: none;">
            <button id="select-files-btn" class="btn btn-primary">Select Images</button>
            <small class="form-error" style="color: var(--text-secondary); display: block; margin-top: var(--spacing-sm);">
              Supported formats: JPG, JPEG, PNG. Max size: 10MB per file
            </small>
          </div>
          
          <div id="preview-container" style="display: none;">
            <h3 style="margin-bottom: var(--spacing-md);">Selected Files (<span id="file-count">0</span>)</h3>
            <div id="preview-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: var(--spacing-md);"></div>
          </div>
        </div>
        <div class="card-footer">
          <button id="upload-btn" class="btn btn-primary" disabled>Upload Frames</button>
          <button id="clear-btn" class="btn btn-secondary">Clear All</button>
        </div>
      </div>
      
      <div id="complete-section" class="card" style="display: none;">
        <div class="card-header">
          <h2 class="card-title">Complete Session</h2>
        </div>
        <div class="card-body">
          <p>All frames have been uploaded successfully. Click the button below to complete the session and process the detection.</p>
        </div>
        <div class="card-footer">
          <button id="complete-session-btn" class="btn btn-success">Complete Session</button>
        </div>
      </div>
    `;

    this.setupEventListeners();
  },

  setupEventListeners() {
    // Camera connection
    document.getElementById('connect-camera-btn').addEventListener('click', () => {
      this.connectCamera();
    });

    document.getElementById('disconnect-camera-btn').addEventListener('click', () => {
      this.disconnectCamera();
    });

    // Capture frame from camera
    document.getElementById('capture-frame-btn').addEventListener('click', () => {
      this.captureFrame();
    });

    // Mouse move on camera preview for coordinates
    const preview = document.getElementById('camera-preview');
    preview.addEventListener('mousemove', (e) => {
      this.updateCoordinates(e);
    });

    preview.addEventListener('mouseleave', () => {
      document.getElementById('coordinate-display').style.display = 'none';
    });

    preview.addEventListener('click', (e) => {
      this.drawCoordinate(e);
    });

    // Generate UUID button
    document.getElementById('generate-uuid-btn').addEventListener('click', () => {
      const uuid = uiManager.generateUUID();
      document.getElementById('session-id').value = uuid;
      localStorage.setItem('parkit_last_session_id', uuid);
    });

    // Auto-save session ID and camera ID on change
    document.getElementById('session-id').addEventListener('change', (e) => {
      localStorage.setItem('parkit_last_session_id', e.target.value);
    });

    document.getElementById('camera-id').addEventListener('change', (e) => {
      localStorage.setItem('parkit_last_camera_id', e.target.value);
    });

    // Select files button
    document.getElementById('select-files-btn').addEventListener('click', () => {
      document.getElementById('file-input').click();
    });

    // File input change
    document.getElementById('file-input').addEventListener('change', (e) => {
      this.handleFileSelection(e.target.files);
    });

    // Upload button
    document.getElementById('upload-btn').addEventListener('click', () => {
      this.uploadFiles();
    });

    // Clear button
    document.getElementById('clear-btn').addEventListener('click', () => {
      this.clearFiles();
    });

    // Complete session button
    document.getElementById('complete-session-btn').addEventListener('click', () => {
      this.completeSession();
    });
  },

  handleFileSelection(files) {
    // Validate files
    const validFiles = [];
    const errors = [];

    Array.from(files).forEach(file => {
      // Check file type
      if (!CONFIG.ALLOWED_FILE_TYPES.includes(file.type)) {
        errors.push(`${file.name}: Invalid file type`);
        return;
      }

      // Check file size
      if (file.size > CONFIG.MAX_FILE_SIZE) {
        errors.push(`${file.name}: File too large (max 10MB)`);
        return;
      }

      validFiles.push(file);
    });

    if (errors.length > 0) {
      uiManager.showNotification(errors.join(', '), 'error');
    }

    if (validFiles.length > 0) {
      this.state.files = validFiles;
      this.renderPreviews();
      document.getElementById('upload-btn').disabled = false;
    }
  },

  renderPreviews() {
    const container = document.getElementById('preview-grid');
    const previewContainer = document.getElementById('preview-container');
    const fileCount = document.getElementById('file-count');

    previewContainer.style.display = 'block';
    fileCount.textContent = this.state.files.length;

    container.innerHTML = '';

    this.state.files.forEach((file, index) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const preview = document.createElement('div');
        preview.className = 'file-preview';
        preview.innerHTML = `
          <div style="border: 1px solid var(--border-color); border-radius: 6px; overflow: hidden;">
            <img src="${e.target.result}" style="width: 100%; height: 150px; object-fit: cover;">
            <div style="padding: var(--spacing-sm); background: var(--bg-secondary);">
              <div style="font-size: var(--font-size-sm); margin-bottom: var(--spacing-xs); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${file.name}</div>
              <div style="font-size: var(--font-size-xs); color: var(--text-secondary);">${(file.size / 1024).toFixed(1)} KB</div>
              <div id="progress-${index}" style="margin-top: var(--spacing-sm); display: none;">
                ${uiManager.createProgressBar(0)}
                <div id="status-${index}" style="font-size: var(--font-size-xs); margin-top: var(--spacing-xs); text-align: center;"></div>
              </div>
            </div>
          </div>
        `;
        container.appendChild(preview);
      };
      reader.readAsDataURL(file);
    });
  },

  async uploadFiles() {
    // Validate session ID
    const sessionId = document.getElementById('session-id').value.trim();
    if (!sessionId) {
      uiManager.showNotification('Session ID is required', 'error');
      return;
    }

    const cameraId = document.getElementById('camera-id').value.trim() || null;

    this.state.sessionId = sessionId;
    this.state.cameraId = cameraId;
    this.state.isUploading = true;
    this.state.allUploaded = false;

    // Disable buttons
    document.getElementById('upload-btn').disabled = true;
    document.getElementById('select-files-btn').disabled = true;

    // Upload each file
    let successCount = 0;
    let failCount = 0;

    for (let i = 0; i < this.state.files.length; i++) {
      const file = this.state.files[i];
      const progressEl = document.getElementById(`progress-${i}`);
      const statusEl = document.getElementById(`status-${i}`);

      progressEl.style.display = 'block';
      statusEl.textContent = 'Uploading...';

      try {
        // Simulate progress (since fetch doesn't support upload progress easily)
        uiManager.updateProgressBar(progressEl, 50, 'default');

        await apiClient.uploadFrame(file, sessionId, cameraId);

        uiManager.updateProgressBar(progressEl, 100, 'success');
        statusEl.textContent = '✓ Uploaded';
        statusEl.style.color = 'var(--success-color)';
        successCount++;

      } catch (error) {
        console.error(`[Upload] Failed to upload ${file.name}:`, error);
        uiManager.updateProgressBar(progressEl, 100, 'error');
        statusEl.textContent = '✕ Failed';
        statusEl.style.color = 'var(--error-color)';
        failCount++;
      }
    }

    this.state.isUploading = false;

    // Show results
    if (successCount > 0) {
      uiManager.showNotification(`${successCount} file(s) uploaded successfully`, 'success');
      this.state.allUploaded = true;
      document.getElementById('complete-section').style.display = 'block';
    }

    if (failCount > 0) {
      uiManager.showNotification(`${failCount} file(s) failed to upload`, 'error');
    }
  },

  async completeSession() {
    if (!this.state.sessionId) {
      uiManager.showNotification('No session to complete', 'error');
      return;
    }

    try {
      uiManager.showLoading();
      await apiClient.completeSession(this.state.sessionId);
      uiManager.showNotification('Session completed successfully', 'success');

      // Navigate to results page
      setTimeout(() => {
        router.navigate('/results');
      }, 1500);

    } catch (error) {
      console.error('[Upload] Complete session error:', error);
      uiManager.showNotification(error.message || 'Failed to complete session', 'error');
    } finally {
      uiManager.hideLoading();
    }
  },

  clearFiles() {
    this.state.files = [];
    this.state.uploadProgress = {};
    this.state.allUploaded = false;

    document.getElementById('file-input').value = '';
    document.getElementById('preview-container').style.display = 'none';
    document.getElementById('complete-section').style.display = 'none';
    document.getElementById('upload-btn').disabled = true;
    document.getElementById('select-files-btn').disabled = false;
  },

  // Camera Integration Functions
  connectCamera() {
    const url = document.getElementById('camera-url').value.trim();

    if (!url) {
      uiManager.showNotification('Please enter camera URL', 'error');
      return;
    }

    // Save URL to localStorage
    localStorage.setItem('parkit_camera_url', url);

    this.state.cameraUrl = url;
    this.state.cameraConnected = true;

    const preview = document.getElementById('camera-preview');
    const container = document.getElementById('camera-preview-container');
    const canvas = document.getElementById('coordinate-overlay');

    // Set crossOrigin to avoid CORS tainted canvas issue
    preview.crossOrigin = 'anonymous';
    
    // Set image source with timestamp to avoid caching
    preview.src = url + '?t=' + new Date().getTime();

    preview.onload = () => {
      // Canvas size follows camera: swap width/height because of 90° rotation
      // Original camera is landscape (e.g. 1280x720), after rotation becomes portrait (720x1280)
      canvas.width = preview.naturalHeight;  // Portrait width
      canvas.height = preview.naturalWidth;  // Portrait height

      // Canvas display size matches preview
      canvas.style.width = preview.width + 'px';
      canvas.style.height = preview.height + 'px';

      console.log('Camera size:', preview.naturalWidth, 'x', preview.naturalHeight, '-> Canvas:', canvas.width, 'x', canvas.height);

      // Apply default 90° rotation
      preview.style.transform = 'rotate(90deg)';
      canvas.style.transform = 'rotate(90deg)';

      container.style.display = 'block';
      document.getElementById('connect-camera-btn').style.display = 'none';
      document.getElementById('disconnect-camera-btn').style.display = 'inline-block';

      uiManager.showNotification('Camera connected (Portrait mode 90°)', 'success');

      // Refresh image periodically for live stream (slower to avoid errors)
      this.refreshCameraStream();
    };

    preview.onerror = () => {
      console.error('[Camera] Failed to load image from:', url);
      // Don't auto-disconnect on first error, might be temporary
      if (!this.state.cameraConnected) {
        uiManager.showNotification('Failed to connect to camera. Check URL and network.', 'error');
      }
    };
  },

  refreshCameraStream() {
    if (!this.state.cameraConnected) return;

    const preview = document.getElementById('camera-preview');
    const url = this.state.cameraUrl;

    // Create new image to preload
    const img = new Image();
    img.onload = () => {
      if (this.state.cameraConnected) {
        preview.src = img.src;
        // Schedule next refresh
        this.state.refreshInterval = setTimeout(() => this.refreshCameraStream(), 500);
      }
    };

    img.onerror = () => {
      // Retry on error with longer delay
      if (this.state.cameraConnected) {
        this.state.refreshInterval = setTimeout(() => this.refreshCameraStream(), 2000);
      }
    };

    // Load new frame with timestamp
    img.src = url + '?t=' + new Date().getTime();
  },

  disconnectCamera() {
    this.state.cameraConnected = false;
    this.state.rotation = 90; // Reset to default 90°

    // Clear timeout instead of interval
    if (this.state.refreshInterval) {
      clearTimeout(this.state.refreshInterval);
      this.state.refreshInterval = null;
    }

    document.getElementById('camera-preview-container').style.display = 'none';
    document.getElementById('connect-camera-btn').style.display = 'inline-block';
    document.getElementById('disconnect-camera-btn').style.display = 'none';

    const preview = document.getElementById('camera-preview');
    preview.src = '';
    preview.style.transform = 'rotate(90deg)';
    preview.onload = null;
    preview.onerror = null;

    const canvas = document.getElementById('coordinate-overlay');
    canvas.style.transform = 'rotate(90deg)';
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    uiManager.showNotification('Camera disconnected', 'info');
  },

  updateCoordinates(e) {
    const preview = e.target;
    const rect = preview.getBoundingClientRect();
    const coordDisplay = document.getElementById('coordinate-display');
    const canvas = document.getElementById('coordinate-overlay');

    // Calculate display coordinates
    const displayX = e.clientX - rect.left;
    const displayY = e.clientY - rect.top;

    // Canvas is rotated 90°, so we need to swap width/height when scaling
    // rect.width is the rotated width (narrow), rect.height is rotated height (tall)
    // canvas.width = 724 (portrait width), canvas.height = 1280 (portrait height)
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    // Portrait coordinates: kiri atas = (0,0)
    const actualX = Math.round(displayX * scaleX);
    const actualY = Math.round(displayY * scaleY);

    // Debug
    console.log('Canvas:', canvas.width, 'x', canvas.height, 'Rect:', rect.width, 'x', rect.height, 'Scale:', scaleX, scaleY, 'Coords:', actualX, actualY);

    // Update text
    coordDisplay.textContent = `X: ${actualX}, Y: ${actualY}`;

    // Position relative to preview wrapper (not absolute to page)
    const wrapper = document.getElementById('preview-wrapper');
    const wrapperRect = wrapper.getBoundingClientRect();

    coordDisplay.style.display = 'block';
    coordDisplay.style.left = (e.clientX - wrapperRect.left + 15) + 'px';
    coordDisplay.style.top = (e.clientY - wrapperRect.top + 15) + 'px';
  },

  drawCoordinate(e) {
    const preview = e.target;
    const rect = preview.getBoundingClientRect();
    const canvas = document.getElementById('coordinate-overlay');
    const ctx = canvas.getContext('2d');

    // Calculate click position
    const displayX = e.clientX - rect.left;
    const displayY = e.clientY - rect.top;

    // Scale to canvas size (which is 724x1280)
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    // Portrait coordinates: kiri atas = (0,0)
    const actualX = Math.round(displayX * scaleX);
    const actualY = Math.round(displayY * scaleY);

    // Clear previous marks
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw directly at portrait coordinates
    const canvasX = actualX;
    const canvasY = actualY;

    ctx.strokeStyle = '#00ff00';
    ctx.lineWidth = 3;

    // Horizontal line
    ctx.beginPath();
    ctx.moveTo(canvasX - 20, canvasY);
    ctx.lineTo(canvasX + 20, canvasY);
    ctx.stroke();

    // Vertical line
    ctx.beginPath();
    ctx.moveTo(canvasX, canvasY - 20);
    ctx.lineTo(canvasX, canvasY + 20);
    ctx.stroke();

    // Draw coordinate text
    ctx.fillStyle = '#00ff00';
    ctx.font = 'bold 16px monospace';
    ctx.fillText(`(${actualX}, ${actualY})`, canvasX + 25, canvasY - 10);

    console.log('[Camera] Clicked at display:', displayX, displayY, '-> Original coords:', actualX, actualY);
  },

  async captureFrame() {
    try {
      const preview = document.getElementById('camera-preview');

      if (!preview || !preview.complete || !preview.naturalWidth) {
        throw new Error('Image not loaded');
      }

      // Create canvas to capture image with 90° rotation
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');

      // Swap width and height for 90° rotation (portrait)
      canvas.width = preview.naturalHeight;
      canvas.height = preview.naturalWidth;

      console.log('[Capture] Canvas size:', canvas.width, 'x', canvas.height);

      // Apply 90° rotation transformation
      ctx.save();
      ctx.translate(canvas.width, 0);
      ctx.rotate(90 * Math.PI / 180);
      ctx.drawImage(preview, 0, 0);
      ctx.restore();

      // Convert to blob
      canvas.toBlob((blob) => {
        if (!blob) {
          console.error('[Capture] Failed to create blob');
          uiManager.showNotification('Failed to capture frame', 'error');
          return;
        }

        const file = new File([blob], `capture_${Date.now()}_portrait.jpg`, { type: 'image/jpeg' });

        // Add to files array
        this.state.files.push(file);
        this.renderPreviews();
        document.getElementById('upload-btn').disabled = false;

        uiManager.showNotification(`Frame captured (${canvas.width}x${canvas.height})`, 'success');
      }, 'image/jpeg', 0.95);

    } catch (error) {
      console.error('[Upload] Capture error:', error);
      uiManager.showNotification(`Failed to capture frame: ${error.message}`, 'error');
    }
  },

  cleanup() {
    // Disconnect camera when leaving page
    if (this.state.cameraConnected) {
      this.disconnectCamera();
    }
  }
};
