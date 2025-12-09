# Training Guide

Esta guía explica cómo fine-tunear el modelo Chatterbox con LoRA para voces en español latinoamericano.

## Visión General

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRAINING PIPELINE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Dataset           LoRA             Merged           Deploy    │
│   ┌───────┐        ┌───────┐        ┌───────┐        ┌───────┐ │
│   │ Audio │───────►│ Train │───────►│ Merge │───────►│ Server│ │
│   │ LATAM │        │ LoRA  │        │Weights│        │       │ │
│   └───────┘        └───────┘        └───────┘        └───────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Requisitos

### Hardware
- GPU con 12GB+ VRAM (RTX 3090, A4000, etc.)
- 32GB+ RAM sistema
- 100GB+ almacenamiento

### Software
- Python 3.10+
- CUDA 11.8+
- PyTorch 2.1+

## Preparación del Dataset

### Formato Requerido

```
dataset/
├── metadata.json
├── audio/
│   ├── 001.wav
│   ├── 002.wav
│   └── ...
```

### metadata.json

```json
[
  {
    "audio_path": "audio/001.wav",
    "text": "Hola, esto es una prueba de audio.",
    "speaker_id": "speaker_01",
    "language": "es-419"
  },
  {
    "audio_path": "audio/002.wav",
    "text": "Buenos días, ¿cómo estás?",
    "speaker_id": "speaker_01",
    "language": "es-419"
  }
]
```

### Requisitos de Audio

| Parámetro | Valor |
|-----------|-------|
| Formato | WAV (PCM) |
| Sample Rate | 24000 Hz |
| Canales | Mono |
| Duración | 1-20 segundos |
| Calidad | Sin ruido, clara |

### Preparar Audio

```bash
# Convertir a formato correcto
ffmpeg -i input.mp3 -ar 24000 -ac 1 output.wav

# Procesar múltiples archivos
for f in *.mp3; do
  ffmpeg -i "$f" -ar 24000 -ac 1 "${f%.mp3}.wav"
done
```

## Configuración de Training

### Parámetros en `lora_es_latam.py`

```python
# Hiperparámetros principales
BATCH_SIZE = 2
EPOCHS = 10
LEARNING_RATE = 2e-5
WARMUP_STEPS = 500

# LoRA específico
LORA_RANK = 32
LORA_ALPHA = 64
LORA_DROPOUT = 0.05

# Gradient accumulation (para GPUs con poca memoria)
GRADIENT_ACCUMULATION_STEPS = 16

# Checkpoints
SAVE_EVERY_N_STEPS = 200
CHECKPOINT_DIR = "checkpoints_lora"
```

### Ajustes según GPU

| GPU | VRAM | Batch Size | Grad Accum |
|-----|------|------------|------------|
| RTX 3090 | 24GB | 4 | 8 |
| RTX 4090 | 24GB | 4 | 8 |
| A4000 | 16GB | 2 | 16 |
| RTX 3080 | 10GB | 1 | 32 |

## Ejecutar Training

### Local

```bash
# Activar entorno
source venv/bin/activate

# Ejecutar training
cd training
python lora_es_latam.py
```

### RunPod

```bash
# Usar script de RunPod
./runpod_train.sh
```

Contenido de `runpod_train.sh`:

```bash
#!/bin/bash
cd /workspace/chatterbox-es-latam/training

# Configurar variables
export CUDA_VISIBLE_DEVICES=0

# Ejecutar con logging
python lora_es_latam.py 2>&1 | tee training_$(date +%Y%m%d_%H%M%S).log
```

## Monitorear Training

### Métricas

El script genera `training_metrics.png` con:
- Loss de training
- Learning rate
- Gradient norms

### Logs

```bash
# Ver progreso
tail -f training_*.log

# Buscar errores
grep -i error training_*.log
```

### Checkpoints

Los checkpoints se guardan en:

```
checkpoints_lora/
├── checkpoint_step_200/
├── checkpoint_step_400/
├── best_model/
└── final_model/
```

## Post-Training

### Merge LoRA Weights

Después del training, merge los weights LoRA con el modelo base:

```bash
python training/create_merged_model.py \
  --base_model "resemble-ai/chatterbox" \
  --lora_path "checkpoints_lora/best_model" \
  --output_path "checkpoints_lora/merged_model"
```

### Verificar Modelo

```bash
# Test rápido de inferencia
python training/test_inference.py \
  --model "checkpoints_lora/merged_model" \
  --text "Hola, esto es una prueba" \
  --output "test_output.wav"
```

### Subir a HuggingFace (Opcional)

```bash
python upload_to_hf.py \
  --model_path "checkpoints_lora/merged_model" \
  --repo_id "tu-usuario/chatterbox-es-latam"
```

## Troubleshooting

### CUDA Out of Memory

```python
# Reducir batch size
BATCH_SIZE = 1

# Aumentar gradient accumulation
GRADIENT_ACCUMULATION_STEPS = 32

# Usar mixed precision (ya habilitado por defecto)
```

### Loss no decrece

1. Verificar learning rate (probar 1e-5 o 5e-5)
2. Verificar calidad del dataset
3. Aumentar epochs

### Audio de salida con ruido

1. Verificar calidad del dataset de entrada
2. Reducir temperature en inferencia
3. Aumentar repetition_penalty

## Datasets Recomendados

### Públicos

| Dataset | Idioma | Horas | Link |
|---------|--------|-------|------|
| Common Voice | es-419 | ~100h | mozilla.org |
| LibriVox | es | Variable | librivox.org |
| VoxPopuli | es | ~100h | github |

### Custom

Para mejores resultados, grabar dataset custom con:
- Múltiples hablantes LATAM
- Variedad de acentos (AR, MX, CO, etc.)
- Textos variados (frases AAC comunes)

## Métricas de Éxito

| Métrica | Target |
|---------|--------|
| Training Loss | < 0.5 |
| Validation Loss | < 0.6 |
| MOS (Mean Opinion Score) | > 3.5/5 |
| Intelligibility | > 90% |
