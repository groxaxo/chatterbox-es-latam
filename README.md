# Chatterbox ES-LATAM

<div align="center">

**Sistema de Síntesis de Voz (TTS) para Español Latinoamericano**

*Servidor TTS avanzado con API compatible OpenAI e interfaz web moderna*

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-CUDA_12.1-blue.svg)](https://www.docker.com/)

</div>

---

## 🎯 Características

- ✨ **TTS de Alta Calidad**: Síntesis de voz natural optimizada para español latinoamericano
- 🎙️ **Clonación de Voz**: Genera audio con voces personalizadas usando muestras de referencia  
- ⚡ **Rendimiento GPU**: Soporte completo para CUDA (NVIDIA)
- 🌐 **API Compatible OpenAI**: Endpoint `/v1/audio/speech` compatible con OpenAI
- 🎨 **Interfaz Web**: UI intuitiva en español con controles avanzados
- 📝 **Textos Largos**: Procesamiento inteligente con chunking automático

---

## 🚀 Quick Start

### Docker (Recomendado)

```bash
# GPU
docker-compose up -d

# CPU only
docker build --build-arg RUNTIME=cpu -t chatterbox-es-latam .
docker run -p 8004:8004 chatterbox-es-latam
```

Abre `http://localhost:8004` en tu navegador.

### Instalación Local

```bash
# 1. Clonar
git clone https://github.com/tu-usuario/chatterbox-es-latam.git
cd chatterbox-es-latam

# 2. Entorno virtual
python -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements-nvidia.txt  # GPU
# o
pip install -r requirements.txt         # CPU

# 4. Iniciar
python server.py
```

---

## 🎛️ Uso

### Interfaz Web

1. Abre `http://localhost:8004`
2. Escribe el texto a sintetizar
3. Selecciona una voz predefinida o sube audio de referencia
4. Ajusta parámetros y haz clic en "Generar Audio"

### API REST

#### OpenAI-Compatible

```bash
curl -X POST http://localhost:8004/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "chatterbox-es-latam",
    "input": "Hola, bienvenido al sistema TTS.",
    "voice": "default.wav",
    "response_format": "mp3",
    "speed": 1.0
  }' \
  --output audio.mp3
```

#### Custom Endpoint

```bash
curl -X POST http://localhost:8004/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Texto a sintetizar en español latinoamericano.",
    "voice_mode": "predefined",
    "predefined_voice_id": "default.wav",
    "temperature": 0.8,
    "exaggeration": 1.0,
    "cfg_weight": 0.5,
    "speed_factor": 1.0,
    "output_format": "wav",
    "split_text": true,
    "chunk_size": 120,
    "language": "es"
  }' \
  --output audio.wav
```

---

## 📋 API Reference

### Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/v1/audio/speech` | POST | Generar audio (OpenAI-compatible) |
| `/tts` | POST | Generar audio (custom) |
| `/v1/audio/voices` | GET | Listar voces disponibles |
| `/v1/voices` | GET | Alias para `/v1/audio/voices` |
| `/v1/audio/models` | GET | Listar modelos disponibles |
| `/v1/models` | GET | Alias para `/v1/audio/models` |

### Parámetros de Generación

| Parámetro | Rango | Default | Descripción |
|-----------|-------|---------|-------------|
| `temperature` | 0.0 - 1.5 | 0.8 | Aleatoriedad (menor = más estable) |
| `exaggeration` | 0.25 - 2.0 | 1.0 | Expresividad de la voz |
| `cfg_weight` | 0.2 - 1.0 | 0.5 | Influencia en estilo |
| `speed_factor` | 0.25 - 4.0 | 1.0 | Velocidad del audio |
| `seed` | ≥ 0 | 0 | Semilla para reproducibilidad |
| `split_text` | boolean | true | Dividir texto largo automáticamente |
| `chunk_size` | 50 - 500 | 120 | Tamaño de chunk para división de texto |
| `language` | string | "es" | Idioma del texto |

---

## 🏗️ Arquitectura

```
┌─────────────────┐         ┌────────────────────────────────┐
│   CLIENTE       │         │   SERVIDOR (GPU NVIDIA)        │
│   (Navegador)   │         │                                │
│                 │  HTTP   │  ┌──────────────────────────┐  │
│  Envía texto   │────────►│  │  TTS Pipeline            │  │
│                 │         │  │  1. Recibe texto         │  │
│  Recibe audio  │◄────────│  │  2. Carga modelo         │  │
│                 │  WAV    │  │  3. Genera audio (GPU)   │  │
└─────────────────┘         │  │  4. Retorna audio        │  │
                            │  └──────────────────────────┘  │
                            └────────────────────────────────┘
```

**Stack**:
- FastAPI (Python)
- PyTorch + Chatterbox TTS
- CUDA para GPU

---

## 💻 Requisitos

### Hardware

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| GPU | RTX 3060 12GB | RTX 4090 / A100 |
| RAM | 16GB | 32GB |
| CPU | 4 cores | 8+ cores |
| Storage | 10GB | 50GB+ |

### Software

```
Docker 24.0+
NVIDIA Container Toolkit
CUDA 12.1+
Python 3.10+ (para desarrollo)
```

### Performance (RTX 4090)

| Texto | Latencia |
|-------|----------|
| Corto (~10 palabras) | ~200ms |
| Medio (~50 palabras) | ~800ms |
| Largo (~200 palabras) | ~3s |

---

## 📁 Estructura

```
chatterbox-es-latam/
├── server.py              # Servidor FastAPI principal
├── engine.py              # Motor de inferencia
├── config.yaml            # Configuración
├── requirements.txt       # Dependencias CPU
├── requirements-nvidia.txt # Dependencias GPU
├── docker-compose.yml     # Docker Compose
├── Dockerfile             # Docker build
├── voices/                # Voces predefinidas
├── reference_audio/       # Audios de referencia
├── outputs/               # Audios generados
├── logs/                  # Logs del servidor
├── ui/                    # Interfaz web
├── web/                   # React UI (desarrollo)
└── training/              # Scripts de fine-tuning
```

---

## 🐳 Deployment

### Opciones

| Opción | Uso | GPU | Costo |
|--------|-----|-----|-------|
| **Local/Docker** | Desarrollo | Opcional | Gratis |
| **RunPod** | Producción | ✅ | ~$0.20/hr |
| **AWS/GCP** | Enterprise | ✅ | Variable |

### Docker Compose

```yaml
services:
  chatterbox-tts:
    build: .
    ports:
      - "8004:8004"
    volumes:
      - ./voices:/app/voices
      - ./reference_audio:/app/reference_audio
      - ./outputs:/app/outputs
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### RunPod

1. Crear Pod con template PyTorch + CUDA 12.1
2. GPU: RTX 3090 o superior
3. Clonar repo e instalar: `pip install -r requirements-nvidia.txt`
4. Ejecutar: `python server.py`

---

## 🔒 Seguridad

- HTTPS recomendado para producción
- Rate limiting en endpoints
- Validación de inputs
- Audio temporal (no se almacena permanentemente)

---

## 🙏 Agradecimientos

- [Resemble AI](https://github.com/resemble-ai/chatterbox) por Chatterbox TTS

---

## 📝 Licencia

MIT License
