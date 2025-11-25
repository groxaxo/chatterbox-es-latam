"""
Script para subir el modelo entrenado a HuggingFace Hub.
Uso: python upload_to_hf.py
"""
import os
from pathlib import Path
from huggingface_hub import HfApi, create_repo

# ============================================================================
# CONFIGURACIÓN - EDITÁ ESTOS VALORES
# ============================================================================
REPO_NAME = "franclarke/chatterbox-es-ar"  # Cambiá por tu usuario/nombre-repo
MODEL_DIR = "./checkpoints_lora/merged_model"
LORA_ADAPTER_PATH = "./checkpoints_lora/final_lora_adapter.pt"
PRIVATE = False  # True si querés que el repo sea privado

# ============================================================================

def main():
    print("=" * 60)
    print("Subiendo modelo a HuggingFace Hub")
    print("=" * 60)
    
    # Verificar que el modelo existe
    model_path = Path(MODEL_DIR)
    if not model_path.exists():
        print(f"❌ Error: No se encontró el modelo en {MODEL_DIR}")
        print("Asegurate de haber completado el entrenamiento primero.")
        return
    
    # Verificar login
    try:
        api = HfApi()
        user_info = api.whoami()
        print(f"✓ Logueado como: {user_info['name']}")
    except Exception as e:
        print("❌ Error: No estás logueado en HuggingFace.")
        print("Ejecutá: huggingface-cli login")
        return
    
    # Crear repositorio (si no existe)
    print(f"\n📦 Creando repositorio: {REPO_NAME}")
    try:
        create_repo(
            repo_id=REPO_NAME,
            repo_type="model",
            private=PRIVATE,
            exist_ok=True
        )
        print(f"✓ Repositorio creado/verificado")
    except Exception as e:
        print(f"⚠️  Advertencia al crear repo: {e}")
    
    # Subir modelo completo (merged_model)
    print(f"\n📤 Subiendo modelo desde {MODEL_DIR}...")
    try:
        api.upload_folder(
            folder_path=str(model_path),
            repo_id=REPO_NAME,
            repo_type="model",
            path_in_repo="merged_model",
        )
        print("✓ Modelo completo subido exitosamente")
    except Exception as e:
        print(f"❌ Error subiendo modelo: {e}")
        return
    
    # Subir adaptador LoRA (opcional, más liviano)
    lora_path = Path(LORA_ADAPTER_PATH)
    if lora_path.exists():
        print(f"\n📤 Subiendo adaptador LoRA desde {LORA_ADAPTER_PATH}...")
        try:
            api.upload_file(
                path_or_fileobj=str(lora_path),
                path_in_repo="lora_adapter/final_lora_adapter.pt",
                repo_id=REPO_NAME,
                repo_type="model",
            )
            print("✓ Adaptador LoRA subido exitosamente")
        except Exception as e:
            print(f"⚠️  Advertencia subiendo LoRA: {e}")
    
    # Crear README.md para el modelo en HF
    readme_content = f"""---
language:
- es
license: apache-2.0
tags:
- text-to-speech
- tts
- chatterbox
- lora
- spanish
- argentinian
datasets:
- GianDiego/latam-spanish-speech-orpheus-tts-24khz
---

# Chatterbox TTS - Español Rioplatense (LoRA Fine-tuned)

Este modelo es una versión fine-tuneada de [ResembleAI/chatterbox-multilingual](https://huggingface.co/ResembleAI/chatterbox-multilingual) usando LoRA para generar voz con acento argentino/rioplatense.

## Uso

```python
from chatterbox.tts import ChatterboxTTS

# Cargar modelo
model = ChatterboxTTS.from_pretrained("{REPO_NAME}")

# Generar audio
text = "Che, me voy al laburo en bondi."
wav = model.generate(text, lang="es")

# Guardar
import soundfile as sf
sf.write("output.wav", wav, 24000)
```

## Entrenamiento

- **Dataset:** [Orpheus LATAM (AR)](https://huggingface.co/datasets/GianDiego/latam-spanish-speech-orpheus-tts-24khz)
- **Método:** LoRA (Low-Rank Adaptation)
- **Código:** [github.com/franclarke/chatterbox-es-latam](https://github.com/franclarke/chatterbox-es-latam)

## Licencia

Apache 2.0
"""
    
    print("\n📝 Creando README.md...")
    try:
        api.upload_file(
            path_or_fileobj=readme_content.encode(),
            path_in_repo="README.md",
            repo_id=REPO_NAME,
            repo_type="model",
        )
        print("✓ README.md creado")
    except Exception as e:
        print(f"⚠️  Advertencia creando README: {e}")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("✅ ¡Subida completada!")
    print("=" * 60)
    print(f"🔗 Tu modelo está disponible en:")
    print(f"   https://huggingface.co/{REPO_NAME}")
    print("\n💡 Para descargarlo en otra máquina:")
    print(f"   model = ChatterboxTTS.from_pretrained('{REPO_NAME}')")
    print("=" * 60)

if __name__ == "__main__":
    main()
