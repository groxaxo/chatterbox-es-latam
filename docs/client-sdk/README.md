# Client SDK

SDK TypeScript para inferencia TTS local en tablets Surface.

> ⚠️ **Estado**: En desarrollo (Fase 3). Esta documentación describe la API planificada.

## Características

- 🚀 Inferencia local ONNX
- 🎯 Optimizado para Surface Pro (NPU/CPU)
- 🔄 Fallback automático a Web Speech API
- 📦 Gestión de voces locales
- 🔊 Utilidades de reproducción de audio

## Instalación

```bash
npm install @neufitech/chatterbox-client
```

## Quick Start

```typescript
import { ChatterboxTTS } from '@neufitech/chatterbox-client';

// Inicializar
const tts = await ChatterboxTTS.create();

// Descargar voz del servidor
await tts.downloadVoice('https://api.example.com', 'voice_id');

// Cargar voz local
await tts.loadVoice('./voices/mi_voz.onnx');

// Sintetizar texto
const audio = await tts.synthesize("Hola mundo");

// O sintetizar y reproducir directamente
await tts.speak("Hola mundo");
```

## API Reference

Ver [API.md](./API.md) para documentación completa.

## Requisitos

### Runtime
- Node.js 18+ (para Electron apps)
- Windows 10/11

### Hardware mínimo
- 8GB RAM
- CPU: Intel 10th Gen+ o Snapdragon X

### Dependencias nativas
- `onnxruntime-node` >= 1.16.0

## Backends Soportados

| Backend | Dispositivo | Performance |
|---------|-------------|-------------|
| QNN | Surface Pro 11 (NPU) | ⭐⭐⭐ |
| DirectML | Surface Pro 9 (iGPU) | ⭐⭐ |
| CPU | Cualquier PC | ⭐ |
| Web Speech | Fallback | Básico |

## Estructura

```
client-sdk/
├── src/
│   ├── index.ts           # Entry point
│   ├── ChatterboxTTS.ts   # Clase principal
│   ├── VoiceManager.ts    # Gestión de voces
│   ├── backends/
│   │   ├── ONNXBackend.ts
│   │   ├── WebSpeechBackend.ts
│   │   └── index.ts
│   └── utils/
│       ├── audio.ts
│       └── detection.ts
├── models/                 # Modelos ONNX
├── package.json
└── tsconfig.json
```

## Próximos Pasos

- [ ] Implementar core (Fase 3)
- [ ] Publicar a npm
- [ ] Documentar API completa
