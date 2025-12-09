import torch
import torchaudio
import numpy as np
from torch.utils.data import Dataset
from chatterbox.tts import punc_norm
from chatterbox.models.s3tokenizer import S3_SR
from chatterbox.models.s3gen import S3GEN_SR

class HFOrpheusDataset(Dataset):
    def __init__(self, hf_dataset, tokenizer, s3_sr=S3_SR, s3gen_sr=S3GEN_SR, max_audio_length=20.0, max_text_length=1000):
        """
        Dataset wrapper for Orpheus LATAM dataset from HuggingFace.
        
        Args:
            hf_dataset: HuggingFace dataset object.
            tokenizer: Tokenizer for text processing (not strictly used in __getitem__ but passed for consistency).
            s3_sr (int): Sample rate for S3 (16k).
            s3gen_sr (int): Sample rate for S3Gen (24k).
            max_audio_length (float): Maximum audio length in seconds.
            max_text_length (int): Maximum text length in characters.
        """
        self.dataset = hf_dataset
        self.tokenizer = tokenizer
        self.s3_sr = s3_sr
        self.s3gen_sr = s3gen_sr
        self.max_audio_length = max_audio_length
        self.max_text_length = max_text_length

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        item = self.dataset[idx]
        
        # Audio processing
        # HF datasets usually return audio as {'array': np.array, 'sampling_rate': int}
        audio_data = item['audio']
        audio_array = audio_data['array']
        orig_sr = audio_data['sampling_rate']
        
        # Convert to tensor
        if isinstance(audio_array, np.ndarray):
            audio_tensor = torch.from_numpy(audio_array).float()
        else:
            audio_tensor = torch.tensor(audio_array).float()
            
        # Ensure shape is (1, T) or (T,) -> we'll work with (1, T) for resampling consistency
        if audio_tensor.dim() == 1:
            audio_tensor = audio_tensor.unsqueeze(0)
            
        # Resample to 24k (S3GEN_SR) if needed
        if orig_sr != self.s3gen_sr:
            resampler = torchaudio.transforms.Resample(orig_sr, self.s3gen_sr)
            audio_tensor = resampler(audio_tensor)
            
        # Truncate or Pad to max length
        max_samples = int(self.max_audio_length * self.s3gen_sr)
        if audio_tensor.shape[-1] > max_samples:
            audio_tensor = audio_tensor[..., :max_samples]
        elif audio_tensor.shape[-1] < max_samples:
            pad_amount = max_samples - audio_tensor.shape[-1]
            audio_tensor = torch.nn.functional.pad(audio_tensor, (0, pad_amount), value=0.0)
            
        # Generate 16k version (S3_SR) for VoiceEncoder/S3 tokenizer
        resampler_16k = torchaudio.transforms.Resample(self.s3gen_sr, self.s3_sr)
        audio_16k = resampler_16k(audio_tensor)
        
        # Squeeze back to (T,) if that's what the collate expects (usually yes for 1D audio)
        audio_tensor = audio_tensor.squeeze(0)
        audio_16k = audio_16k.squeeze(0)
        
        # Text processing
        text = item.get('text', '')
        text = punc_norm(text)
        if len(text) > self.max_text_length:
            text = text[:self.max_text_length]
            
        # Metadata
        # Orpheus dataset specific fields
        nationality = item.get('nationality', 'unknown')
        speaker_id = item.get('speaker_id', 'unknown')
        # Use a string identifier for audio_path if real path is not available
        audio_path = item.get('path', f"orpheus_{idx}")

        return {
            "audio": audio_tensor,      # 24k
            "audio_16k": audio_16k,     # 16k
            "text": text,
            "audio_path": audio_path,
            "nationality": nationality,
            "speaker_id": speaker_id
        }
