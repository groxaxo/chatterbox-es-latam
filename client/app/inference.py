import onnxruntime
import numpy as np
import soundfile as sf
import argparse
import os
import json
from tqdm import tqdm

# Constants
S3GEN_SR = 24000
START_SPEECH_TOKEN = 6561
STOP_SPEECH_TOKEN = 6562

class RepetitionPenaltyLogitsProcessor:
    def __init__(self, penalty: float):
        self.penalty = penalty

    def __call__(self, input_ids: np.ndarray, scores: np.ndarray) -> np.ndarray:
        score = np.take_along_axis(scores, input_ids, axis=1)
        score = np.where(score < 0, score * self.penalty, score / self.penalty)
        scores_processed = scores.copy()
        np.put_along_axis(scores_processed, input_ids, score, axis=1)
        return scores_processed

def run_inference(
    text,
    voice_id_path,
    models_dir,
    output_path="output.wav",
    max_new_tokens=256,
    exaggeration=0.5
):
    print(f"Loading models from {models_dir}...")
    
    # Load Voice ID
    print(f"Loading Voice ID from {voice_id_path}...")
    voice_data = np.load(voice_id_path, allow_pickle=True).item()
    
    # Extract conditioning tensors
    cond_emb = voice_data['cond_emb']
    prompt_token = voice_data['prompt_token']
    speaker_embeddings = voice_data['speaker_embeddings']
    speaker_features = voice_data['speaker_features']
    
    # Load ONNX sessions
    embed_tokens_path = os.path.join(models_dir, "embed_tokens.onnx")
    language_model_path = os.path.join(models_dir, "language_model.onnx")
    conditional_decoder_path = os.path.join(models_dir, "conditional_decoder.onnx")
    
    embed_tokens_session = onnxruntime.InferenceSession(embed_tokens_path)
    llama_session = onnxruntime.InferenceSession(language_model_path)
    cond_decoder_session = onnxruntime.InferenceSession(conditional_decoder_path)
    
    # Tokenize text (Simple mapping for now, assuming character level or simple BPE)
    # TODO: We need the actual tokenizer. For now, let's assume the user provides tokens or we use a simple mock.
    # The original script used AutoTokenizer.from_pretrained(model_id).
    # We should probably export the tokenizer or use the same one.
    # For this implementation, I'll assume we can use the same tokenizer logic if we had the library.
    # Since we are in a "client" folder, we might not have 'transformers'. 
    # But for now, let's assume we do or we need to implement a simple text->id mapping.
    
    # For the sake of this demo, I will try to import AutoTokenizer, if fails, warn user.
    try:
        from transformers import AutoTokenizer
        # Use a standard tokenizer or the one from the repo
        tokenizer = AutoTokenizer.from_pretrained("vladislavbro/llama_backbone_0.5") # Or local path
        input_ids = tokenizer(text, return_tensors="np")["input_ids"].astype(np.int64)
    except Exception as e:
        print(f"Warning: Could not load tokenizer: {e}")
        print("Using dummy input_ids for testing.")
        input_ids = np.array([[1, 2, 3]], dtype=np.int64)

    position_ids = np.where(
        input_ids >= START_SPEECH_TOKEN,
        0,
        np.arange(input_ids.shape[1])[np.newaxis, :] - 1
    )

    # Embed text
    ort_embed_tokens_inputs = {
        "input_ids": input_ids,
        "position_ids": position_ids,
        "exaggeration": np.array([exaggeration], dtype=np.float32)
    }
    
    text_embeds = embed_tokens_session.run(None, ort_embed_tokens_inputs)[0]
    
    # Concatenate with voice conditioning
    # cond_emb shape: [1, len, dim]
    # text_embeds shape: [1, len, dim]
    inputs_embeds = np.concatenate((cond_emb, text_embeds), axis=1)
    
    # Prepare LLM inputs
    batch_size, seq_len, _ = inputs_embeds.shape
    num_hidden_layers = 30 # Llama config
    num_key_value_heads = 16
    head_dim = 64
    
    past_key_values = {
        f"past_key_values.{layer}.{kv}": np.zeros([batch_size, num_key_value_heads, 0, head_dim], dtype=np.float32)
        for layer in range(num_hidden_layers)
        for kv in ("key", "value")
    }
    attention_mask = np.ones((batch_size, seq_len), dtype=np.int64)
    
    generate_tokens = np.array([[START_SPEECH_TOKEN]], dtype=np.int64)
    repetition_penalty_processor = RepetitionPenaltyLogitsProcessor(penalty=1.2)
    
    print("Generating speech tokens...")
    for i in tqdm(range(max_new_tokens)):
        # Run LLM
        ort_inputs = {
            "inputs_embeds": inputs_embeds,
            "attention_mask": attention_mask,
            **past_key_values
        }
        
        outputs = llama_session.run(None, ort_inputs)
        logits = outputs[0]
        present_key_values_list = outputs[1:]
        
        # Update past_key_values
        for j, key in enumerate(past_key_values):
            past_key_values[key] = present_key_values_list[j]
            
        # Sample next token
        next_token_logits = logits[:, -1, :]
        next_token_logits = repetition_penalty_processor(generate_tokens, next_token_logits)
        next_token = np.argmax(next_token_logits, axis=-1, keepdims=True).astype(np.int64)
        
        generate_tokens = np.concatenate((generate_tokens, next_token), axis=-1)
        
        if (next_token.flatten() == STOP_SPEECH_TOKEN).all():
            break
            
        # Prepare next input
        position_ids = np.full((batch_size, 1), i + 1, dtype=np.int64)
        ort_embed_tokens_inputs["input_ids"] = next_token
        ort_embed_tokens_inputs["position_ids"] = position_ids
        
        inputs_embeds = embed_tokens_session.run(None, ort_embed_tokens_inputs)[0]
        attention_mask = np.concatenate([attention_mask, np.ones((batch_size, 1), dtype=np.int64)], axis=1)

    # Decode to Audio
    print("Decoding to audio...")
    speech_tokens = generate_tokens[:, 1:-1] # Remove start/stop
    # Prepend prompt tokens if needed (the model might expect them)
    # The inference script did: speech_tokens = np.concatenate([prompt_token, speech_tokens], axis=1)
    speech_tokens = np.concatenate([prompt_token, speech_tokens], axis=1)
    
    cond_input = {
        "speech_tokens": speech_tokens,
        "speaker_embeddings": speaker_embeddings,
        "speaker_features": speaker_features,
    }
    
    wav = cond_decoder_session.run(None, cond_input)[0]
    wav = np.squeeze(wav, axis=0)
    
    sf.write(output_path, wav, S3GEN_SR)
    print(f"✅ Audio saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=str, required=True)
    parser.add_argument("--voice", type=str, required=True, help="Path to voice_id.npy")
    parser.add_argument("--models", type=str, required=True, help="Directory containing ONNX models")
    parser.add_argument("--output", type=str, default="output.wav")
    args = parser.parse_args()
    
    run_inference(args.text, args.voice, args.models, args.output)
