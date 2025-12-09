import torch
import numpy as np
from chatterbox.models.voice_encoder import VoiceEncoder
from ..core.config import settings

class VoiceEncoderService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VoiceEncoderService, cls).__new__(cls)
        return cls._instance

    def initialize(self):
        if self._model is None:
            print(f"Initializing VoiceEncoder on {settings.DEVICE}...")
            # VoiceEncoder loads pre-trained weights automatically from HF if not provided
            self._model = VoiceEncoder().to(settings.DEVICE).eval()
            print("VoiceEncoder initialized.")

    def compute_embedding(self, wav: np.ndarray) -> list[float]:
        """
        Computes the voice embedding for a given 16kHz mono audio array.
        """
        if self._model is None:
            self.initialize()
            
        # VoiceEncoder expects a list of wavs, or a batch
        # embeds_from_wavs handles preprocessing internally but we already did resampling
        # It expects raw audio samples
        
        with torch.no_grad():
            # We use the internal method or the convenience wrapper
            # The wrapper `embeds_from_wavs` is robust
            embeds = self._model.embeds_from_wavs(
                [wav],
                sample_rate=settings.SAMPLE_RATE,
                as_spk=False, # We want the embedding vector
                batch_size=1,
                rate=1.3,
                overlap=0.5
            )
            
            # embeds is (N, 256) where N is number of segments found
            # We usually average them for a stable speaker ID
            
            parts = torch.from_numpy(embeds)
            if len(parts) == 0:
                # Fallback if no voice detected
                return np.zeros(256).tolist()
                
            ref = parts[0].unsqueeze(0)
            sims = torch.nn.functional.cosine_similarity(parts, ref, dim=-1)
            voiced = parts[sims > 0.6]
            
            if len(voiced) > 0:
                final_embed = voiced.mean(0)
            else:
                final_embed = parts.mean(0)
                
            # Normalize
            final_embed = final_embed / final_embed.norm(p=2, dim=-1, keepdim=True)
            
            return final_embed.cpu().numpy().tolist()

voice_encoder_service = VoiceEncoderService()
