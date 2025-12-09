import torch
import os
import argparse
from chatterbox.tts import ChatterboxTTS
from typing import Optional, Tuple, List, Dict

class LlamaWrapper(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model
        
    def forward(
        self,
        inputs_embeds: torch.Tensor,
        attention_mask: torch.Tensor,
        *past_key_values
    ):
        # Reconstruct past_key_values tuple of tuples
        # Input is a flat list of (key, value) tensors
        # Structure: ((k0, v0), (k1, v1), ...)
        num_layers = len(past_key_values) // 2
        pkv = []
        for i in range(num_layers):
            pkv.append((past_key_values[2*i], past_key_values[2*i+1]))
        pkv = tuple(pkv)
        
        outputs = self.model(
            inputs_embeds=inputs_embeds,
            attention_mask=attention_mask,
            past_key_values=pkv,
            use_cache=True,
            return_dict=True
        )
        
        logits = outputs.logits
        present = outputs.past_key_values
        
        # Flatten present_key_values for ONNX output
        present_flat = []
        for layer_pkv in present:
            present_flat.append(layer_pkv[0]) # key
            present_flat.append(layer_pkv[1]) # value
            
        return (logits,) + tuple(present_flat)

def export_llm(model_path, output_path, device="cpu"):
    print(f"Loading model from {model_path}...")
    # Load the full Chatterbox model
    # We use from_local if it's a directory, else from_pretrained
    if os.path.isdir(model_path):
        model = ChatterboxTTS.from_local(ckpt_dir=model_path, device=device)
    else:
        model = ChatterboxTTS.from_pretrained(device=device)
        
    # Extract the Llama backbone
    # Based on lora_es_latam.py, it's at model.t3.tfmr
    llama_model = model.t3.tfmr
    llama_model.eval()
    
    wrapper = LlamaWrapper(llama_model)
    
    # Dummy inputs
    batch_size = 1
    seq_len = 1
    hidden_size = llama_model.config.hidden_size
    num_heads = llama_model.config.num_key_value_heads
    head_dim = llama_model.config.hidden_size // llama_model.config.num_attention_heads # Approximation
    # Better to get head_dim from config if available
    if hasattr(llama_model.config, "head_dim"):
        head_dim = llama_model.config.head_dim
    
    print(f"Config: Hidden={hidden_size}, Heads={num_heads}, HeadDim={head_dim}")
    
    inputs_embeds = torch.randn(batch_size, seq_len, hidden_size, device=device)
    attention_mask = torch.ones(batch_size, seq_len, dtype=torch.long, device=device)
    
    # Create dummy past_key_values
    num_layers = llama_model.config.num_hidden_layers
    past_key_values = []
    input_names = ["inputs_embeds", "attention_mask"]
    output_names = ["logits"]
    dynamic_axes = {
        "inputs_embeds": {0: "batch_size", 1: "sequence_length"},
        "attention_mask": {0: "batch_size", 1: "total_sequence_length"},
        "logits": {0: "batch_size", 1: "sequence_length"},
    }
    
    for i in range(num_layers):
        # Key: [batch, num_heads, seq_len, head_dim]
        k = torch.randn(batch_size, num_heads, 0, head_dim, device=device)
        v = torch.randn(batch_size, num_heads, 0, head_dim, device=device)
        past_key_values.extend([k, v])
        
        input_names.extend([f"past_key_values.{i}.key", f"past_key_values.{i}.value"])
        output_names.extend([f"present_key_values.{i}.key", f"present_key_values.{i}.value"])
        
        dynamic_axes[f"past_key_values.{i}.key"] = {0: "batch_size", 2: "past_sequence_length"}
        dynamic_axes[f"past_key_values.{i}.value"] = {0: "batch_size", 2: "past_sequence_length"}
        dynamic_axes[f"present_key_values.{i}.key"] = {0: "batch_size", 2: "total_sequence_length"}
        dynamic_axes[f"present_key_values.{i}.value"] = {0: "batch_size", 2: "total_sequence_length"}

    print("Exporting to ONNX...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    torch.onnx.export(
        wrapper,
        (inputs_embeds, attention_mask, *past_key_values),
        output_path,
        input_names=input_names,
        output_names=output_names,
        dynamic_axes=dynamic_axes,
        opset_version=17,
        export_params=True,
        do_constant_folding=True
    )
    print(f"✅ LLM exported to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True, help="Path to merged model")
    parser.add_argument("--output", type=str, required=True, help="Output ONNX file")
    args = parser.parse_args()
    
    export_llm(args.model, args.output)
