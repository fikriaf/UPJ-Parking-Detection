# Backend Flow - Parkit System

## Backend Architecture & Processing Flow

```mermaid
flowchart TD
    Start([Start Backend Server]) --> Init[Initialize FastAPI App]
    Init --> LoadModel[Load YOLO Model]
    LoadModel --> LoadCalib[Load Calibration Data]
    LoadCalib --> Ready[Backend Ready]
    
    Ready --> API{API Request}
    
    %% Upload Frame Flow
    API -->|POST /upload| UploadFrame[Receive Frame Upload]
    UploadFrame --> ValidateFrame{Valid Image?}
    ValidateFrame -->|No| Error400[Return 400 Error]
    ValidateFrame -->|Yes| SaveFrame[Save Frame to Storage]
    SaveFrame --> CreateSession{Session Exists?}
    CreateSession -->|No| NewSession[Create New Session]
    CreateSession -->|Yes| UpdateSession[Update Session]
    NewSession --> StoreFrame[Store Frame Metadata]
    UpdateSession --> StoreFrame
    StoreFrame --> Return200[Return 200 Success]
    
    %% Complete Session Flow
    API -->|POST /complete| CompleteReq[Complete Session Request]
    CompleteReq --> GetFrames[Get All Session Frames]
    GetFrames --> ProcessLoop{For Each Frame}
    ProcessLoop --> RunYOLO[Run YOLO Detection]
    RunYOLO --> GetDetections[Get Bounding Boxes]
    GetDetections --> CheckCalib{Calibration Active?}
    CheckCalib -->|Yes| AssignRows[Assign Detections to Rows]
    CheckCalib -->|No| StoreDetection[Store Detection Results]
    AssignRows --> CalcSpaces[Calculate Empty Spaces]
    CalcSpaces --> StoreDetection
    StoreDetection --> NextFrame{More Frames?}
    NextFrame -->|Yes| ProcessLoop
    NextFrame -->|No| SelectBest[Select Best Frame]
    SelectBest --> DrawAnnotations[Draw Bounding Boxes & Spaces]
    DrawAnnotations --> SaveImage[Save Annotated Image]
    SaveImage --> UpdateStatus[Update Session Status]
    UpdateStatus --> ReturnResult[Return Detection Result]
    
    %% Get Results Flow
    API -->|GET /results/live| GetLive[Get Active Session]
    GetLive --> ReturnLive[Return Live Results]
    
    API -->|GET /results/:id| GetSession[Get Session by ID]
    GetSession --> ReturnSession[Return Session Results]
    
    API -->|GET /results/:id/image| GetImage[Get Annotated Image]
    GetImage --> ReturnImage[Return JPEG Image]
    
    API -->|GET /results/latest| GetLatest[Get Latest Sessions]
    GetLatest --> ReturnList[Return Sessions List]
    
    %% Calibration Flow
    API -->|POST /calibration| CalibReq[Calibration Request]
    CalibReq --> ValidateCalib{Valid Data?}
    ValidateCalib -->|No| Error422[Return 422 Error]
    ValidateCalib -->|Yes| SaveCalib[Save Calibration]
    SaveCalib --> ReturnCalib[Return Calibration Data]
    
    API -->|GET /calibration/:id| GetCalibReq[Get Calibration]
    GetCalibReq --> ReturnCalibData[Return Calibration]
    
    API -->|DELETE /calibration/:id| DeleteCalib[Delete Calibration]
    DeleteCalib --> ReturnDelete[Return Success]
    
    %% Error Handling
    Error400 --> API
    Error422 --> API
    Return200 --> API
    ReturnResult --> API
    ReturnLive --> API
    ReturnSession --> API
    ReturnImage --> API
    ReturnList --> API
    ReturnCalib --> API
    ReturnCalibData --> API
    ReturnDelete --> API
    
    style Start fill:#90EE90
    style Ready fill:#87CEEB
    style Error400 fill:#FFB6C1
    style Error422 fill:#FFB6C1
    style ReturnResult fill:#98FB98
    style SaveImage fill:#FFD700
```

## Key Components

### 1. YOLO Detection Engine
- Model: YOLOv8 (motorcycle detection)
- Input: Image frames
- Output: Bounding boxes with confidence scores

### 2. Calibration System
- Stores parking row positions
- Assigns detections to rows
- Calculates empty spaces
- Determines motorcycle fit

### 3. Session Management
- Tracks upload sessions
- Stores frame metadata
- Manages detection results
- Handles session lifecycle

### 4. Storage Layer
- Frame images (uploads/)
- Annotated results (results/)
- Session data (in-memory/database)
- Calibration data (JSON files)

## Processing Pipeline

1. **Frame Upload** → Validate → Store → Track Session
2. **Detection** → YOLO → Bounding Boxes → Confidence Filtering
3. **Calibration** → Row Assignment → Space Calculation → Occupancy Rate
4. **Annotation** → Draw Boxes → Draw Spaces → Save Image
5. **Results** → Best Frame Selection → API Response

