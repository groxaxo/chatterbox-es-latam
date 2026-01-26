# Chatterbox ES-LATAM TTS Server - Guía Completa

## Tabla de Contenidos

- [Introducción](#introducción)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [API Reference](#api-reference)
- [Desarrollo](#desarrollo)
- [Troubleshooting](#troubleshooting)

## Introducción

Chatterbox ES-LATAM TTS Server es un servidor de síntesis de voz (Text-to-Speech) optimizado para español latinoamericano, basado en el modelo Chatterbox de Resemble AI.

### Características

- ✨ Síntesis de voz natural en español LATAM
- 🎙️ Clonación de voz con audio de referencia
- ⚡ Soporte GPU (CUDA) para rendimiento óptimo
- 🌐 API compatible con OpenAI
- 🎨 Interfaz web moderna en español
- 📝 Procesamiento de textos largos
- 🎚️ Control fino de parámetros

## Instalación

### Prerrequisitos

- Python 3.10 o superior
- (Opcional) GPU NVIDIA con CUDA 12.1+
- (Opcional) Docker

### Opción 1: Instalación con pip

```bash
# Clonar repositorio
git clone https://github.com/groxaxo/chatterbox-es-latam.git
cd chatterbox-es-latam

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

# Instalar dependencias
# Para CPU:
pip install -r requirements.txt

# Para GPU NVIDIA:
pip install -r requirements-nvidia.txt
```

### Opción 2: Docker

```bash
# Construir imagen (GPU)
docker build -t chatterbox-es-latam:cuda .

# Construir imagen (CPU)
docker build --build-arg RUNTIME=cpu -t chatterbox-es-latam:cpu .

# Ejecutar (GPU)
docker run --gpus all -p 8004:8004 chatterbox-es-latam:cuda

# Ejecutar (CPU)
docker run -p 8004:8004 chatterbox-es-latam:cpu
```

## Configuración

El servidor se configura mediante el archivo `config.yaml`:

```yaml
server:
  host: 0.0.0.0        # Dirección del servidor
  port: 8004           # Puerto
  
model:
  repo_id: chatterbox-es-latam  # Modelo a usar

tts_engine:
  device: auto         # auto, cuda, mps, o cpu
  
generation_defaults:
  temperature: 0.8     # Aleatoriedad (0.0-1.5)
  exaggeration: 1.0    # Expresividad (0.25-2.0)
  cfg_weight: 0.5      # Peso de guía (0.2-1.0)
  speed_factor: 1.0    # Velocidad (0.25-4.0)
  language: es         # Idioma
  
audio_output:
  format: wav          # wav, mp3, opus
  sample_rate: 24000   # Hz
```

### Variables de Entorno

- `HF_HOME`: Directorio para cache de Hugging Face
- `CUDA_VISIBLE_DEVICES`: GPU(s) a usar (ej. "0,1")

## Uso

### Iniciar el Servidor

```bash
# Método 1: Directamente con Python
python server.py

# Método 2: Con uvicorn
uvicorn server:app --host 0.0.0.0 --port 8004

# Método 3: Con uvicorn y reload (desarrollo)
uvicorn server:app --reload --port 8004
```

El servidor se iniciará en `http://localhost:8004`

### Interfaz Web

1. Abre `http://localhost:8004` en tu navegador
2. La interfaz se abrirá automáticamente al iniciar el servidor
3. Usa los controles para generar audio:
   - Ingresa texto
   - Selecciona modo de voz
   - Ajusta parámetros (opcional)
   - Genera y descarga

### Línea de Comandos

```bash
# Ejemplo básico
curl -X POST http://localhost:8004/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "chatterbox-es-latam",
    "input": "Hola, este es un ejemplo de síntesis de voz.",
    "voice": "default.wav"
  }' \
  --output audio.mp3

# Con parámetros personalizados
curl -X POST http://localhost:8004/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Texto a sintetizar",
    "voice_mode": "predefined",
    "predefined_voice_id": "default.wav",
    "temperature": 0.8,
    "exaggeration": 1.2,
    "output_format": "mp3"
  }' \
  --output audio.mp3
```

## API Reference

### GET /health

Verifica el estado del servidor.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cuda"
}
```

### POST /v1/audio/speech

Endpoint compatible con OpenAI TTS API.

**Request Body:**
```json
{
  "model": "chatterbox-es-latam",
  "input": "Texto a sintetizar",
  "voice": "default.wav",
  "response_format": "mp3",
  "speed": 1.0,
  "seed": 0
}
```

**Parameters:**
- `model` (string): Modelo a usar (siempre "chatterbox-es-latam")
- `input` (string): Texto a sintetizar
- `voice` (string): ID de la voz (nombre del archivo en voices/)
- `response_format` (string): Formato de salida ("wav", "mp3", "opus")
- `speed` (float): Velocidad (0.25-4.0)
- `seed` (int, optional): Semilla para reproducibilidad

**Response:**
Audio en el formato especificado (streaming)

### POST /tts

Endpoint personalizado con parámetros avanzados.

**Request Body:**
```json
{
  "text": "Texto a sintetizar",
  "voice_mode": "predefined",
  "predefined_voice_id": "default.wav",
  "temperature": 0.8,
  "exaggeration": 1.0,
  "cfg_weight": 0.5,
  "speed_factor": 1.0,
  "seed": 0,
  "output_format": "wav",
  "split_text": true,
  "chunk_size": 200,
  "language": "es"
}
```

**Parameters:**
- `text` (string, required): Texto a sintetizar
- `voice_mode` (string): "predefined" o "clone"
- `predefined_voice_id` (string): ID de voz predefinida
- `reference_audio_filename` (string): Archivo de referencia para clonación
- `temperature` (float): Aleatoriedad (0.0-1.5)
- `exaggeration` (float): Expresividad (0.25-2.0)
- `cfg_weight` (float): Peso de guía (0.2-1.0)
- `speed_factor` (float): Velocidad (0.25-4.0)
- `seed` (int): Semilla para reproducibilidad
- `output_format` (string): "wav", "mp3", o "opus"
- `split_text` (bool): Dividir texto en chunks
- `chunk_size` (int): Tamaño de chunks
- `language` (string): Idioma ("es")

**Response:**
Audio en el formato especificado (streaming)

### GET /

Interfaz web principal (HTML)

## Desarrollo

### Estructura del Código

```
├── server.py           # FastAPI app principal
├── config.py          # Gestión de configuración
├── engine.py          # Wrapper del motor TTS
├── models.py          # Modelos Pydantic
├── utils.py           # Utilidades
├── config.yaml        # Configuración
└── ui/                # Interfaz web
    ├── index.html
    ├── styles.css
    └── script.js
```

### Agregar Voces Predefinidas

1. Coloca archivos WAV en el directorio `voices/`
2. El nombre del archivo será el ID de la voz
3. Usa ese ID en la API

```bash
# Ejemplo
voices/
├── default.wav
├── masculine.wav
└── feminine.wav
```

### Modificar Parámetros por Defecto

Edita `config.yaml`:

```yaml
generation_defaults:
  temperature: 0.8      # Tu valor
  exaggeration: 1.0     # Tu valor
  cfg_weight: 0.5       # Tu valor
  speed_factor: 1.0     # Tu valor
```

## Troubleshooting

### El servidor no inicia

**Problema**: Error al cargar el modelo

**Solución**:
```bash
# Verifica que las dependencias estén instaladas
pip install -r requirements.txt

# Verifica CUDA si usas GPU
python -c "import torch; print(torch.cuda.is_available())"

# Intenta con CPU
# En config.yaml, cambia device: auto a device: cpu
```

### Error de memoria

**Problema**: Out of memory (OOM)

**Solución**:
- Usa GPU con más VRAM
- Reduce el tamaño de chunks
- Procesa textos más cortos
- Usa CPU (más lento pero sin límite de VRAM)

### Audio de mala calidad

**Problema**: Audio distorsionado o poco natural

**Solución**:
- Usa temperatura más baja (0.3-0.5)
- Ajusta exaggeration a valores más bajos (0.5-0.8)
- Usa audio de referencia de mejor calidad
- Verifica que el modelo esté correctamente cargado

### API no responde

**Problema**: Timeout o sin respuesta

**Solución**:
```bash
# Verifica que el servidor esté corriendo
curl http://localhost:8004/health

# Verifica logs
tail -f logs/tts_server.log

# Reinicia el servidor
```

### Docker: GPU no detectada

**Problema**: CUDA no disponible en Docker

**Solución**:
```bash
# Instala nvidia-docker2
sudo apt-get install nvidia-docker2
sudo systemctl restart docker

# Ejecuta con --gpus all
docker run --gpus all -p 8004:8004 chatterbox-es-latam:cuda

# Verifica dentro del contenedor
docker run --gpus all --rm nvidia/cuda:12.1.0-runtime-ubuntu22.04 nvidia-smi
```

## Recursos Adicionales

- [Repositorio GitHub](https://github.com/groxaxo/chatterbox-es-latam)
- [Chatterbox Original](https://github.com/resemble-ai/chatterbox)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Documentación del proyecto](./docs/)

## Licencia

MIT License - Ver [LICENSE](../LICENSE)

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Haz commit de tus cambios
4. Push a la rama
5. Abre un Pull Request

## Soporte

- **Issues**: [GitHub Issues](https://github.com/groxaxo/chatterbox-es-latam/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/groxaxo/chatterbox-es-latam/discussions)
