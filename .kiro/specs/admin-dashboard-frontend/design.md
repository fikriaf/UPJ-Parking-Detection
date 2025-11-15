# Design Document

## Overview

Admin Dashboard Frontend adalah single-page application (SPA) berbasis vanilla HTML, CSS, dan JavaScript yang menyediakan interface untuk administrator mengelola sistem ParkIt. Aplikasi ini berkomunikasi dengan backend FastAPI melalui REST API dan menggunakan API key untuk autentikasi. Design mengutamakan kesederhanaan, performa, dan kemudahan deployment dengan Docker.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser (Client)                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           Admin Dashboard (HTML/CSS/JS)               │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  │  │
│  │  │   Auth      │  │  API Client  │  │  UI Manager │  │  │
│  │  │   Manager   │  │              │  │             │  │  │
│  │  └─────────────┘  └──────────────┘  └─────────────┘  │  │
│  │         │                 │                 │          │  │
│  │         └─────────────────┴─────────────────┘          │  │
│  │                           │                             │  │
│  └───────────────────────────┼─────────────────────────────┘  │
└─────────────────────────────┼─────────────────────────────────┘
                              │ HTTP/REST API
                              │ (API Key in Header)
┌─────────────────────────────┼─────────────────────────────────┐
│                             ▼                                  │
│                    Backend FastAPI Server                      │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  /api/admin/*  │  /api/frames/*  │  /api/results/*      │ │
│  └──────────────────────────────────────────────────────────┘ │
│                             │                                  │
│                             ▼                                  │
│                      MongoDB Database                          │
└────────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Frontend**: Vanilla HTML5, CSS3, JavaScript (ES6+)
- **Web Server**: Nginx (untuk production deployment)
- **Containerization**: Docker
- **API Communication**: Fetch API
- **State Management**: LocalStorage untuk API key dan session data
- **UI Components**: Custom CSS dengan responsive design

### File Structure

```
frontend/
├── index.html                 # Main HTML file (SPA shell)
├── css/
│   ├── main.css              # Global styles
│   ├── components.css        # Reusable component styles
│   └── responsive.css        # Media queries
├── js/
│   ├── app.js                # Main application entry point
│   ├── auth.js               # Authentication management
│   ├── api.js                # API client wrapper
│   ├── router.js             # Client-side routing
│   ├── ui.js                 # UI utilities and notifications
│   └── pages/
│       ├── dashboard.js      # Dashboard page logic
│       ├── upload.js         # Frame upload page logic
│       ├── calibration.js    # Calibration management logic
│       ├── results.js        # Results monitoring logic
│       ├── sessions.js       # Session management logic
│       └── users.js          # User management logic
├── assets/
│   ├── logo.png              # ParkIt logo
│   └── icons/                # UI icons
├── Dockerfile                # Docker configuration
├── nginx.conf                # Nginx configuration
└── README.md                 # Frontend documentation
```

## Components and Interfaces

### 1. Authentication Manager (auth.js)

**Purpose**: Mengelola API key authentication dan session management

**Key Functions**:
```javascript
class AuthManager {
  // Check if user is authenticated
  isAuthenticated() -> boolean
  
  // Save API key to localStorage
  login(apiKey) -> void
  
  // Remove API key from localStorage
  logout() -> void
  
  // Get stored API key
  getApiKey() -> string | null
  
  // Validate API key with backend
  async validateApiKey(apiKey) -> Promise<boolean>
}
```

**Storage**:
- LocalStorage key: `parkit_admin_api_key`

### 2. API Client (api.js)

**Purpose**: Wrapper untuk semua HTTP requests ke backend dengan automatic API key injection

**Key Functions**:
```javascript
class ApiClient {
  constructor(baseUrl, authManager)
  
  // Generic request method
  async request(endpoint, options) -> Promise<Response>
  
  // Admin endpoints
  async getStats() -> Promise<Object>
  async getCalibrations() -> Promise<Array>
  async getCalibration(cameraId) -> Promise<Object>
  async createCalibration(data) -> Promise<Object>
  async updateCalibration(cameraId, data) -> Promise<Object>
  async deleteCalibration(cameraId) -> Promise<Object>
  async getSessions(params) -> Promise<Object>
  async deleteSession(sessionId) -> Promise<Object>
  async getUsers(params) -> Promise<Object>
  async toggleUserActive(username) -> Promise<Object>
  
  // Frame upload endpoints
  async uploadFrame(file, sessionId, cameraId) -> Promise<Object>
  async completeSession(sessionId) -> Promise<Object>
  
  // Results endpoints (public)
  async getLiveResults() -> Promise<Object>
  async getResult(sessionId) -> Promise<Object>
  async getLatestResults(limit, skip) -> Promise<Object>
}
```

**Error Handling**:
- Automatic retry untuk network errors (max 3 attempts)
- 401 Unauthorized → trigger logout dan redirect ke login
- 403 Forbidden → show error notification
- 500 Server Error → show error notification dengan detail
- Network timeout → 30 seconds

### 3. Router (router.js)

**Purpose**: Client-side routing untuk SPA navigation tanpa page reload

**Key Functions**:
```javascript
class Router {
  constructor()
  
  // Register route handler
  addRoute(path, handler) -> void
  
  // Navigate to route
  navigate(path) -> void
  
  // Get current route
  getCurrentRoute() -> string
  
  // Initialize router with history API
  init() -> void
}
```

**Routes**:
- `/` → Dashboard page
- `/upload` → Frame upload page
- `/calibration` → Calibration management page
- `/results` → Results monitoring page
- `/sessions` → Session management page
- `/users` → User management page
- `/login` → Login page (if not authenticated)

### 4. UI Manager (ui.js)

**Purpose**: Utilities untuk UI updates, notifications, dan loading states

**Key Functions**:
```javascript
class UIManager {
  // Show toast notification
  showNotification(message, type) -> void
  // type: 'success' | 'error' | 'warning' | 'info'
  
  // Show/hide loading spinner
  showLoading(target) -> void
  hideLoading(target) -> void
  
  // Show confirmation dialog
  async showConfirm(message) -> Promise<boolean>
  
  // Update page title
  setPageTitle(title) -> void
  
  // Render table with data
  renderTable(container, data, columns) -> void
  
  // Render pagination
  renderPagination(container, currentPage, totalPages, onPageChange) -> void
  
  // Format date/time
  formatDateTime(timestamp) -> string
  
  // Format number with separators
  formatNumber(number) -> string
}
```

**Notification System**:
- Toast notifications di top-right corner
- Auto-dismiss setelah 5 detik
- Support untuk success, error, warning, info types
- Stack multiple notifications

### 5. Page Components

#### Dashboard Page (dashboard.js)

**Purpose**: Menampilkan statistik sistem dan overview

**UI Elements**:
- Stats cards: Total Users, Total Sessions, Active Sessions, Completed Sessions, Total Detections
- Recent sessions table (last 10)
- Quick actions buttons
- Last update timestamp

**Data Flow**:
```
Load Page → API.getStats() → Render Stats Cards
         → API.getSessions({limit: 10}) → Render Recent Table
         → Auto-refresh every 30 seconds
```

#### Upload Page (upload.js)

**Purpose**: Upload multiple frames untuk detection session

**UI Elements**:
- Session ID input (auto-generate UUID option)
- Camera ID input (optional)
- File input (multiple, accept: image/*)
- Preview thumbnails grid
- Upload progress bars per file
- Complete session button

**Data Flow**:
```
Select Files → Show Previews
            → Click Upload → For each file:
                            → API.uploadFrame(file, sessionId, cameraId)
                            → Update progress bar
            → All uploaded → Enable "Complete Session" button
            → Click Complete → API.completeSession(sessionId)
                            → Navigate to results page
```

**Validation**:
- Session ID required (UUID format)
- At least 1 file selected
- File size max 10MB per file
- File type: jpg, jpeg, png only

#### Calibration Page (calibration.js)

**Purpose**: Manage camera calibrations

**UI Elements**:
- Calibration list table
- Create/Edit calibration form
- Row configuration builder (dynamic add/remove rows)
- Visual helper untuk perspective calculation
- Delete confirmation modal

**Form Fields**:
- Camera ID (text, required)
- Rows (array):
  - Row Index (number, auto-increment)
  - Y Coordinate (number, required)
  - Label (text, optional)
- Min Space Width (number, 10-500, required)
- Space Coefficient (number, 0.1-1.0, required)
- Row Start X (number, default: 0)
- Row End X (number, default: 1920)

**Data Flow**:
```
Load Page → API.getCalibrations() → Render Table
Create → Fill Form → Validate → API.createCalibration(data) → Refresh Table
Edit → Load Data → Fill Form → Validate → API.updateCalibration(id, data) → Refresh Table
Delete → Confirm → API.deleteCalibration(id) → Refresh Table
```

**Validation**:
- Camera ID unique check
- Y coordinates ascending order
- Min space width range: 10-500
- Space coefficient range: 0.1-1.0
- At least 1 row required, max 10 rows

#### Results Page (results.js)

**Purpose**: Monitor detection results real-time dan history

**UI Elements**:
- Live detection section:
  - Result image dengan bounding boxes
  - Stats: Total Motorcycles, Empty Spaces, Occupancy Rate
  - Empty spaces per row breakdown
  - Auto-refresh toggle
- History table:
  - Session ID, Camera ID, Timestamp, Detection Count, Status
  - View detail button per row
- Detail modal:
  - Full result image
  - Complete detection data
  - Empty spaces list

**Data Flow**:
```
Load Page → API.getLiveResults() → Render Live Section
         → API.getLatestResults() → Render History Table
         → Auto-refresh every 5 seconds (if enabled)
Click Detail → API.getResult(sessionId) → Show Modal
```

#### Sessions Page (sessions.js)

**Purpose**: Manage detection sessions

**UI Elements**:
- Filter dropdown (All, Active, Completed)
- Sessions table with pagination
- Delete button per row
- Pagination controls

**Data Flow**:
```
Load Page → API.getSessions({limit: 20, skip: 0, status: 'all'}) → Render Table
Filter Change → API.getSessions({status: filter}) → Render Table
Page Change → API.getSessions({skip: page * limit}) → Render Table
Delete → Confirm → API.deleteSession(sessionId) → Refresh Table
```

#### Users Page (users.js)

**Purpose**: Manage system users

**UI Elements**:
- Search box (username/email)
- Users table with pagination
- Active/Inactive toggle per row
- Pagination controls

**Data Flow**:
```
Load Page → API.getUsers({limit: 20, skip: 0}) → Render Table
Search → Filter table client-side
Toggle Active → API.toggleUserActive(username) → Update row
Page Change → API.getUsers({skip: page * limit}) → Render Table
```

## Data Models

### Frontend State Models

#### AuthState
```javascript
{
  isAuthenticated: boolean,
  apiKey: string | null
}
```

#### CalibrationData
```javascript
{
  camera_id: string,
  rows: [
    {
      row_index: number,
      y_coordinate: number,
      label: string
    }
  ],
  min_space_width: number,
  space_coefficient: number,
  row_start_x: number,
  row_end_x: number
}
```

#### UploadState
```javascript
{
  sessionId: string,
  cameraId: string | null,
  files: File[],
  uploadProgress: {
    [filename]: {
      progress: number,  // 0-100
      status: 'pending' | 'uploading' | 'completed' | 'failed',
      error: string | null
    }
  },
  isCompleted: boolean
}
```

#### DetectionResult
```javascript
{
  session_id: string,
  camera_id: string | null,
  status: 'active' | 'completed',
  max_detection_count: number,
  best_frame: {
    frame_id: string,
    timestamp: string,
    detections: Array,
    detection_count: number,
    empty_spaces: Array | null,
    total_motorcycles: number | null,
    total_empty_spaces: number | null,
    empty_spaces_per_row: Object | null,
    parking_occupancy_rate: number | null
  },
  total_frames: number
}
```

## Error Handling

### Error Types dan Handling Strategy

1. **Authentication Errors (401)**
   - Clear localStorage
   - Redirect to login page
   - Show notification: "Session expired. Please login again."

2. **Authorization Errors (403)**
   - Show notification: "You don't have permission to perform this action."
   - Stay on current page

3. **Validation Errors (400)**
   - Show notification dengan detail error dari backend
   - Highlight invalid form fields
   - Stay on current page

4. **Not Found Errors (404)**
   - Show notification: "Resource not found."
   - Redirect to appropriate page

5. **Server Errors (500)**
   - Show notification: "Server error. Please try again later."
   - Log error to console
   - Stay on current page

6. **Network Errors**
   - Retry request (max 3 attempts dengan exponential backoff)
   - Show notification: "Connection failed. Please check your internet."
   - Log error to console

7. **Timeout Errors**
   - Show notification: "Request timeout. Please try again."
   - Cancel pending request
   - Stay on current page

### Error Logging

```javascript
class ErrorLogger {
  log(error, context) {
    console.error('[ParkIt Admin]', {
      timestamp: new Date().toISOString(),
      error: error.message,
      stack: error.stack,
      context: context
    });
  }
}
```

## Testing Strategy

### Manual Testing Checklist

1. **Authentication Flow**
   - [ ] Login dengan valid API key
   - [ ] Login dengan invalid API key
   - [ ] Logout functionality
   - [ ] Auto-logout pada 401 error
   - [ ] API key persistence di localStorage

2. **Frame Upload**
   - [ ] Upload single file
   - [ ] Upload multiple files
   - [ ] Preview thumbnails
   - [ ] Progress tracking
   - [ ] Complete session
   - [ ] Error handling untuk failed uploads
   - [ ] File validation (type, size)

3. **Calibration Management**
   - [ ] Create new calibration
   - [ ] View calibration list
   - [ ] Edit existing calibration
   - [ ] Delete calibration
   - [ ] Form validation
   - [ ] Dynamic row add/remove

4. **Results Monitoring**
   - [ ] View live detection
   - [ ] Auto-refresh functionality
   - [ ] View history table
   - [ ] View detail modal
   - [ ] Image loading
   - [ ] Empty spaces visualization

5. **Session Management**
   - [ ] View sessions list
   - [ ] Filter by status
   - [ ] Pagination
   - [ ] Delete session
   - [ ] Confirmation dialog

6. **User Management**
   - [ ] View users list
   - [ ] Search functionality
   - [ ] Toggle active status
   - [ ] Pagination

7. **Navigation**
   - [ ] Sidebar navigation
   - [ ] Active menu highlight
   - [ ] Mobile responsive menu
   - [ ] Browser back/forward buttons

8. **Error Handling**
   - [ ] Network error notification
   - [ ] Validation error display
   - [ ] Server error notification
   - [ ] Timeout handling

9. **Responsive Design**
   - [ ] Desktop view (1920x1080)
   - [ ] Tablet view (768x1024)
   - [ ] Mobile view (375x667)
   - [ ] Hamburger menu on mobile

### Browser Compatibility Testing

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

### Performance Testing

- Page load time < 2 seconds
- API response handling < 500ms
- Image loading optimization
- Smooth animations (60fps)

## Docker Deployment

### Dockerfile Design

```dockerfile
# Multi-stage build untuk optimasi
FROM nginx:alpine

# Copy static files
COPY index.html /usr/share/nginx/html/
COPY css/ /usr/share/nginx/html/css/
COPY js/ /usr/share/nginx/html/js/
COPY assets/ /usr/share/nginx/html/assets/

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # SPA routing - redirect all to index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

### Docker Compose Integration

```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - BACKEND_API_URL=http://backend:8000
    depends_on:
      - backend
    networks:
      - parkit-network

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    networks:
      - parkit-network

networks:
  parkit-network:
    driver: bridge
```

### Environment Configuration

Frontend akan menggunakan environment variable untuk backend URL:

```javascript
// config.js
const CONFIG = {
  API_BASE_URL: window.ENV?.BACKEND_API_URL || 'http://localhost:8000',
  API_TIMEOUT: 30000,
  AUTO_REFRESH_INTERVAL: 5000,
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_FILE_TYPES: ['image/jpeg', 'image/jpg', 'image/png']
};
```

## Security Considerations

1. **API Key Storage**
   - Store di localStorage (client-side only)
   - Never log API key to console
   - Clear on logout

2. **XSS Prevention**
   - Sanitize user inputs
   - Use textContent instead of innerHTML untuk user data
   - Validate all form inputs

3. **CSRF Protection**
   - Backend handles CSRF tokens
   - Frontend sends API key di header (bukan cookie)

4. **Content Security Policy**
   - Restrict script sources
   - Prevent inline scripts jika memungkinkan

5. **HTTPS**
   - Production deployment harus menggunakan HTTPS
   - Nginx configuration untuk SSL/TLS

## Performance Optimization

1. **Code Splitting**
   - Load page modules on-demand
   - Lazy load images

2. **Caching Strategy**
   - Cache static assets (1 year)
   - Cache API responses (short-lived, 5 seconds)
   - Use ETag untuk conditional requests

3. **Image Optimization**
   - Compress uploaded images sebelum display
   - Use thumbnail untuk preview
   - Lazy load images di tables

4. **Minification**
   - Minify CSS dan JavaScript untuk production
   - Use build script untuk optimization

5. **Network Optimization**
   - Batch API requests jika memungkinkan
   - Use pagination untuk large datasets
   - Implement request debouncing untuk search

## Accessibility

1. **Keyboard Navigation**
   - All interactive elements accessible via keyboard
   - Logical tab order
   - Focus indicators visible

2. **Screen Reader Support**
   - Semantic HTML elements
   - ARIA labels untuk custom components
   - Alt text untuk images

3. **Color Contrast**
   - WCAG AA compliance
   - Sufficient contrast ratios
   - Don't rely on color alone untuk information

4. **Responsive Text**
   - Scalable font sizes
   - Readable line heights
   - Support browser zoom

## Future Enhancements

1. **Real-time Updates**
   - WebSocket connection untuk live updates
   - Push notifications untuk new detections

2. **Advanced Analytics**
   - Charts dan graphs untuk statistics
   - Historical trends analysis
   - Export data to CSV/PDF

3. **Multi-language Support**
   - i18n implementation
   - Language switcher

4. **Dark Mode**
   - Theme toggle
   - Persist preference

5. **Offline Support**
   - Service Worker untuk offline functionality
   - Cache API responses
   - Queue uploads untuk retry
