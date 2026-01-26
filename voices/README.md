# Voces Predefinidas

Este directorio contiene las voces predefinidas que se pueden usar en el sistema TTS.

## Agregar voces

Para agregar una nueva voz:

1. Coloca un archivo de audio (WAV recomendado) en este directorio
2. El archivo debe contener una muestra clara de voz (3-10 segundos)
3. El nombre del archivo será el ID de la voz en la API

Ejemplo:
```
voices/
├── default.wav         # Voz por defecto
├── masculine.wav       # Voz masculina
└── feminine.wav        # Voz femenina
```

## Uso en la API

```bash
# OpenAI-compatible
curl -X POST http://localhost:8004/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "chatterbox-es-latam",
    "input": "Hola mundo",
    "voice": "default.wav"
  }'

# Custom endpoint
curl -X POST http://localhost:8004/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hola mundo",
    "voice_mode": "predefined",
    "predefined_voice_id": "default.wav"
  }'
```

## Notas

- Formato recomendado: WAV, 24kHz, mono
- Duración recomendada: 3-10 segundos
- Calidad: Audio claro sin ruido de fondo
