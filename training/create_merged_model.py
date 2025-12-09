#!/usr/bin/env python3
"""
Script para crear el modelo mergeado a partir del checkpoint final.
Ejecutá esto si el entrenamiento se completó pero falló al crear el merged_model.
"""
import torch
from pathlib import Path
from chatterbox.tts import ChatterboxTTS
from huggingface_hub import hf_hub_download
import shutil

# Configuración
CHECKPOINT_DIR = "checkpoints_lora"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
LORA_RANK = 32
LORA_ALPHA = 64
LORA_DROPOUT = 0.05

print("=" * 60)
print("Creando modelo mergeado desde checkpoint...")
print("=" * 60)

# Cargar el adaptador LoRA
adapter_path = Path(CHECKPOINT_DIR) / "final_lora_adapter.pt"
if not adapter_path.exists():
    print(f"ERROR: No se encontró {adapter_path}")
    print("Asegurate de que el entrenamiento se haya completado.")
    exit(1)

print(f"Cargando adaptador LoRA desde {adapter_path}...")
adapter_dict = torch.load(adapter_path, map_location=DEVICE)
lora_config = adapter_dict['lora_config']
lora_weights = adapter_dict['lora_weights']

print(f"Configuración LoRA: rank={lora_config['rank']}, alpha={lora_config['alpha']}")

# Cargar modelo base
print("Cargando modelo base de Chatterbox...")
model = ChatterboxTTS.from_pretrained(device=DEVICE)

# Importar funciones necesarias del script de entrenamiento
import sys
sys.path.insert(0, str(Path(__file__).parent))
from lora_es_latam import inject_lora_layers, merge_lora_weights

# Inyectar capas LoRA
print("Inyectando capas LoRA...")
target_modules = lora_config['target_modules']
lora_layers = inject_lora_layers(
    model.t3.tfmr,
    target_modules,
    rank=lora_config['rank'],
    alpha=lora_config['alpha'],
    dropout=lora_config['dropout']
)

# Cargar pesos entrenados
print("Cargando pesos entrenados...")
for name, weights in lora_weights.items():
    if name in lora_layers:
        lora_layers[name].lora_A.data = weights['lora_A'].to(DEVICE)
        lora_layers[name].lora_B.data = weights['lora_B'].to(DEVICE)

# Mergear pesos
print("Mergeando pesos LoRA con el modelo base...")
model = merge_lora_weights(model, lora_layers)

# Guardar modelo mergeado
merged_dir = Path(CHECKPOINT_DIR) / "merged_model"
merged_dir.mkdir(parents=True, exist_ok=True)

print(f"Guardando modelo mergeado en {merged_dir}...")
torch.save(model.ve.state_dict(), merged_dir / "ve.pt")
torch.save(model.t3.state_dict(), merged_dir / "t3_cfg.pt")
torch.save(model.s3gen.state_dict(), merged_dir / "s3gen.pt")

# Copiar tokenizer
print("Copiando tokenizer...")
tokenizer_path = Path(hf_hub_download(repo_id="ResembleAI/chatterbox", filename="tokenizer.json"))
shutil.copy(tokenizer_path, merged_dir / "tokenizer.json")

# Guardar conditionals si existen
if model.conds:
    model.conds.save(merged_dir / "conds.pt")

print("=" * 60)
print("✅ ¡Modelo mergeado creado exitosamente!")
print("=" * 60)
print(f"Ubicación: {merged_dir}")
print("\nPara probar el modelo:")
print(f"  python src/test_inference.py")
print("\nPara subirlo a HuggingFace:")
print(f"  python upload_to_hf.py")
