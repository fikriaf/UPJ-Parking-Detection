# Deployment Guide - Parkit Smart Parking Detection System

Panduan deployment sistem Parkit di PC lokal ruang B506 menggunakan Docker WSL2 dan Ngrok.

## Daftar Isi

- [Arsitektur Sistem](#arsitektur-sistem)
- [Prasyarat](#prasyarat)
- [Setup Environment](#setup-environment)
- [Deployment Backend](#deployment-backend)
- [Deployment Frontend](#deployment-frontend)
- [Setup Ngrok](#setup-ngrok)
- [Konfigurasi](#konfigurasi)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

---

## Arsitektur Sistem

### Deployment Architecture
[Deployment Architecture](/docs/Deployment%20Architecture.png)

**Penjelasan Diagram:** Diagram ini menggambarkan arsitektur deployment sistem Parkit yang berjalan di PC lokal ruang B506 menggunakan Docker WSL2. Sistem terdiri dari tiga container Docker utama: Backend API (FastAPI) pada port 8000 yang menangani deteksi motor menggunakan YOLOv8, Admin Dashboard pada port 3000 untuk manajemen sistem, dan Client Frontend pada port 8080 untuk tampilan publik. Backend terhubung dengan MongoDB Atlas sebagai cloud database untuk menyimpan data session dan hasil deteksi, serta mengakses local storage untuk menyimpan file uploads, results, calibration data, dan model YOLO. Ketiga service ini di-expose ke internet melalui Ngrok tunnels yang menyediakan HTTPS proxy, memungkinkan akses dari admin user dan public user melalui browser dari mana saja via internet.

### System Components Diagram
[System Components Diagram](/docs/System%20Components%20Diagram.png)

**Penjelasan Diagram:** Diagram komponen sistem ini menunjukkan arsitektur berlapis (layered architecture) dari aplikasi Parkit. Layer paling atas adalah Frontend Layer yang terdiri dari Admin Dashboard dan Client Frontend yang berkomunikasi dengan API Layer melalui REST API. API Layer menggunakan FastAPI dengan tiga router utama: Upload Router untuk menangani upload frame, Results Router untuk menampilkan hasil deteksi, dan Calibration Router untuk konfigurasi kamera. Router-router ini memanggil Service Layer yang berisi business logic (Detection Service, Calibration Service, Session Service), yang kemudian menggunakan Processing Engine untuk melakukan deteksi objek dengan YOLOv8, pemrosesan gambar, dan kalkulasi ruang parkir kosong. Semua data disimpan di Data Layer yang terdiri dari MongoDB Atlas untuk data terstruktur dan File Storage lokal untuk menyimpan file gambar dan model. Seluruh sistem dapat diakses dari internet melalui Ngrok tunnels.

### Data Flow Diagram
[Data Flow Diagram](/docs/Data%20Flow%20Diagram.png)

**Penjelasan Diagram:** Diagram alur data ini mengilustrasikan empat proses utama dalam sistem Parkit. Pertama, proses Upload Frames dimana admin memilih gambar dari kamera dan mengirimkannya ke backend melalui Admin UI, backend menyimpan frame ke file storage dan membuat session baru di MongoDB. Kedua, proses Complete Session dimana admin memicu pemrosesan deteksi, backend memuat frame dari storage, menjalankan YOLO inference untuk mendeteksi motor, mengambil konfigurasi kalibrasi dari database, menghitung ruang parkir kosong menggunakan Calibration Engine, menyimpan gambar hasil anotasi, dan menyimpan hasil deteksi ke MongoDB. Ketiga, proses View Results dimana admin dapat melihat hasil deteksi terbaru melalui Admin UI dengan mengambil data dari database dan menampilkan gambar hasil anotasi. Keempat, proses Public View dimana pengguna umum dapat melihat status parkir real-time melalui Client UI tanpa perlu autentikasi, dengan data yang diambil dari session aktif di database.

### Komponen Sistem

1. **Backend API** (FastAPI)
   - Port: 8000
   - Deteksi motor dengan YOLOv8
   - Kalkulasi ruang parkir kosong
   - REST API untuk frontend

2. **Admin Dashboard Frontend**
   - Port: 3000
   - Upload frames dari kamera
   - Kalibrasi kamera
   - Monitoring hasil deteksi
   - Management session

3. **Client Frontend** (Public)
   - Port: 8080
   - View hasil deteksi real-time
   - Tidak perlu authentication
   - Interface untuk end-user

4. **MongoDB Atlas**
   - Cloud database
   - Menyimpan session data
   - Menyimpan hasil deteksi

5. **Ngrok**
   - Expose local server ke internet
   - HTTPS tunnel
   - Public URL access

---

## Prasyarat

### Software yang Dibutuhkan

- [x] Windows 10/11
- [x] WSL2 (Windows Subsystem for Linux)
- [x] Docker Desktop for Windows
- [x] Git
- [x] Ngrok account (free tier)
- [x] MongoDB Atlas account (free tier)

### Hardware Minimum

- CPU: 4 cores
- RAM: 8 GB
- Storage: 20 GB free space
- Network: Koneksi internet stabil

---

## Setup Environment

### 1. Install WSL2

```powershell
# Buka PowerShell sebagai Administrator
wsl --install

# Restart komputer
# Setelah restart, set WSL2 sebagai default
wsl --set-default-version 2

# Install Ubuntu
wsl --install -d Ubuntu-22.04
```

### 2. Install Docker Desktop

1. Download Docker Desktop dari https://www.docker.com/products/docker-desktop
2. Install dan restart komputer
3. Buka Docker Desktop
4. Settings → General → Enable "Use WSL 2 based engine"
5. Settings → Resources → WSL Integration → Enable Ubuntu-22.04

### 3. Verify Installation

```bash
# Buka WSL terminal
wsl

# Check Docker
docker --version
docker-compose --version

# Test Docker
docker run hello-world
```

### 4. Clone Repository

```bash
# Di WSL terminal
cd ~
git clone <repository-url> parkit
cd parkit
```

---

## Deployment Backend

### 1. Setup MongoDB Atlas

1. **Buat Account**
   - Kunjungi https://www.mongodb.com/cloud/atlas
   - Sign up (gratis)

2. **Buat Cluster**
   - Create New Cluster
   - Pilih Free Tier (M0)
   - Region: Singapore (terdekat)
   - Cluster Name: parkit-cluster

3. **Setup Database Access**
   - Database Access → Add New Database User
   - Username: `parkit_user`
   - Password: (generate strong password)
   - Role: Read and write to any database

4. **Setup Network Access**
   - Network Access → Add IP Address
   - Allow Access from Anywhere: `0.0.0.0/0`
   - (Untuk development, production gunakan IP spesifik)

5. **Get Connection String**
   - Clusters → Connect → Connect your application
   - Copy connection string
   - Format: `mongodb+srv://parkit_user:<password>@cluster.mongodb.net/`

### 2. Konfigurasi Backend

```bash
cd ~/parkit/backend

# Copy .env example (jika ada) atau buat baru
nano .env
```

Isi file `.env`:

```env
# MongoDB Atlas
MONGODB_URL=mongodb+srv://parkit_user:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=parkit_db

# Model Configuration
MODEL_PATH=models/best.pt
CONFIDENCE_THRESHOLD=0.25
IOU_THRESHOLD=0.45
MAX_DETECTIONS=300

# Admin API Key (ganti dengan key yang kuat)
ADMIN_API_KEY=parkit-admin-B506-secret-key-2025

# Frame Processing
MAX_FRAMES_PER_SESSION=10
FRAME_COMPARISON_WINDOW=5

# Calibration
DEFAULT_MIN_SPACE_WIDTH=150
DEFAULT_SPACE_COEFFICIENT=0.8
MAX_PARKING_ROWS=10
```

### 3. Pastikan Model YOLO Ada

```bash
# Check model file
ls -lh ~/parkit/backend/models/best.pt

# Jika tidak ada, copy dari training results atau download
```

### 4. Build dan Run Backend dengan Docker

```bash
cd ~/parkit/backend

# Build Docker image
docker build -t parkit-backend .

# Run container
docker run -d \
  --name parkit-backend \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/results:/app/results \
  -v $(pwd)/calibration:/app/calibration \
  -v $(pwd)/models:/app/models \
  --restart unless-stopped \
  parkit-backend

# Check logs
docker logs -f parkit-backend

# Test backend
curl http://localhost:8000/health
```

**Atau menggunakan Docker Compose:**

```bash
cd ~/parkit/backend

# Start backend
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop backend
docker-compose down
```

---

## Deployment Frontend

### 1. Admin Dashboard Frontend

```bash
cd ~/parkit/frontend

# Build Docker image
docker build -t parkit-admin-frontend .

# Run container
docker run -d \
  --name parkit-admin-frontend \
  -p 3000:80 \
  -e BACKEND_API_URL=http://localhost:8000 \
  --restart unless-stopped \
  parkit-admin-frontend

# Check logs
docker logs parkit-admin-frontend

# Test frontend
# Buka browser: http://localhost:3000
```

**Atau tanpa Docker (development):**

```bash
cd ~/parkit/frontend

# Serve dengan Python
python3 -m http.server 3000

# Atau dengan Node.js
npx http-server -p 3000
```

### 2. Client Frontend (Public)

Jika Anda memiliki folder terpisah untuk client frontend:

```bash
cd ~/parkit/client-frontend  # atau folder client Anda

# Serve dengan Python
python3 -m http.server 8080

# Atau dengan Docker
docker build -t parkit-client-frontend .
docker run -d \
  --name parkit-client-frontend \
  -p 8080:80 \
  --restart unless-stopped \
  parkit-client-frontend
```

**Jika client frontend belum ada**, buat folder sederhana:

```bash
mkdir -p ~/parkit/client
cd ~/parkit/client

# Buat index.html sederhana
cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Parkit - Status Parkir</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        .status-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        .result-image {
            max-width: 100%;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <h1>Status Parkir Motor UPJ</h1>
    <div id="status"></div>
    <script>
        const API_URL = 'http://localhost:8000';
        
        async function loadStatus() {
            try {
                const response = await fetch(`${API_URL}/api/results/live`);
                const data = await response.json();
                
                document.getElementById('status').innerHTML = `
                    <div class="status-card">
                        <h2>Deteksi Terbaru</h2>
                        <p>Motor Terdeteksi: ${data.max_detection_count || 0}</p>
                        <p>Ruang Kosong: ${data.best_frame?.empty_spaces?.length || 0}</p>
                        <p>Tingkat Okupansi: ${data.occupancy_rate || 0}%</p>
                        ${data.best_frame?.annotated_image_url ? 
                          `<img src="${API_URL}${data.best_frame.annotated_image_url}" class="result-image">` : 
                          '<p>Tidak ada gambar</p>'}
                    </div>
                `;
            } catch (error) {
                document.getElementById('status').innerHTML = 
                    '<p>Tidak dapat memuat data. Pastikan backend berjalan.</p>';
            }
        }
        
        loadStatus();
        setInterval(loadStatus, 5000); // Refresh setiap 5 detik
    </script>
</body>
</html>
EOF

# Serve
python3 -m http.server 8080
```

---

## Setup Ngrok

### 1. Install Ngrok

```bash
# Download Ngrok
cd ~
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz

# Extract
tar -xvzf ngrok-v3-stable-linux-amd64.tgz

# Move to /usr/local/bin
sudo mv ngrok /usr/local/bin/

# Verify
ngrok version
```

### 2. Setup Ngrok Account

1. Kunjungi https://ngrok.com/
2. Sign up (gratis)
3. Dashboard → Your Authtoken
4. Copy authtoken

```bash
# Authenticate
ngrok config add-authtoken <your-authtoken>
```

### 3. Expose Backend ke Internet

```bash
# Expose port 8000 (backend)
ngrok http 8000

# Output akan menampilkan:
# Forwarding: https://xxxx-xxx-xxx-xxx.ngrok-free.app -> http://localhost:8000
```

**Simpan URL ngrok** (contoh: `https://abc123.ngrok-free.app`)

### 4. Expose Admin Frontend

```bash
# Terminal baru
ngrok http 3000

# Simpan URL untuk admin dashboard
```

### 5. Expose Client Frontend

```bash
# Terminal baru
ngrok http 8080

# Simpan URL untuk client public
```

### 6. Ngrok dengan Custom Domain (Optional - Paid)

Jika Anda memiliki ngrok paid plan:

```bash
# Backend
ngrok http 8000 --domain=parkit-api.ngrok.app

# Admin
ngrok http 3000 --domain=parkit-admin.ngrok.app

# Client
ngrok http 8080 --domain=parkit-client.ngrok.app
```

### 7. Ngrok Configuration File (Recommended)

Buat file `~/ngrok.yml`:

```yaml
version: "2"
authtoken: <your-authtoken>

tunnels:
  backend:
    proto: http
    addr: 8000
    inspect: true
  
  admin:
    proto: http
    addr: 3000
    inspect: true
  
  client:
    proto: http
    addr: 8080
    inspect: true
```

Start semua tunnels:

```bash
ngrok start --all --config ~/ngrok.yml
```

---

## Konfigurasi

### Update Frontend Configuration

Setelah mendapat URL ngrok, update konfigurasi frontend:

**Admin Frontend** (`frontend/js/config.js`):

```javascript
const CONFIG = {
  // Untuk akses lokal
  API_BASE_URL: 'http://localhost:8000',
  
  // Untuk akses dari luar (ganti dengan URL ngrok backend)
  // API_BASE_URL: 'https://abc123.ngrok-free.app',
  
  // ... config lainnya
};
```

**Client Frontend** (update di HTML atau config):

```javascript
const API_URL = 'https://abc123.ngrok-free.app'; // URL ngrok backend
```

### CORS Configuration

Update backend untuk allow ngrok URLs:

Edit `backend/main.py` atau `backend/app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "https://*.ngrok-free.app",  # Allow all ngrok URLs
        "https://*.ngrok.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Rebuild dan restart backend setelah perubahan.

---

## Testing

### 1. Test Backend

```bash
# Health check
curl http://localhost:8000/health

# Atau dengan ngrok URL
curl https://abc123.ngrok-free.app/health

# Expected response:
# {"status":"healthy"}
```

### 2. Test Admin Frontend

1. Buka browser: `http://localhost:3000` atau URL ngrok admin
2. Login dengan API key dari `.env`
3. Test upload frame
4. Test calibration
5. Test view results

### 3. Test Client Frontend

1. Buka browser: `http://localhost:8080` atau URL ngrok client
2. Verify data muncul
3. Test auto-refresh

### 4. Test dari Device Lain

Gunakan URL ngrok untuk akses dari HP atau komputer lain:

- Backend API: `https://abc123.ngrok-free.app`
- Admin Dashboard: `https://def456.ngrok-free.app`
- Client Public: `https://ghi789.ngrok-free.app`

---

## Troubleshooting

### Backend Tidak Start

```bash
# Check logs
docker logs parkit-backend

# Common issues:
# 1. MongoDB connection failed
#    - Verify MONGODB_URL di .env
#    - Check network access di MongoDB Atlas

# 2. Model file not found
ls -lh ~/parkit/backend/models/best.pt

# 3. Port already in use
sudo lsof -i :8000
# Kill process jika perlu
```

### Frontend Tidak Bisa Connect ke Backend

```bash
# 1. Check backend running
curl http://localhost:8000/health

# 2. Check CORS configuration
#    - Verify allow_origins di backend

# 3. Check API_BASE_URL di frontend config
#    - Pastikan URL benar

# 4. Check browser console untuk errors
#    - F12 → Console tab
```

### Ngrok Tunnel Mati

```bash
# Ngrok free tier: tunnel expires setelah 2 jam
# Restart ngrok:
ngrok http 8000

# Atau gunakan ngrok config file:
ngrok start --all --config ~/ngrok.yml

# Update URL baru di frontend jika berubah
```

### Docker Container Tidak Start

```bash
# Check Docker status
docker ps -a

# Check logs
docker logs parkit-backend

# Restart container
docker restart parkit-backend

# Rebuild jika perlu
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Upload Gagal

```bash
# 1. Check disk space
df -h

# 2. Check permissions
ls -la ~/parkit/backend/uploads/

# 3. Check file size limit
#    - Default: 50MB di Nginx
#    - Check backend logs untuk error

# 4. Check network
#    - Pastikan koneksi stabil
```

### Detection Lambat

```bash
# 1. Check CPU/Memory usage
htop

# 2. Reduce confidence threshold di .env
CONFIDENCE_THRESHOLD=0.3  # Increase dari 0.25

# 3. Reduce max detections
MAX_DETECTIONS=200  # Reduce dari 300

# 4. Check model file
#    - Pastikan best.pt ada dan valid
```

---

## Maintenance

### Daily Tasks

```bash
# 1. Check service status
docker ps

# 2. Check logs untuk errors
docker logs --tail 50 parkit-backend

# 3. Check disk space
df -h

# 4. Verify ngrok tunnels active
curl https://abc123.ngrok-free.app/health
```

### Weekly Tasks

```bash
# 1. Cleanup old uploads (older than 7 days)
find ~/parkit/backend/uploads -type f -mtime +7 -delete

# 2. Cleanup old results (older than 30 days)
find ~/parkit/backend/results -type f -mtime +30 -delete

# 3. Check Docker disk usage
docker system df

# 4. Cleanup unused Docker resources
docker system prune -f
```

### Backup

```bash
# Backup script
cat > ~/parkit/backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR=~/parkit-backups
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup uploads, results, calibration
tar -czf $BACKUP_DIR/parkit_data_$DATE.tar.gz \
    ~/parkit/backend/uploads \
    ~/parkit/backend/results \
    ~/parkit/backend/calibration

# Backup .env
cp ~/parkit/backend/.env $BACKUP_DIR/.env_$DATE

# Keep only last 7 backups
ls -t $BACKUP_DIR/parkit_data_*.tar.gz | tail -n +8 | xargs rm -f

echo "Backup completed: $DATE"
EOF

chmod +x ~/parkit/backup.sh

# Run backup
~/parkit/backup.sh

# Schedule dengan cron (optional)
crontab -e
# Add: 0 2 * * * ~/parkit/backup.sh
```

### Update Application

```bash
# 1. Backup current version
~/parkit/backup.sh

# 2. Pull latest code
cd ~/parkit
git pull origin main

# 3. Rebuild backend
cd backend
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 4. Rebuild frontend (jika ada perubahan)
cd ../frontend
docker build -t parkit-admin-frontend .
docker stop parkit-admin-frontend
docker rm parkit-admin-frontend
docker run -d --name parkit-admin-frontend -p 3000:80 parkit-admin-frontend

# 5. Verify
curl http://localhost:8000/health
```

### Restart Services

```bash
# Restart backend
docker restart parkit-backend

# Restart frontend
docker restart parkit-admin-frontend

# Restart all
docker restart parkit-backend parkit-admin-frontend

# Restart ngrok
# Kill existing ngrok processes
pkill ngrok

# Start again
ngrok start --all --config ~/ngrok.yml
```

### Monitor Resources

```bash
# CPU and Memory
htop

# Docker stats
docker stats

# Disk usage
du -sh ~/parkit/*

# Network
netstat -tulpn | grep -E '8000|3000|8080'
```

---

## Quick Reference

### Start All Services

```bash
# Backend
cd ~/parkit/backend
docker-compose up -d

# Admin Frontend
docker start parkit-admin-frontend
# Atau: cd ~/parkit/frontend && python3 -m http.server 3000

# Client Frontend
cd ~/parkit/client && python3 -m http.server 8080

# Ngrok
ngrok start --all --config ~/ngrok.yml
```

### Stop All Services

```bash
# Backend
docker-compose -f ~/parkit/backend/docker-compose.yml down

# Frontend
docker stop parkit-admin-frontend

# Kill Python servers
pkill -f "http.server"

# Stop ngrok
pkill ngrok
```

### View Logs

```bash
# Backend
docker logs -f parkit-backend

# Frontend
docker logs parkit-admin-frontend

# Ngrok
# Check ngrok web interface: http://localhost:4040
```

### Useful Commands

```bash
# Check what's running on ports
sudo lsof -i :8000  # Backend
sudo lsof -i :3000  # Admin
sudo lsof -i :8080  # Client

# Check Docker containers
docker ps -a

# Check Docker images
docker images

# Remove stopped containers
docker container prune

# Remove unused images
docker image prune -a

# Check WSL status
wsl --list --verbose

# Restart WSL (if needed)
wsl --shutdown
# Then open WSL again
```

---

## Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MONGODB_URL` | MongoDB Atlas connection string | - | Yes |
| `DATABASE_NAME` | Database name | parkit_db | Yes |
| `MODEL_PATH` | Path to YOLO model | models/best.pt | Yes |
| `ADMIN_API_KEY` | Admin API key untuk authentication | - | Yes |
| `CONFIDENCE_THRESHOLD` | Detection confidence threshold | 0.25 | No |
| `IOU_THRESHOLD` | IoU threshold | 0.45 | No |
| `MAX_DETECTIONS` | Max detections per frame | 300 | No |
| `MAX_FRAMES_PER_SESSION` | Max frames per session | 10 | No |
| `FRAME_COMPARISON_WINDOW` | Frame comparison window | 5 | No |
| `DEFAULT_MIN_SPACE_WIDTH` | Min parking space width (px) | 150 | No |
| `DEFAULT_SPACE_COEFFICIENT` | Space calculation coefficient | 0.8 | No |
| `MAX_PARKING_ROWS` | Max parking rows per camera | 10 | No |

---

## Port Reference

| Port | Service | Access |
|------|---------|--------|
| 8000 | Backend API | Local + Ngrok |
| 3000 | Admin Dashboard | Local + Ngrok |
| 8080 | Client Frontend | Local + Ngrok |
| 4040 | Ngrok Web Interface | Local only |

---

## URLs Reference

### Local Access (di PC B506)

- Backend API: `http://localhost:8000`
- Admin Dashboard: `http://localhost:3000`
- Client Frontend: `http://localhost:8080`
- Ngrok Dashboard: `http://localhost:4040`

### Remote Access (via Ngrok)

Ganti dengan URL ngrok Anda:

- Backend API: `https://abc123.ngrok-free.app`
- Admin Dashboard: `https://def456.ngrok-free.app`
- Client Frontend: `https://ghi789.ngrok-free.app`

---

## Security Notes

### API Key

- Ganti default API key di `.env`
- Jangan commit `.env` ke Git
- Gunakan key yang kuat (min 32 karakter)

### MongoDB

- Gunakan strong password
- Untuk production, whitelist IP spesifik (bukan 0.0.0.0/0)
- Enable MongoDB Atlas backup

### Ngrok

- Free tier: URL berubah setiap restart
- Paid tier: custom domain yang persistent
- Ngrok URLs bersifat public, siapa saja bisa akses

### CORS

- Update `allow_origins` di backend untuk production
- Jangan gunakan `*` di production
- Specify exact ngrok URLs

---

## Troubleshooting Checklist

- [ ] WSL2 running: `wsl --list --verbose`
- [ ] Docker running: `docker ps`
- [ ] Backend container running: `docker ps | grep parkit-backend`
- [ ] Backend healthy: `curl http://localhost:8000/health`
- [ ] MongoDB connected: Check backend logs
- [ ] Model file exists: `ls ~/parkit/backend/models/best.pt`
- [ ] Frontend accessible: Open browser to `http://localhost:3000`
- [ ] Ngrok tunnels active: Check `http://localhost:4040`
- [ ] CORS configured: Check browser console
- [ ] API key correct: Check `.env` file

---

## Contact & Support

**Lokasi**: Ruang B506
**Sistem**: PC Lokal dengan Docker WSL2 + Ngrok

Untuk issues atau pertanyaan:
- Check logs: `docker logs parkit-backend`
- Check documentation: `README.md`, `CLIENT_API_DOCUMENTATION.md`, `ADMIN_API_DOCUMENTATION.md`
- Check backend flow: `docs/BACKEND_FLOW.md`

---

## Changelog

### Version 1.0.0 (2025)
- Initial deployment guide untuk setup lokal B506
- Docker WSL2 deployment
- Ngrok tunnel setup
- Admin dan Client frontend deployment
- MongoDB Atlas integration

---

**Last Updated**: 2025
**Location**: Ruang B506
**Deployment Type**: Local PC + Docker WSL2 + Ngrok
