from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str = "mongodb+srv://vulgansaran_db_user:mvSK7Fh1kZRhAOmJ@cluster0.9gm55jt.mongodb.net/?appName=Cluster0"
    DATABASE_NAME: str = "parkit_db"
    
    # Model
    MODEL_PATH: str = "models/best.pt"
    CONFIDENCE_THRESHOLD: float = 0.25
    IOU_THRESHOLD: float = 0.45
    MAX_DETECTIONS: int = 300
    
    # Frame processing
    MAX_FRAMES_PER_SESSION: int = 10
    FRAME_COMPARISON_WINDOW: int = 5  # Compare last N frames
    
    # Admin
    ADMIN_API_KEY: str = "parkit-admin-secret-key-change-this"
    
    # Calibration (Optional - for parking space detection)
    DEFAULT_MIN_SPACE_WIDTH: float = 150.0
    DEFAULT_SPACE_COEFFICIENT: float = 0.8
    MAX_PARKING_ROWS: int = 10
    
    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"  # Ignore extra fields in .env
    )

settings = Settings()
