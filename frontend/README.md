# ParkIt Admin Dashboard Frontend

Admin dashboard frontend untuk sistem deteksi parkir motor ParkIt. Aplikasi web berbasis HTML, CSS, dan JavaScript vanilla yang menyediakan interface untuk mengelola sistem deteksi parkir.

## Features

- ✅ **Authentication** - Login dengan API key
- ✅ **Dashboard** - Statistik sistem dan overview
- ✅ **Frame Upload** - Upload multiple frames dari CCTV
- ✅ **Calibration Management** - Konfigurasi kamera untuk deteksi ruang kosong
- ✅ **Results Monitoring** - Live detection dan history
- ✅ **Session Management** - Kelola detection sessions
- ✅ **User Management** - Kelola system users
- ✅ **Responsive Design** - Mobile-friendly interface
- ✅ **Docker Support** - Easy deployment dengan Docker

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Web Server**: Nginx
- **Containerization**: Docker
- **API Communication**: Fetch API
- **State Management**: LocalStorage

## Project Structure

```
frontend/
├── index.html              # Main HTML file (SPA shell)
├── css/
│   ├── main.css           # Global styles dan CSS variables
│   ├── components.css     # Reusable component styles
│   └── responsive.css     # Media queries untuk responsive design
├── js/
│   ├── config.js          # Configuration constants
│   ├── auth.js            # Authentication manager
│   ├── api.js             # API client wrapper
│   ├── router.js          # Client-side routing
│   ├── ui.js              # UI utilities dan notifications
│   ├── app.js             # Main application entry point
│   └── pages/
│       ├── dashboard.js   # Dashboard page
│       ├── upload.js      # Frame upload page
│       ├── calibration.js # Calibration management
│       ├── results.js     # Results monitoring
│       ├── sessions.js    # Session management
│       └── users.js       # User management
├── assets/                # Images dan icons (optional)
├── Dockerfile             # Docker configuration
├── nginx.conf             # Nginx configuration
└── README.md              # This file
```

## Setup

### Prerequisites

- Modern web browser (Chrome, Firefox, Safari, Edge)
- Backend API running (default: http://localhost:8000)
- API key untuk authentication

### Local Development

1. **Clone repository**

```bash
git clone <repository-url>
cd frontend
```

2. **Configure backend URL**

Edit `js/config.js` dan sesuaikan `API_BASE_URL`:

```javascript
const CONFIG = {
  API_BASE_URL: 'http://localhost:8000',
  // ... other config
};
```

3. **Serve dengan web server**

Gunakan web server sederhana untuk serve static files:

**Python:**
```bash
python -m http.server 8080
```

**Node.js (http-server):**
```bash
npx http-server -p 8080
```

**PHP:**
```bash
php -S localhost:8080
```

4. **Open browser**

```
http://localhost:8080
```

5. **Login**

Gunakan API key default:
```
parkit-admin-secret-key-change-this
```

⚠️ **Important:** Ganti API key default di production!

### Docker Deployment

#### Build Docker Image

```bash
docker build -t parkit-frontend .
```

#### Run Container

```bash
docker run -d -p 3000:80 --name parkit-frontend parkit-frontend
```

Access dashboard di: `http://localhost:3000`

#### Docker Compose

Untuk deploy frontend dan backend bersamaan:

```bash
# From project root
docker-compose up -d
```

Services:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

#### Stop Container

```bash
docker stop parkit-frontend
docker rm parkit-frontend
```

## Configuration

### Environment Variables

Frontend menggunakan environment variables untuk konfigurasi:

```javascript
// js/config.js
const CONFIG = {
  // API Configuration
  API_BASE_URL: window.ENV?.BACKEND_API_URL || 'http://localhost:8000',
  API_TIMEOUT: 30000, // 30 seconds
  
  // Auto-refresh intervals
  AUTO_REFRESH_INTERVAL: 5000, // 5 seconds
  STATS_REFRESH_INTERVAL: 30000, // 30 seconds
  
  // File upload constraints
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_FILE_TYPES: ['image/jpeg', 'image/jpg', 'image/png'],
  
  // Pagination
  DEFAULT_PAGE_SIZE: 20,
  
  // LocalStorage keys
  STORAGE_KEY_API_KEY: 'parkit_admin_api_key',
  
  // Retry configuration
  MAX_RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
  
  // Notification duration
  NOTIFICATION_DURATION: 5000
};
```

### Nginx Configuration

Edit `nginx.conf` untuk custom configuration:

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # SPA routing
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
    gzip_types text/plain text/css application/json application/javascript;
}
```

## Usage

### Login

1. Open dashboard di browser
2. Enter API key
3. Click "Login"

### Dashboard

- View system statistics
- Monitor recent sessions
- Quick access to features

### Upload Frames

1. Navigate to "Upload Frames"
2. Generate atau enter session ID
3. (Optional) Enter camera ID untuk calibration
4. Select image files (JPG, PNG)
5. Click "Upload Frames"
6. Wait untuk upload completion
7. Click "Complete Session"

### Calibration

1. Navigate to "Calibration"
2. Click "New Calibration"
3. Enter camera ID
4. Add parking rows dengan Y coordinates
5. Set min space width dan space coefficient
6. Click "Save Calibration"

### Results

1. Navigate to "Results"
2. View live detection dengan auto-refresh
3. Browse history table
4. Click "View" untuk detail results

### Sessions

1. Navigate to "Sessions"
2. Filter by status (all, active, completed)
3. Use pagination untuk browse
4. Delete sessions jika diperlukan

### Users

1. Navigate to "Users"
2. Search by username atau email
3. Toggle user active/inactive status
4. View user details

## Browser Compatibility

Tested dan supported di:

- ✅ Chrome (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Edge (latest)

## Responsive Design

Dashboard fully responsive dengan breakpoints:

- **Desktop**: > 1024px
- **Tablet**: 768px - 1024px
- **Mobile**: < 768px

Mobile features:
- Hamburger menu
- Collapsible sidebar
- Touch-friendly buttons
- Optimized layouts

## API Documentation

Untuk detail API endpoints, lihat:

- [Client API Documentation](../CLIENT_API_DOCUMENTATION.md) - Public endpoints
- [Admin API Documentation](../ADMIN_API_DOCUMENTATION.md) - Admin endpoints

## Security

### Best Practices

1. **Change Default API Key**: Selalu ganti default API key di production
2. **Use HTTPS**: Deploy dengan HTTPS di production
3. **Secure Storage**: API key disimpan di localStorage (client-side only)
4. **Input Validation**: Semua input divalidasi sebelum submit
5. **XSS Prevention**: Menggunakan textContent untuk user data
6. **CORS**: Configure CORS di backend untuk production

### Security Headers

Nginx configuration includes security headers:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

## Performance

### Optimization

- **Gzip Compression**: Enabled untuk text files
- **Cache Headers**: Static assets cached untuk 1 year
- **Lazy Loading**: Images loaded on-demand
- **Pagination**: Large datasets paginated
- **Auto-refresh**: Configurable intervals

### Metrics

- Page load time: < 2 seconds
- API response handling: < 500ms
- Smooth animations: 60fps

## Troubleshooting

### Cannot Connect to Backend

**Problem**: "Connection failed. Please check your internet connection"

**Solution**:
1. Check backend is running: `http://localhost:8000`
2. Verify `API_BASE_URL` di `config.js`
3. Check CORS settings di backend
4. Check network tab di browser DevTools

### Invalid API Key

**Problem**: "Invalid API key"

**Solution**:
1. Verify API key di backend configuration
2. Check header `X-API-Key` di network requests
3. Try default key: `parkit-admin-secret-key-change-this`

### Images Not Loading

**Problem**: Result images tidak muncul

**Solution**:
1. Check backend uploads directory exists
2. Verify image URL di network tab
3. Check CORS headers untuk image requests
4. Verify session has completed

### Mobile Menu Not Working

**Problem**: Hamburger menu tidak toggle

**Solution**:
1. Check JavaScript console untuk errors
2. Verify `app.js` loaded correctly
3. Clear browser cache
4. Try different browser

## Development

### Adding New Pages

1. Create page component di `js/pages/`:

```javascript
// js/pages/mypage.js
const MyPage = {
  async render() {
    const container = document.getElementById('page-container');
    container.innerHTML = `<h1>My Page</h1>`;
  },
  
  cleanup() {
    // Cleanup logic
  }
};
```

2. Register route di `app.js`:

```javascript
router.addRoute('/mypage', () => this.showPage(MyPage));
```

3. Add navigation item di `index.html`:

```html
<a href="#/mypage" class="nav-item" data-route="/mypage">
  <span class="nav-icon">📄</span>
  <span class="nav-text">My Page</span>
</a>
```

### Adding API Methods

Add methods di `api.js`:

```javascript
async myApiMethod(params) {
  const response = await this.request('/api/my-endpoint', {
    method: 'POST',
    body: JSON.stringify(params)
  });
  return response.json();
}
```

### Styling

Edit CSS files:

- `main.css`: Global styles dan variables
- `components.css`: Reusable components
- `responsive.css`: Media queries

Use CSS variables untuk consistency:

```css
color: var(--primary-color);
padding: var(--spacing-md);
font-size: var(--font-size-base);
```

## Contributing

1. Fork repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## License

MIT

## Support

Untuk issues atau questions:
- Check documentation
- Review API documentation
- Check browser console untuk errors
- Contact system administrator

## Changelog

### Version 1.0.0 (2024-01-15)

- ✅ Initial release
- ✅ Authentication system
- ✅ Dashboard dengan statistics
- ✅ Frame upload dengan progress tracking
- ✅ Calibration management
- ✅ Results monitoring dengan live detection
- ✅ Session management
- ✅ User management
- ✅ Responsive design
- ✅ Docker support
- ✅ Complete API documentation
