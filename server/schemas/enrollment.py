from pydantic import BaseModel
from typing import List, Optional

class VoiceMetadata(BaseModel):
    id: str
    name: str
    created_at: str
    enrollment_time_seconds: float
    ref_audio_path: Optional[str] = None

class VoiceEnrollmentResponse(BaseModel):
    voice_id: List[float]
    metadata: VoiceMetadata
    status: str = "success"

class InferenceRequest(BaseModel):
    text: str
    voice_id: str
    temperature: float = 0.7
    speed: float = 1.0

class InferenceResponse(BaseModel):
    audio_url_lora: str
    inference_time_lora: float
    audio_url_base: str
    inference_time_base: float
    status: str = "success"

class InferenceHistoryItem(BaseModel):
    id: str
    voice_id: str
    text: str
    audio_path: Optional[str] = None # Legacy
    audio_path_lora: Optional[str] = None
    audio_path_base: Optional[str] = None
    created_at: str
    inference_time_seconds: Optional[float] = None # Legacy
    inference_time_lora: Optional[float] = None
    inference_time_base: Optional[float] = None

class ErrorResponse(BaseModel):
    detail: str
