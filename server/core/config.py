import os
import torch
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Chatterbox Enrollment Service"
    API_V1_STR: str = "/api/v1"
    
    # Audio constraints
    MIN_AUDIO_DURATION: float = 1.0
    MAX_AUDIO_DURATION: float = 30.0
    SAMPLE_RATE: int = 16000 # Required by VoiceEncoder
    
    # Model paths (optional, can load default)
    MODEL_PATH: str | None = "./checkpoints_lora/merged_model"
    DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"

    class Config:
        case_sensitive = True

settings = Settings()
