import json
import os
import time
import numpy as np
from typing import List, Optional, Dict
from datetime import datetime
from ..schemas.enrollment import VoiceMetadata, InferenceHistoryItem
from ..core.config import settings

class StorageService:
    def __init__(self):
        # Ensure directories exist
        self.voices_dir = os.path.join("server", "data", "voices")
        self.audio_input_dir = os.path.join("server", "data", "audio_input")
        self.audio_output_dir = os.path.join("server", "data", "audio_output")
        self.history_dir = os.path.join("server", "data", "history")
        
        os.makedirs(self.voices_dir, exist_ok=True)
        os.makedirs(self.audio_input_dir, exist_ok=True)
        os.makedirs(self.audio_output_dir, exist_ok=True)
        os.makedirs(self.history_dir, exist_ok=True)

    def save_voice(self, name: str, embedding: List[float], enrollment_time: float, ref_audio_path: str = None) -> VoiceMetadata:
        safe_name = "".join([c for c in name if c.isalnum() or c in ('-', '_')]).lower()
        timestamp = int(time.time())
        voice_id = f"{safe_name}_{timestamp}"
        
        npy_path = os.path.join(self.voices_dir, f"{voice_id}.npy")
        np.save(npy_path, np.array(embedding, dtype=np.float32))
        
        metadata = VoiceMetadata(
            id=voice_id,
            name=name,
            created_at=datetime.now().isoformat(),
            enrollment_time_seconds=enrollment_time,
            ref_audio_path=ref_audio_path
        )
        
        json_path = os.path.join(self.voices_dir, f"{voice_id}.json")
        with open(json_path, "w") as f:
            f.write(metadata.model_dump_json(indent=2))
            
        return metadata

    def list_voices(self) -> List[VoiceMetadata]:
        voices = []
        if not os.path.exists(self.voices_dir):
            return []
            
        for filename in os.listdir(self.voices_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(self.voices_dir, filename), "r") as f:
                        data = json.load(f)
                        voices.append(VoiceMetadata(**data))
                except Exception as e:
                    print(f"Error loading voice metadata {filename}: {e}")
        
        voices.sort(key=lambda x: x.created_at, reverse=True)
        return voices

    def get_voice_metadata(self, voice_id: str) -> Optional[VoiceMetadata]:
        json_path = os.path.join(self.voices_dir, f"{voice_id}.json")
        if not os.path.exists(json_path):
            return None
        with open(json_path, "r") as f:
            return VoiceMetadata(**json.load(f))

    def delete_voice(self, voice_id: str):
        # Delete JSON
        json_path = os.path.join(self.voices_dir, f"{voice_id}.json")
        if os.path.exists(json_path):
            # Load to get ref audio path if we want to delete it too
            # But ref audio might be shared? Unlikely with our naming scheme.
            # Let's try to delete ref audio too.
            try:
                with open(json_path, "r") as f:
                    data = json.load(f)
                    ref_path = data.get("ref_audio_path")
                    if ref_path:
                        full_ref = os.path.join(self.audio_input_dir, ref_path)
                        if os.path.exists(full_ref):
                            os.remove(full_ref)
            except:
                pass
            os.remove(json_path)
            
        # Delete NPY
        npy_path = os.path.join(self.voices_dir, f"{voice_id}.npy")
        if os.path.exists(npy_path):
            os.remove(npy_path)

    def save_inference_dual(self, lora_wav: np.ndarray, base_wav: np.ndarray, sample_rate: int, text: str, voice_id: str, lora_time: float, base_time: float) -> dict:
        import soundfile as sf
        timestamp = int(time.time())
        
        # Save LoRA
        filename_lora = f"infer_lora_{voice_id}_{timestamp}.wav"
        path_lora = os.path.join(self.audio_output_dir, filename_lora)
        sf.write(path_lora, lora_wav, sample_rate)
        
        # Save Base
        filename_base = f"infer_base_{voice_id}_{timestamp}.wav"
        path_base = os.path.join(self.audio_output_dir, filename_base)
        sf.write(path_base, base_wav, sample_rate)
        
        # Save History
        history_item = InferenceHistoryItem(
            id=f"hist_{timestamp}",
            voice_id=voice_id,
            text=text,
            audio_path_lora=filename_lora,
            audio_path_base=filename_base,
            created_at=datetime.now().isoformat(),
            inference_time_lora=lora_time,
            inference_time_base=base_time
        )
        
        hist_path = os.path.join(self.history_dir, f"{history_item.id}.json")
        with open(hist_path, "w") as f:
            f.write(history_item.model_dump_json(indent=2))
            
        return {
            "lora_path": path_lora,
            "base_path": path_base
        }

    def list_history(self) -> List[InferenceHistoryItem]:
        items = []
        if not os.path.exists(self.history_dir):
            return []
            
        for filename in os.listdir(self.history_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(self.history_dir, filename), "r") as f:
                        data = json.load(f)
                        items.append(InferenceHistoryItem(**data))
                except Exception as e:
                    print(f"Error loading history {filename}: {e}")
        
        items.sort(key=lambda x: x.created_at, reverse=True)
        return items

    def delete_history_item(self, history_id: str):
        json_path = os.path.join(self.history_dir, f"{history_id}.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r") as f:
                    data = json.load(f)
                    # Delete both audios
                    if "audio_path_lora" in data:
                        p = os.path.join(self.audio_output_dir, data["audio_path_lora"])
                        if os.path.exists(p): os.remove(p)
                    if "audio_path_base" in data:
                        p = os.path.join(self.audio_output_dir, data["audio_path_base"])
                        if os.path.exists(p): os.remove(p)
                    # Legacy support
                    if "audio_path" in data:
                        p = os.path.join(self.audio_output_dir, data["audio_path"])
                        if os.path.exists(p): os.remove(p)
            except:
                pass
            os.remove(json_path)

storage_service = StorageService()
