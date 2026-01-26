# Guía de Inicio Rápido - Chatterbox ES-LATAM TTS Server

## 🚀 Inicio Rápido en 5 Minutos

### Opción 1: Docker Compose (Más fácil)

```bash
# 1. Clonar el repositorio
git clone https://github.com/groxaxo/chatterbox-es-latam.git
cd chatterbox-es-latam

# 2. Iniciar con Docker Compose
docker-compose up -d

# 3. Ver logs
docker-compose logs -f

# 4. Abrir en el navegador
# http://localhost:8004
```

¡Listo! El servidor está corriendo.

### Opción 2: Docker Manual

```bash
# GPU (recomendado)
docker build -t chatterbox-es-latam .
docker run --gpus all -p 8004:8004 chatterbox-es-latam

# CPU
docker build --build-arg RUNTIME=cpu -t chatterbox-es-latam .
docker run -p 8004:8004 chatterbox-es-latam
```

### Opción 3: Instalación Local

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt  # CPU
# o
pip install -r requirements-nvidia.txt  # GPU

# 3. Iniciar servidor
python server.py
```

## 🎯 Primeros Pasos

### 1. Verificar que el servidor funciona

```bash
curl http://localhost:8004/health
```

Debería responder:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cuda"
}
```

### 2. Generar tu primer audio

#### Usando la interfaz web:
1. Abre http://localhost:8004
2. Escribe: "Hola, este es mi primer audio con Chatterbox ES-LATAM"
3. Click en "Generar Audio"
4. ¡Escucha y descarga!

#### Usando la API:
```bash
curl -X POST http://localhost:8004/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "chatterbox-es-latam",
    "input": "Hola, este es mi primer audio con Chatterbox ES-LATAM",
    "voice": "default.wav",
    "response_format": "mp3"
  }' \
  --output primer_audio.mp3
```

### 3. Experimentar con parámetros

```bash
curl -X POST http://localhost:8004/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Probando diferentes voces y estilos",
    "voice_mode": "predefined",
    "predefined_voice_id": "default.wav",
    "temperature": 0.5,
    "exaggeration": 1.5,
    "speed_factor": 1.2,
    "output_format": "wav"
  }' \
  --output experimento.wav
```

## 📋 Casos de Uso Comunes

### Audiobooks / Narración

```python
import requests

text = """
Capítulo 1: El Comienzo

Era una mañana soleada cuando todo comenzó.
Los pájaros cantaban y el viento soplaba suavemente.
"""

response = requests.post(
    "http://localhost:8004/tts",
    json={
        "text": text,
        "voice_mode": "predefined",
        "predefined_voice_id": "default.wav",
        "temperature": 0.6,  # Más estable para narración
        "exaggeration": 0.8,  # Menos dramático
        "speed_factor": 0.9,  # Ligeramente más lento
        "output_format": "mp3"
    }
)

with open("capitulo1.mp3", "wb") as f:
    f.write(response.content)
```

### Asistente Virtual

```python
def speak(text):
    """Función simple para TTS en un asistente"""
    response = requests.post(
        "http://localhost:8004/v1/audio/speech",
        json={
            "model": "chatterbox-es-latam",
            "input": text,
            "voice": "default.wav",
            "speed": 1.2  # Más rápido para respuestas
        }
    )
    # Reproducir audio...
    return response.content

# Uso
speak("Hola, soy tu asistente virtual. ¿En qué puedo ayudarte?")
```

### Contenido Educativo

```python
# Generar explicaciones con diferentes énfasis
lesson = """
Hoy aprenderemos sobre la fotosíntesis.
La fotosíntesis es el proceso por el cual las plantas
convierten la luz solar en energía.
"""

response = requests.post(
    "http://localhost:8004/tts",
    json={
        "text": lesson,
        "voice_mode": "predefined",
        "predefined_voice_id": "default.wav",
        "temperature": 0.7,
        "exaggeration": 1.2,  # Más expresivo para educación
        "speed_factor": 0.85,  # Más lento para claridad
        "output_format": "mp3"
    }
)
```

## ⚙️ Configuración Común

### Para voz más natural y estable:
```json
{
  "temperature": 0.5,
  "exaggeration": 0.8,
  "cfg_weight": 0.6,
  "speed_factor": 1.0
}
```

### Para voz más dramática/expresiva:
```json
{
  "temperature": 1.0,
  "exaggeration": 1.5,
  "cfg_weight": 0.4,
  "speed_factor": 0.95
}
```

### Para narración de audiolibros:
```json
{
  "temperature": 0.6,
  "exaggeration": 0.7,
  "cfg_weight": 0.5,
  "speed_factor": 0.9
}
```

## 🔧 Administración

### Ver logs
```bash
# Docker
docker-compose logs -f

# Local
tail -f logs/tts_server.log
```

### Detener servidor
```bash
# Docker Compose
docker-compose down

# Docker
docker stop chatterbox-tts-server

# Local
Ctrl+C
```

### Actualizar
```bash
# Docker Compose
git pull
docker-compose down
docker-compose build
docker-compose up -d

# Local
git pull
pip install -r requirements.txt --upgrade
python server.py
```

### Limpiar archivos generados
```bash
# Eliminar outputs antiguos
rm -rf outputs/*

# Eliminar logs antiguos
rm -rf logs/*

# Eliminar cache de modelos (se descargará de nuevo)
rm -rf model_cache/*
```

## 🐛 Solución de Problemas Rápida

### Servidor no responde
```bash
# 1. Verificar si está corriendo
curl http://localhost:8004/health

# 2. Ver logs para errores
tail -f logs/tts_server.log

# 3. Reiniciar
docker-compose restart  # o python server.py
```

### Modelo no carga
```bash
# Verificar CUDA (si usas GPU)
python -c "import torch; print(torch.cuda.is_available())"

# Cambiar a CPU en config.yaml
device: cpu
```

### Puerto en uso
```bash
# Cambiar puerto en config.yaml
port: 8005  # o cualquier puerto disponible
```

## 📚 Siguiente Paso

Lee la [documentación completa](docs/TTS_SERVER.md) para:
- API reference detallada
- Agregar voces personalizadas
- Configuración avanzada
- Integración con otras aplicaciones
- Deployment en producción

## 🎓 Ejemplos Adicionales

Ver el directorio `examples/` para:
- Script Python completo
- Integración con Discord bot
- API client en JavaScript
- Batch processing de textos

## 💡 Tips

1. **Rendimiento**: Usa GPU para mejor velocidad
2. **Calidad**: Temperatura baja = más consistente
3. **Velocidad**: Ajusta `speed_factor` post-generación
4. **Textos largos**: El sistema divide automáticamente
5. **Reproducibilidad**: Usa `seed` distinto de 0

¡Disfruta sintetizando voz en español LATAM! 🎉
