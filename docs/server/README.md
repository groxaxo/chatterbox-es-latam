# Servidor de Enrollment

El servidor procesa audio de usuarios y genera "Voice IDs" optimizados para inferencia local en tablets.

## Stack Tecnológico

- **Framework**: FastAPI (Python 3.10+)
- **ML**: PyTorch + Chatterbox TTS
- **GPU**: CUDA 11.8+
- **Audio**: librosa, soundfile

## Estructura

```
server/
├── api/
│   └── v1/
│       └── endpoints.py      # Rutas de la API
├── core/
│   └── config.py             # Configuración
├── schemas/
│   └── enrollment.py         # Pydantic models
├── services/
│   ├── audio_processor.py    # Procesamiento de audio
│   ├── inference_service.py  # Inferencia TTS
│   ├── storage_service.py    # Almacenamiento
│   └── voice_encoder.py      # Encoding de voz
├── data/
│   ├── audio_input/          # Audios de referencia
│   └── audio_output/         # Audios generados
├── main.py                   # Entry point
└── enroll.py                 # CLI de enrollment
```

## Quick Start

### Requisitos
- Python 3.10+
- CUDA 11.8+ (GPU)
- 8GB+ VRAM

### Instalación

```bash
# Desde la raíz del proyecto
cd server

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r ../requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores
```

### Ejecución

```bash
# Desarrollo
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Producción
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
```

## Configuración

Variables de entorno (`.env`):

```env
# Servidor
PROJECT_NAME="Chatterbox ES-LATAM API"
API_V1_STR="/api/v1"

# Modelo
MODEL_PATH="../checkpoints_lora/merged_model"
DEVICE="cuda"  # o "cpu"

# Audio
SAMPLE_RATE=24000
```

## Próximos Pasos

Ver documentación detallada:
- [API Reference](./API.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Training Guide](./TRAINING.md)
