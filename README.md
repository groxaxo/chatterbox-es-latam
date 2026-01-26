# Chatterbox ES-LATAM

<div align="center">

![Chatterbox ES-LATAM Banner](https://img.shields.io/badge/Chatterbox-ES--LATAM-orange?style=for-the-badge&logo=google-assistant&logoColor=white)

**Sistema de Síntesis de Voz (TTS) para Español Latinoamericano**

*Servidor TTS avanzado con API compatible OpenAI, interfaz web moderna y voces expresivas*

*Optimizado para aplicaciones de Comunicación Aumentativa Alternativa (AAC)*

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?style=flat-square)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg?style=flat-square)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-CUDA_12.1-blue.svg?style=flat-square)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

</div>

---

## 🎯 Características Principales

✨ **TTS de Alta Calidad**: Síntesis de voz natural y expresiva optimizada para español latinoamericano

🎙️ **Clonación de Voz**: Genera audio con voces personalizadas usando muestras de referencia

⚡ **Rendimiento GPU**: Soporte completo para CUDA (NVIDIA) con aceleración por GPU

🌐 **API Compatible OpenAI**: Endpoint `/v1/audio/speech` compatible con la API de OpenAI

🎨 **Interfaz Web Moderna**: UI intuitiva en español con controles avanzados

📝 **Textos Largos**: Procesamiento inteligente de textos extensos con chunking automático

🎚️ **Control Fino**: Ajusta temperatura, expresividad, velocidad y más parámetros

## 🚀 Quick Start

### Opción 1: Docker (Recomendado)

```bash
# Con soporte CUDA (GPU NVIDIA)
docker build -t chatterbox-es-latam .
docker run --gpus all -p 8004:8004 chatterbox-es-latam

# CPU solamente
docker build --build-arg RUNTIME=cpu -t chatterbox-es-latam .
docker run -p 8004:8004 chatterbox-es-latam
```

Abre tu navegador en `http://localhost:8004`

### Opción 2: Instalación Local

```bash
# 1. Clonar repositorio
git clone https://github.com/groxaxo/chatterbox-es-latam.git
cd chatterbox-es-latam

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
# Para CPU:
pip install -r requirements.txt

# Para GPU (NVIDIA CUDA):
pip install -r requirements-nvidia.txt

# 4. Iniciar servidor TTS
python server.py
```

El servidor se iniciará en `http://localhost:8004` y abrirá automáticamente tu navegador.

## 📖 Uso del Servidor TTS

### Interfaz Web

1. Abre `http://localhost:8004` en tu navegador
2. Escribe el texto que deseas sintetizar
3. Selecciona una voz predefinida o sube audio de referencia
4. Ajusta los parámetros de generación (opcional)
5. Haz clic en "Generar Audio"
6. Descarga o reproduce el audio generado

### API REST

#### OpenAI-Compatible Endpoint

```bash
curl -X POST http://localhost:8004/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "chatterbox-es-latam",
    "input": "Hola, bienvenido al sistema de síntesis de voz.",
    "voice": "default.wav",
    "response_format": "mp3",
    "speed": 1.0
  }' \
  --output audio.mp3
```

#### Custom TTS Endpoint

```bash
curl -X POST http://localhost:8004/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Este es un ejemplo de síntesis de voz en español latinoamericano.",
    "voice_mode": "predefined",
    "predefined_voice_id": "default.wav",
    "temperature": 0.8,
    "exaggeration": 1.0,
    "cfg_weight": 0.5,
    "speed_factor": 1.0,
    "output_format": "wav",
    "language": "es"
  }' \
  --output audio.wav
```

## 🎛️ Parámetros de Generación

| Parámetro | Rango | Por Defecto | Descripción |
|-----------|-------|-------------|-------------|
| `temperature` | 0.0 - 1.5 | 0.8 | Controla aleatoriedad (menor = más estable) |
| `exaggeration` | 0.25 - 2.0 | 1.0 | Expresividad/dramatización de la voz |
| `cfg_weight` | 0.2 - 1.0 | 0.5 | Peso de guía (influencia en estilo) |
| `speed_factor` | 0.25 - 4.0 | 1.0 | Velocidad del audio (1.0 = normal) |
| `seed` | ≥ 0 | 0 | Semilla para reproducibilidad (0 = aleatorio) |

## 📋 Requisitos

### Servidor
- Python 3.10+
- CUDA 12.1+ (para GPU)
- 8GB+ VRAM

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver [LICENSE](LICENSE) para detalles.

## 🙏 Agradecimientos

- [Resemble AI](https://github.com/resemble-ai/chatterbox) por Chatterbox TTS

