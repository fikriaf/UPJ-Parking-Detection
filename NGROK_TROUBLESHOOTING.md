# Ngrok Troubleshooting Guide

## Error 8012: Failed to connect to localhost

Error ini terjadi ketika ngrok tidak bisa connect ke service lokal Anda.

### Penyebab Umum

1. **Service tidak berjalan** di port yang ditentukan
2. **Port salah** di konfigurasi ngrok
3. **Service binding ke 127.0.0.1** bukan 0.0.0.0
4. **Firewall** memblokir koneksi
5. **Docker network** issue (jika menggunakan Docker)

---

## Langkah Troubleshooting

### 1. Pastikan Service Berjalan

```bash
# Check apakah ada service di port 8000, 3000, 8080
netstat -ano | findstr "8000"
netstat -ano | findstr "3000"
netstat -ano | findstr "8080"

# Atau di WSL/Linux:
sudo lsof -i :8000
sudo lsof -i :3000
sudo lsof -i :8080

# Atau dengan PowerShell:
Get-NetTCPConnection -LocalPort 8000,3000,8080
```

**Jika tidak ada output**, berarti service tidak berjalan!

### 2. Start Services Terlebih Dahulu

#### Backend (Port 8000)

```bash
# Option 1: Docker
cd ~/parkit/backend
docker-compose up -d

# Option 2: Manual
cd ~/parkit/backend
source venv/bin/activate  # Linux/WSL
# atau: venv\Scripts\activate  # Windows
uvicorn main:app --host 0.0.0.0 --port 8000

# Verify
curl http://localhost:8000/health
```

#### Admin Frontend (Port 3000)

```bash
# Option 1: Docker
docker run -d -p 3000:80 --name parkit-admin-frontend parkit-admin-frontend

# Option 2: Manual
cd ~/parkit/frontend
python3 -m http.server 3000

# Verify
curl http://localhost:3000
```

#### Client Frontend (Port 8080)

```bash
# Manual
cd ~/parkit/client
python3 -m http.server 8080

# Verify
curl http://localhost:8080
```

### 3. Test Koneksi Lokal

Sebelum start ngrok, pastikan service bisa diakses:

```bash
# Test backend
curl http://localhost:8000/health

# Test admin (akan return HTML)
curl -I http://localhost:3000

# Test client (akan return HTML)
curl -I http://localhost:8080
```

**Jika curl gagal**, service belum ready atau tidak berjalan!

### 4. Check Docker Network (Jika Pakai Docker)

Jika menggunakan Docker, ngrok di host tidak bisa langsung akses container:

```bash
# Check container running
docker ps

# Check port mapping
docker ps --format "table {{.Names}}\t{{.Ports}}"

# Pastikan port di-expose ke host:
# 0.0.0.0:8000->8000/tcp
# 0.0.0.0:3000->80/tcp
```

### 5. Fix ngrok.yml Configuration

Pastikan indentasi benar (gunakan 2 spaces):

```yaml
version: "2"
authtoken: YOUR_ACTUAL_TOKEN_HERE

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

**PENTING**: Ganti `<your-authtoken>` dengan token asli dari ngrok dashboard!

### 6. Start Ngrok dengan Benar

```bash
# Start semua tunnels
ngrok start --all --config ngrok.yml

# Atau start satu per satu untuk testing
ngrok http 8000 --config ngrok.yml
```

---

## Solusi Berdasarkan Setup

### Setup 1: Semua Service Manual (Tanpa Docker)

```bash
# Terminal 1: Backend
cd ~/parkit/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2: Admin Frontend
cd ~/parkit/frontend
python3 -m http.server 3000

# Terminal 3: Client Frontend
cd ~/parkit/client
python3 -m http.server 8080

# Terminal 4: Ngrok
ngrok start --all --config ngrok.yml
```

### Setup 2: Backend Docker, Frontend Manual

```bash
# Terminal 1: Backend Docker
cd ~/parkit/backend
docker-compose up

# Terminal 2: Admin Frontend
cd ~/parkit/frontend
python3 -m http.server 3000

# Terminal 3: Client Frontend
cd ~/parkit/client
python3 -m http.server 8080

# Terminal 4: Ngrok
ngrok start --all --config ngrok.yml
```

### Setup 3: Semua Docker

```bash
# Start backend
cd ~/parkit/backend
docker-compose up -d

# Start admin frontend
docker run -d -p 3000:80 --name parkit-admin parkit-admin-frontend

# Start client frontend
docker run -d -p 8080:80 --name parkit-client parkit-client-frontend

# Verify all running
docker ps

# Start ngrok
ngrok start --all --config ngrok.yml
```

---

## Checklist Sebelum Start Ngrok

- [ ] Backend berjalan di port 8000
- [ ] Admin frontend berjalan di port 3000
- [ ] Client frontend berjalan di port 8080
- [ ] Semua service bisa diakses via `curl http://localhost:PORT`
- [ ] ngrok.yml memiliki authtoken yang valid
- [ ] ngrok.yml indentasi benar (2 spaces)
- [ ] Tidak ada service lain yang menggunakan port yang sama

---

## Verifikasi Step by Step

### Step 1: Check Backend

```bash
# Check process
ps aux | grep uvicorn
# atau
docker ps | grep backend

# Test endpoint
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

### Step 2: Check Admin Frontend

```bash
# Check process
ps aux | grep "http.server 3000"
# atau
docker ps | grep admin

# Test endpoint
curl -I http://localhost:3000
# Expected: HTTP/1.0 200 OK
```

### Step 3: Check Client Frontend

```bash
# Check process
ps aux | grep "http.server 8080"
# atau
docker ps | grep client

# Test endpoint
curl -I http://localhost:8080
# Expected: HTTP/1.0 200 OK
```

### Step 4: Start Ngrok

```bash
# Validate config first
cat ngrok.yml

# Start ngrok
ngrok start --all --config ngrok.yml

# Check ngrok dashboard
# Open browser: http://localhost:4040
```

---

## Common Errors & Solutions

### Error: "Failed to connect to localhost:3000"

**Penyebab**: Admin frontend tidak berjalan

**Solusi**:
```bash
cd ~/parkit/frontend
python3 -m http.server 3000
```

### Error: "Failed to connect to localhost:8080"

**Penyebab**: Client frontend tidak berjalan

**Solusi**:
```bash
cd ~/parkit/client
python3 -m http.server 8080
```

### Error: "Failed to connect to localhost:8000"

**Penyebab**: Backend tidak berjalan

**Solusi**:
```bash
cd ~/parkit/backend
docker-compose up -d
# atau
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Error: "Address already in use"

**Penyebab**: Port sudah digunakan service lain

**Solusi**:
```bash
# Find process using port
sudo lsof -i :3000

# Kill process
kill -9 <PID>

# Atau di Windows
netstat -ano | findstr "3000"
taskkill /PID <PID> /F
```

### Error: "Invalid authtoken"

**Penyebab**: Token di ngrok.yml salah atau belum diganti

**Solusi**:
1. Login ke https://dashboard.ngrok.com/
2. Copy authtoken
3. Edit ngrok.yml dan ganti `<your-authtoken>` dengan token asli

---

## Quick Fix Script

Buat script untuk start semua service:

```bash
#!/bin/bash
# start-all.sh

echo "Starting Backend..."
cd ~/parkit/backend
docker-compose up -d
sleep 5

echo "Starting Admin Frontend..."
cd ~/parkit/frontend
python3 -m http.server 3000 &
sleep 2

echo "Starting Client Frontend..."
cd ~/parkit/client
python3 -m http.server 8080 &
sleep 2

echo "Verifying services..."
curl -s http://localhost:8000/health && echo "✓ Backend OK"
curl -s -I http://localhost:3000 | head -1 && echo "✓ Admin OK"
curl -s -I http://localhost:8080 | head -1 && echo "✓ Client OK"

echo ""
echo "Starting Ngrok..."
ngrok start --all --config ~/ngrok.yml
```

Jalankan:
```bash
chmod +x start-all.sh
./start-all.sh
```

---

## Debug Mode

Untuk debug lebih detail:

```bash
# Start ngrok dengan log level debug
ngrok start --all --config ngrok.yml --log=stdout --log-level=debug

# Check ngrok web interface
# Open: http://localhost:4040
# Lihat tab "Status" dan "Inspect"
```

---

## Kesimpulan

**Urutan yang benar:**

1. ✅ Start Backend (port 8000)
2. ✅ Start Admin Frontend (port 3000)
3. ✅ Start Client Frontend (port 8080)
4. ✅ Verify semua service dengan curl
5. ✅ Start Ngrok

**Jangan start ngrok sebelum service berjalan!**
