"""
Convierte los archivos .pt del modelo a .safetensors
"""
import torch
from safetensors.torch import save_file
from pathlib import Path

MODEL_DIR = Path("checkpoints_lora/merged_model")

print("Convirtiendo archivos .pt a .safetensors...")

# Lista de archivos a convertir
files_to_convert = [
    ("ve.pt", "ve.safetensors"),
    ("t3_cfg.pt", "t3_cfg.safetensors"),
    ("s3gen.pt", "s3gen.safetensors"),
]

for pt_file, safetensors_file in files_to_convert:
    pt_path = MODEL_DIR / pt_file
    safetensors_path = MODEL_DIR / safetensors_file
    
    if not pt_path.exists():
        print(f"⚠️  {pt_file} no encontrado, saltando...")
        continue
    
    print(f"Convirtiendo {pt_file} -> {safetensors_file}...")
    
    # Cargar el state_dict
    state_dict = torch.load(pt_path, map_location="cpu")
    
    # Guardar como safetensors
    save_file(state_dict, safetensors_path)
    
    print(f"✅ {safetensors_file} creado ({safetensors_path.stat().st_size / 1024 / 1024:.2f} MB)")

print("\n✅ Conversión completada!")
print(f"Archivos en: {MODEL_DIR}")
