# Requirements Document

## Introduction

Sistem admin dashboard frontend untuk ParkIt adalah aplikasi web berbasis HTML yang memungkinkan administrator mengelola sistem deteksi parkir motor. Dashboard ini menyediakan antarmuka untuk upload frame CCTV, konfigurasi kalibrasi kamera, monitoring hasil deteksi real-time, dan manajemen data sistem. Dashboard akan berkomunikasi dengan backend FastAPI melalui REST API dan memerlukan autentikasi menggunakan API key.

## Glossary

- **Admin Dashboard**: Aplikasi web HTML untuk administrator sistem ParkIt
- **Backend API**: FastAPI server yang menyediakan endpoint REST untuk operasi sistem
- **Frame**: Gambar tunggal dari CCTV/kamera yang akan diproses untuk deteksi motor
- **Session**: Kumpulan frame yang di-upload dalam satu sesi deteksi
- **Calibration**: Konfigurasi parameter kamera untuk deteksi ruang parkir kosong
- **Empty Space**: Area parkir yang kosong dan dapat diisi motor
- **Detection Result**: Hasil analisis frame yang menunjukkan posisi motor dan ruang kosong
- **API Key**: Token autentikasi untuk mengakses endpoint admin
- **Camera ID**: Identifier unik untuk setiap kamera CCTV
- **Row**: Baris horizontal area parkir dalam frame kamera
- **Best Frame**: Frame dengan jumlah deteksi motor terbanyak dalam satu session

## Requirements

### Requirement 1: Admin Authentication

**User Story:** Sebagai administrator, saya ingin login menggunakan API key agar dapat mengakses fitur admin dashboard dengan aman

#### Acceptance Criteria

1. WHEN administrator membuka dashboard, THE Admin Dashboard SHALL menampilkan form input API key
2. WHEN administrator memasukkan API key dan submit, THE Admin Dashboard SHALL menyimpan API key di browser localStorage
3. WHEN API key tersimpan, THE Admin Dashboard SHALL menampilkan halaman utama dashboard
4. IF API key tidak valid saat request ke backend, THEN THE Admin Dashboard SHALL menampilkan pesan error dan kembali ke form login
5. WHERE administrator sudah login, THE Admin Dashboard SHALL menyediakan tombol logout untuk menghapus API key dari localStorage

### Requirement 2: Frame Upload Management

**User Story:** Sebagai administrator, saya ingin upload multiple frame dari CCTV agar sistem dapat memilih frame terbaik untuk deteksi

#### Acceptance Criteria

1. THE Admin Dashboard SHALL menampilkan form upload dengan input file multiple dan field session_id
2. WHEN administrator memilih file gambar, THE Admin Dashboard SHALL menampilkan preview thumbnail untuk setiap file
3. WHEN administrator klik tombol upload, THE Admin Dashboard SHALL mengirim setiap file ke endpoint POST /api/frames/upload dengan API key di header
4. WHILE upload sedang berjalan, THE Admin Dashboard SHALL menampilkan progress bar dan status upload untuk setiap file
5. WHEN semua file berhasil di-upload, THE Admin Dashboard SHALL menampilkan tombol "Complete Session"
6. WHEN administrator klik "Complete Session", THE Admin Dashboard SHALL memanggil endpoint POST /api/frames/complete/{session_id}
7. IF upload gagal untuk satu atau lebih file, THEN THE Admin Dashboard SHALL menampilkan error message dengan detail file yang gagal

### Requirement 3: Camera Calibration Configuration

**User Story:** Sebagai administrator, saya ingin mengkonfigurasi kalibrasi kamera agar sistem dapat mendeteksi ruang parkir kosong dengan akurat

#### Acceptance Criteria

1. THE Admin Dashboard SHALL menampilkan halaman kalibrasi dengan form input untuk camera_id, rows, min_space_width, space_coefficient, row_start_x, dan row_end_x
2. WHERE administrator menambah row baru, THE Admin Dashboard SHALL menampilkan input fields untuk row_index, y_coordinate, dan label
3. WHEN administrator submit form kalibrasi, THE Admin Dashboard SHALL mengirim data ke endpoint POST /api/admin/calibration/ dengan validasi client-side
4. THE Admin Dashboard SHALL memvalidasi bahwa y_coordinate untuk setiap row dalam urutan ascending sebelum submit
5. THE Admin Dashboard SHALL memvalidasi bahwa min_space_width berada dalam range 10-500 pixels
6. THE Admin Dashboard SHALL memvalidasi bahwa space_coefficient berada dalam range 0.1-1.0
7. WHEN kalibrasi berhasil disimpan, THE Admin Dashboard SHALL menampilkan notifikasi sukses dan refresh daftar kalibrasi
8. IF validasi gagal, THEN THE Admin Dashboard SHALL menampilkan error message dengan detail field yang tidak valid

### Requirement 4: Calibration Management

**User Story:** Sebagai administrator, saya ingin melihat dan mengelola semua kalibrasi kamera yang ada agar dapat memantau konfigurasi sistem

#### Acceptance Criteria

1. THE Admin Dashboard SHALL menampilkan tabel daftar semua kalibrasi dengan kolom camera_id, jumlah rows, min_space_width, space_coefficient, dan action buttons
2. WHEN halaman kalibrasi dibuka, THE Admin Dashboard SHALL memanggil endpoint GET /api/admin/calibration/ untuk mendapatkan daftar kalibrasi
3. WHERE administrator klik tombol "View" pada kalibrasi, THE Admin Dashboard SHALL menampilkan detail lengkap kalibrasi dalam modal atau section terpisah
4. WHERE administrator klik tombol "Edit" pada kalibrasi, THE Admin Dashboard SHALL mengisi form kalibrasi dengan data existing untuk diedit
5. WHERE administrator klik tombol "Delete" pada kalibrasi, THE Admin Dashboard SHALL menampilkan konfirmasi dialog sebelum menghapus
6. WHEN administrator konfirmasi delete, THE Admin Dashboard SHALL memanggil endpoint DELETE /api/admin/calibration/{camera_id}
7. WHEN delete berhasil, THE Admin Dashboard SHALL menghapus item dari tabel dan menampilkan notifikasi sukses

### Requirement 5: Detection Results Monitoring

**User Story:** Sebagai administrator, saya ingin melihat hasil deteksi real-time dan history agar dapat memantau performa sistem

#### Acceptance Criteria

1. THE Admin Dashboard SHALL menampilkan section "Live Detection" yang menampilkan hasil deteksi terkini
2. THE Admin Dashboard SHALL memanggil endpoint GET /api/results/live setiap 5 detik untuk update data live
3. WHERE hasil deteksi tersedia, THE Admin Dashboard SHALL menampilkan gambar hasil deteksi dengan bounding boxes
4. THE Admin Dashboard SHALL menampilkan informasi total_motorcycles, total_empty_spaces, dan parking_occupancy_rate
5. WHERE kalibrasi aktif, THE Admin Dashboard SHALL menampilkan breakdown empty_spaces_per_row dalam format visual
6. THE Admin Dashboard SHALL menampilkan tabel history hasil deteksi dengan kolom session_id, timestamp, detection_count, dan status
7. WHEN administrator klik session_id di tabel, THE Admin Dashboard SHALL menampilkan detail hasil deteksi session tersebut
8. THE Admin Dashboard SHALL menyediakan tombol "Refresh" untuk manual update data

### Requirement 6: System Statistics Dashboard

**User Story:** Sebagai administrator, saya ingin melihat statistik sistem secara keseluruhan agar dapat memantau penggunaan dan performa

#### Acceptance Criteria

1. THE Admin Dashboard SHALL menampilkan halaman dashboard utama dengan statistik sistem
2. WHEN halaman dashboard dibuka, THE Admin Dashboard SHALL memanggil endpoint GET /api/admin/stats
3. THE Admin Dashboard SHALL menampilkan card untuk total_users, total_sessions, active_sessions, completed_sessions, dan total_detections
4. THE Admin Dashboard SHALL menampilkan statistik dalam format visual yang mudah dibaca (cards dengan icons)
5. WHERE data statistik berhasil dimuat, THE Admin Dashboard SHALL menampilkan timestamp last update
6. THE Admin Dashboard SHALL menyediakan tombol "Refresh Stats" untuk update manual

### Requirement 7: Session Management

**User Story:** Sebagai administrator, saya ingin mengelola session deteksi agar dapat menghapus data yang tidak diperlukan

#### Acceptance Criteria

1. THE Admin Dashboard SHALL menampilkan halaman session management dengan tabel semua session
2. WHEN halaman dibuka, THE Admin Dashboard SHALL memanggil endpoint GET /api/admin/sessions dengan pagination
3. THE Admin Dashboard SHALL menampilkan kolom session_id, camera_id, status, max_detection_count, total_frames, dan created_at
4. THE Admin Dashboard SHALL menyediakan filter untuk status session (all, active, completed)
5. WHERE administrator klik tombol "Delete" pada session, THE Admin Dashboard SHALL menampilkan konfirmasi dialog
6. WHEN administrator konfirmasi delete, THE Admin Dashboard SHALL memanggil endpoint DELETE /api/admin/sessions/{session_id}
7. THE Admin Dashboard SHALL menyediakan pagination controls (previous, next, page numbers)

### Requirement 8: User Management

**User Story:** Sebagai administrator, saya ingin mengelola user sistem agar dapat mengontrol akses pengguna

#### Acceptance Criteria

1. THE Admin Dashboard SHALL menampilkan halaman user management dengan tabel semua users
2. WHEN halaman dibuka, THE Admin Dashboard SHALL memanggil endpoint GET /api/admin/users dengan pagination
3. THE Admin Dashboard SHALL menampilkan kolom username, email, is_active, is_admin, dan created_at
4. WHERE administrator klik toggle "Active/Inactive", THE Admin Dashboard SHALL memanggil endpoint PUT /api/admin/users/{username}/toggle-active
5. WHEN toggle berhasil, THE Admin Dashboard SHALL update status di tabel tanpa reload halaman
6. THE Admin Dashboard SHALL menyediakan search box untuk filter users berdasarkan username atau email

### Requirement 9: Responsive Navigation

**User Story:** Sebagai administrator, saya ingin navigasi yang mudah antar halaman agar dapat mengakses fitur dengan cepat

#### Acceptance Criteria

1. THE Admin Dashboard SHALL menampilkan sidebar navigation dengan menu untuk Dashboard, Upload Frames, Calibration, Results, Sessions, dan Users
2. WHEN administrator klik menu item, THE Admin Dashboard SHALL menampilkan halaman yang sesuai tanpa reload full page
3. THE Admin Dashboard SHALL menandai menu item yang aktif dengan highlight visual
4. WHERE layar berukuran mobile, THE Admin Dashboard SHALL menampilkan hamburger menu untuk toggle sidebar
5. THE Admin Dashboard SHALL menampilkan header dengan logo ParkIt dan informasi admin yang sedang login

### Requirement 10: Error Handling dan Notifications

**User Story:** Sebagai administrator, saya ingin melihat notifikasi yang jelas untuk setiap aksi agar dapat mengetahui status operasi

#### Acceptance Criteria

1. WHEN operasi berhasil (create, update, delete), THE Admin Dashboard SHALL menampilkan toast notification sukses dengan pesan yang relevan
2. IF operasi gagal, THEN THE Admin Dashboard SHALL menampilkan toast notification error dengan detail error message dari backend
3. WHEN terjadi network error, THE Admin Dashboard SHALL menampilkan pesan "Connection failed. Please check your internet connection"
4. THE Admin Dashboard SHALL menampilkan loading spinner saat melakukan request ke backend
5. WHERE request memakan waktu lebih dari 30 detik, THE Admin Dashboard SHALL menampilkan timeout warning
6. THE Admin Dashboard SHALL menyimpan log error di browser console untuk debugging

### Requirement 11: Docker Containerization

**User Story:** Sebagai DevOps engineer, saya ingin frontend dapat di-deploy menggunakan Docker agar deployment konsisten dan mudah

#### Acceptance Criteria

1. THE Frontend Repository SHALL menyediakan Dockerfile untuk build container image
2. THE Dockerfile SHALL menggunakan nginx sebagai web server untuk serve static HTML files
3. WHEN Docker image di-build, THE Dockerfile SHALL menyalin semua file HTML, CSS, dan JavaScript ke nginx document root
4. THE Dockerfile SHALL mengkonfigurasi nginx untuk serve aplikasi pada port 80
5. WHEN container dijalankan, THE Frontend Application SHALL dapat diakses melalui browser pada port yang di-expose
6. THE Dockerfile SHALL menggunakan multi-stage build untuk optimasi ukuran image jika diperlukan

### Requirement 12: API Documentation

**User Story:** Sebagai developer, saya ingin dokumentasi lengkap endpoint API agar dapat memahami cara integrasi dengan backend

#### Acceptance Criteria

1. THE Project Repository SHALL menyediakan file CLIENT_API_DOCUMENTATION.md untuk endpoint public
2. THE CLIENT_API_DOCUMENTATION.md SHALL mendokumentasikan semua endpoint yang dapat diakses tanpa API key
3. THE CLIENT_API_DOCUMENTATION.md SHALL menyertakan contoh request dan response untuk setiap endpoint
4. THE Project Repository SHALL menyediakan file ADMIN_API_DOCUMENTATION.md untuk endpoint admin
5. THE ADMIN_API_DOCUMENTATION.md SHALL mendokumentasikan semua endpoint yang memerlukan API key
6. THE ADMIN_API_DOCUMENTATION.md SHALL menyertakan informasi tentang cara menggunakan API key di header request
7. BOTH documentation files SHALL menyertakan error codes dan handling untuk setiap endpoint
