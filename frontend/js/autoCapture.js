// Global Auto-Capture Manager
// Runs in background even when switching pages

const AutoCaptureManager = {
  state: {
    isRunning: false,
    sessionId: null,
    cameraId: null,
    cameraUrl: null,
    captureDelay: 5000, // Default 5 seconds
    captureCount: 0,
    captureInterval: null,
    previewImage: null,
    onStatusChange: null // Callback for UI updates
  },

  init() {
    // Load saved settings
    this.state.captureDelay = parseInt(localStorage.getItem('parkit_auto_delay') || '5000');
    this.state.cameraUrl = localStorage.getItem('parkit_camera_url') || '';
    console.log('[AutoCapture] Initialized with delay:', this.state.captureDelay);
  },

  start(sessionId, cameraId, cameraUrl) {
    if (this.state.isRunning) {
      console.log('[AutoCapture] Already running');
      return false;
    }

    if (!sessionId) {
      console.error('[AutoCapture] Session ID required');
      return false;
    }

    if (!cameraUrl) {
      console.error('[AutoCapture] Camera URL required');
      return false;
    }

    this.state.sessionId = sessionId;
    this.state.cameraId = cameraId;
    this.state.cameraUrl = cameraUrl;
    this.state.isRunning = true;
    this.state.captureCount = 0;

    // Save to localStorage
    localStorage.setItem('parkit_auto_session_id', sessionId);
    localStorage.setItem('parkit_auto_camera_id', cameraId || '');
    localStorage.setItem('parkit_camera_url', cameraUrl);

    console.log('[AutoCapture] Started - Session:', sessionId, 'Delay:', this.state.captureDelay);
    
    this.notifyStatusChange();
    this.runCapture();
    
    return true;
  },

  stop() {
    this.state.isRunning = false;
    
    if (this.state.captureInterval) {
      clearTimeout(this.state.captureInterval);
      this.state.captureInterval = null;
    }

    console.log('[AutoCapture] Stopped - Total captured:', this.state.captureCount);
    this.notifyStatusChange();
  },

  setDelay(delayMs) {
    this.state.captureDelay = delayMs;
    localStorage.setItem('parkit_auto_delay', delayMs.toString());
    console.log('[AutoCapture] Delay set to:', delayMs);
  },

  getStatus() {
    return {
      isRunning: this.state.isRunning,
      sessionId: this.state.sessionId,
      cameraId: this.state.cameraId,
      cameraUrl: this.state.cameraUrl,
      captureDelay: this.state.captureDelay,
      captureCount: this.state.captureCount
    };
  },

  onStatusChange(callback) {
    this.state.onStatusChange = callback;
  },

  notifyStatusChange() {
    if (this.state.onStatusChange) {
      this.state.onStatusChange(this.getStatus());
    }
  },

  async runCapture() {
    if (!this.state.isRunning) return;

    try {
      const blob = await this.captureFrame();
      
      if (blob) {
        const file = new File([blob], `auto_${Date.now()}.jpg`, { type: 'image/jpeg' });
        await apiClient.uploadFrame(file, this.state.sessionId, this.state.cameraId);
        
        this.state.captureCount++;
        console.log(`[AutoCapture] Frame ${this.state.captureCount} uploaded`);
        this.notifyStatusChange();
      }
    } catch (error) {
      console.error('[AutoCapture] Error:', error.message);
    }

    // Schedule next capture
    if (this.state.isRunning) {
      this.state.captureInterval = setTimeout(() => this.runCapture(), this.state.captureDelay);
    }
  },

  captureFrame() {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      
      img.onload = () => {
        try {
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');

          // 90° rotation (portrait)
          canvas.width = img.naturalHeight;
          canvas.height = img.naturalWidth;

          ctx.save();
          ctx.translate(canvas.width, 0);
          ctx.rotate(90 * Math.PI / 180);
          ctx.drawImage(img, 0, 0);
          ctx.restore();

          canvas.toBlob((blob) => {
            if (blob) resolve(blob);
            else reject(new Error('Blob creation failed'));
          }, 'image/jpeg', 0.95);
        } catch (e) {
          reject(e);
        }
      };

      img.onerror = () => reject(new Error('Image load failed'));
      img.src = this.state.cameraUrl + '?t=' + Date.now();
    });
  }
};

// Initialize on load
AutoCaptureManager.init();
