import librosa
import numpy as np
import torch
import io
from fastapi import UploadFile, HTTPException
from ..core.config import settings

class AudioProcessor:
    @staticmethod
    async def process_upload(file: UploadFile) -> tuple[np.ndarray, float]:
        """
        Reads an uploaded audio file, resamples to 16kHz mono, and trims silence.
        Returns: (audio_array, duration_seconds)
        """
        try:
            # Read file into memory
            contents = await file.read()
            # Load with librosa (handles wav, mp3, etc.)
            # sr=16000 is critical for VoiceEncoder
            wav, sr = librosa.load(io.BytesIO(contents), sr=settings.SAMPLE_RATE, mono=True)
            
            # Trim silence
            wav, _ = librosa.effects.trim(wav, top_db=20)
            
            # Normalize volume
            wav = librosa.util.normalize(wav)
            
            duration = len(wav) / sr
            
            # Validate duration
            if duration < settings.MIN_AUDIO_DURATION:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Audio too short ({duration:.2f}s). Min required: {settings.MIN_AUDIO_DURATION}s"
                )
            
            # We don't strictly enforce max duration here, but we could truncate
            if duration > settings.MAX_AUDIO_DURATION:
                # Optional: truncate
                wav = wav[:int(settings.MAX_AUDIO_DURATION * sr)]
                duration = settings.MAX_AUDIO_DURATION
                
            return wav, duration
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=400, detail=f"Invalid audio file: {str(e)}")

audio_processor = AudioProcessor()
