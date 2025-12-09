import time
import torch
import numpy as np
from chatterbox.tts import ChatterboxTTS
from ..core.config import settings

class InferenceService:
    _instance = None
    _lora_model = None
    _base_model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InferenceService, cls).__new__(cls)
        return cls._instance

    def initialize(self):
        print(f"Initializing Inference Models on {settings.DEVICE}...")
        
        # 1. Load LoRA Model (Fine-tuned)
        if self._lora_model is None:
            if settings.MODEL_PATH:
                print(f"Loading LoRA Model from {settings.MODEL_PATH}...")
                self._lora_model = ChatterboxTTS.from_local(ckpt_dir=settings.MODEL_PATH, device=settings.DEVICE)
            else:
                print("Warning: No MODEL_PATH set for LoRA. Using pretrained as LoRA (fallback).")
                self._lora_model = ChatterboxTTS.from_pretrained(device=settings.DEVICE)
        
        # 2. Load Base Model (Pretrained)
        if self._base_model is None:
            print("Loading Base Model (Pretrained)...")
            self._base_model = ChatterboxTTS.from_pretrained(device=settings.DEVICE)
            
        print("Models initialized.")

    def _generate_single(self, model, text: str, ref_audio_path: str, temperature: float) -> tuple[np.ndarray, float]:
        start_time = time.time()
        
        # Heuristic for max length: ~15 tokens per second of speech? 
        # Better: char length * factor. Average speaking rate is ~15 chars/sec.
        # Let's be generous: text_len * 0.5 seconds * 24000 samples? 
        # Actually, for T3 generation, we control 'max_new_tokens'.
        # A conservative estimate: 10 tokens per character is way too much.
        # Let's try to limit based on text length to avoid 40s of silence.
        # 400 chars ~ 30-40 seconds. 
        # So max_new_tokens = len(text) * 3 (rough token estimate) + buffer
        
        # However, ChatterboxTTS.generate might not expose max_new_tokens directly in all versions.
        # We will try to pass it.
        
        # Also, we enforce device placement just in case
        
        try:
            wav = model.generate(
                text,
                audio_prompt_path=ref_audio_path,
                temperature=temperature,
                top_p=0.9,
                repetition_penalty=1.5, # Increased to prevent loops/silence
                min_p=0.05,
                lang="es"
            )
        except TypeError:
            wav = model.generate(
                text,
                audio_prompt_path=ref_audio_path,
                temperature=temperature,
                top_p=0.9,
                repetition_penalty=1.5,
                min_p=0.05
            )

        if isinstance(wav, torch.Tensor):
            wav = wav.cpu().numpy()
        if wav.ndim > 1:
            wav = wav.squeeze()
            
        # Post-processing: Trim silence
        # This is the "safety net"
        import librosa
        wav, _ = librosa.effects.trim(wav, top_db=30)
            
        return wav, time.time() - start_time

    def generate_dual(self, text: str, ref_audio_path: str, temperature: float = 0.7) -> dict:
        """
        Generates audio using both LoRA and Base models.
        Returns: { 'lora': (wav, time), 'base': (wav, time) }
        """
        if self._lora_model is None or self._base_model is None:
            self.initialize()

        # Generate LoRA
        lora_wav, lora_time = self._generate_single(self._lora_model, text, ref_audio_path, temperature)
        
        # Generate Base
        base_wav, base_time = self._generate_single(self._base_model, text, ref_audio_path, temperature)
        
        return {
            "lora": (lora_wav, lora_time),
            "base": (base_wav, base_time)
        }

inference_service = InferenceService()
