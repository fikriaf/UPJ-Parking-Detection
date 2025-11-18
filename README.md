# Parkit - Smart Parking Detection System

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

Parkit is an intelligent parking detection system that uses YOLOv8 deep learning model to detect motorcycles and calculate available parking spaces in real-time. The system provides both admin dashboard for management and public client interface for viewing parking availability.

## Features

- **Real-time Detection**: Motorcycle detection using YOLOv8
- **Empty Space Calculation**: Automatic calculation of available parking spaces
- **Parking Row Calibration**: Configure parking rows for accurate space detection
- **Occupancy Tracking**: Real-time parking occupancy rate monitoring
- **Camera Integration**: Support for DroidCam and IP cameras
- **Session Management**: Multi-session support with history tracking
- **RESTful API**: Clean API for integration with other systems
- **Responsive UI**: Mobile-friendly admin dashboard and client interface

## Architecture

### System Components

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Camera    │────▶│   Frontend   │────▶│   Backend   │
│  (DroidCam) │     │  (Admin/UI)  │     │  (FastAPI)  │
└─────────────┘     └──────────────┘     └─────────────┘
                                                 │
                                                 ▼
                                          ┌─────────────┐
                                          │    YOLO     │
                                          │   Engine    │
                                          └─────────────┘
                                                 │
                                                 ▼
                                          ┌─────────────┐
                                          │   Storage   │
                                          │  (Results)  │
                                          └─────────────┘
```

### Flow Diagrams

- [Backend Processing Flow](docs/backend-flow.mmd)
- [Frontend Admin Flow](docs/frontend-flow.mmd)
- [Client Interface Flow](docs/client-frontend-flow.mmd)
- [System Architecture](docs/system-architecture.mmd)
- [User Journey](docs/user-journey.mmd)

### Documentation

- [Backend Flow Documentation](docs/BACKEND_FLOW.md)
- [Frontend Flow Documentation](docs/FRONTEND_FLOW.md)
- [System Communication Flow](docs/SYSTEM_COMMUNICATION_FLOW.md)
- [API Documentation](CLIENT_API_DOCUMENTATION.md)

## Quick Start

### Prerequisites

- Python 3.9+
- Docker & Docker Compose (optional)
- DroidCam or IP Camera (for live detection)

### Installation

#### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd parkit

# Start services
docker-compose up -d

# Access the application
# Backend API: http://localhost:8000
# Frontend: http://localhost:8080
```

#### Option 2: Manual Setup

```bash
# Backend setup
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend setup (separate terminal)
cd frontend
python -m http.server 8080
```

### Configuration

Create `.env` file in backend directory:

```env
# Model Configuration
MODEL_PATH=models/best.pt
CONFIDENCE_THRESHOLD=0.5

# Storage
UPLOAD_DIR=uploads
RESULTS_DIR=results
CALIBRATION_DIR=calibration

# Server
HOST=0.0.0.0
PORT=8000
```

## Usage

### 1. Camera Calibration (One-time Setup)

1. Navigate to Calibration page
2. Upload reference parking image
3. Click to mark parking row positions
4. Enter row details (spacing, motorcycle width)
5. Save calibration

### 2. Upload Frames

**Option A: Camera Stream**
1. Enter camera URL (e.g., `http://192.168.1.100:4747/video`)
2. Connect to camera
3. Capture frames from live preview
4. Upload captured frames

**Option B: Manual Upload**
1. Select image files from device
2. Preview selected images
3. Upload frames

### 3. Process Detection

1. Enter Session ID and Camera ID
2. Click "Upload Frames"
3. Click "Complete Session" to process
4. View detection results

### 4. View Results

- **Live View**: Real-time detection results
- **History**: Browse past detection sessions
- **Statistics**: Motorcycles count, empty spaces, occupancy rate
- **Annotated Image**: Visual representation with bounding boxes

## API Endpoints

### Public Endpoints (No Authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/results/live` | Get active detection session |
| GET | `/api/results/{session_id}` | Get specific session results |
| GET | `/api/results/{session_id}/image` | Get annotated result image |
| GET | `/api/results/latest` | Get latest sessions list |

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload frame image |
| POST | `/complete/{session_id}` | Process detection |
| POST | `/calibration` | Save calibration data |
| GET | `/calibration/{camera_id}` | Get calibration |
| DELETE | `/calibration/{camera_id}` | Delete calibration |

See [API Documentation](CLIENT_API_DOCUMENTATION.md) for detailed information.

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **ML Model**: YOLOv8 (Ultralytics)
- **Image Processing**: OpenCV, Pillow
- **Server**: Uvicorn (ASGI)

### Frontend
- **Architecture**: Single Page Application (SPA)
- **Language**: Vanilla JavaScript
- **Styling**: CSS3
- **API Client**: Fetch API

### Storage
- **Images**: File system
- **Calibration**: JSON files
- **Sessions**: In-memory (can be extended to database)

## Project Structure

```
parkit/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── models/              # Data models
│   │   ├── routers/             # API routes
│   │   └── services/            # Business logic
│   ├── models/                  # YOLO model files
│   ├── uploads/                 # Uploaded frames
│   ├── results/                 # Detection results
│   ├── calibration/             # Calibration data
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── app.js               # Main application
│       ├── router.js            # SPA router
│       ├── api-client.js        # API communication
│       └── pages/               # Page components
├── docs/
│   ├── backend-flow.mmd         # Backend flowchart
│   ├── frontend-flow.mmd        # Frontend flowchart
│   ├── client-frontend-flow.mmd # Client flowchart
│   ├── system-architecture.mmd  # Architecture diagram
│   └── user-journey.mmd         # User journey sequence
├── docker-compose.yml
└── README.md
```

## Development

### Running Tests

```bash
cd backend
pytest tests/
```

### Code Quality

```bash
# Format code
black app/

# Lint
flake8 app/

# Type checking
mypy app/
```

### Adding New Features

1. Create feature branch
2. Implement changes
3. Add tests
4. Update documentation
5. Submit pull request

## Performance

- **Detection Speed**: ~100-200ms per frame (GPU)
- **API Response**: <50ms (cached results)
- **Image Processing**: ~500ms per frame
- **Concurrent Sessions**: Supports multiple simultaneous sessions

## Troubleshooting

### Common Issues

**Camera Connection Failed**
- Check camera URL is correct
- Ensure camera is on same network
- Verify CORS settings on camera

**Detection Not Working**
- Verify YOLO model is loaded
- Check confidence threshold settings
- Ensure images are clear and well-lit

**Empty Spaces Not Calculated**
- Verify calibration is configured
- Check camera ID matches calibration
- Ensure parking rows are properly marked

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- YOLOv8 by Ultralytics
- FastAPI framework
- OpenCV community
- DroidCam for camera streaming

## Contact

For questions or support, please open an issue on GitHub.

---

**Built with Python, FastAPI, and YOLOv8**
