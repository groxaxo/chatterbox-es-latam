# Chatterbox ES-LATAM

> Sistema de Text-to-Speech personalizado para español latinoamericano, optimizado para aplicaciones de Comunicación Aumentativa Alternativa (AAC).

## 🎯 Objetivo

Permitir que personas con discapacidades del habla puedan comunicarse usando **su propia voz clonada**, con inferencia rápida en tablets Surface.

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                    SERVIDOR (GPU Potente)                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  1. Usuario sube audio de su voz                            ││
│  │  2. Servidor procesa con modelo LoRA fine-tuned             ││
│  │  3. Genera "Voice ID" optimizado para inferencia            ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ Descarga Voice ID
┌─────────────────────────────────────────────────────────────────┐
│                    TABLET SURFACE                                │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  1. Carga Voice ID localmente                               ││
│  │  2. Inferencia ONNX rápida (CPU/NPU)                        ││
│  │  3. Reproduce audio con la voz del usuario                  ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Estructura del Proyecto

```
chatterbox-es-latam/
├── docs/                    # 📚 Documentación (estás aquí)
├── server/                  # 🖥️ Servidor FastAPI de enrollment
├── training/                # 🎓 Scripts de fine-tuning LoRA
├── client-sdk/              # 📱 SDK para tablets (ONNX)
└── web/                     # 🌐 Demo web
```

## 🚀 Quick Start

### Para desarrollo del servidor
```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Iniciar servidor
cd server
uvicorn main:app --reload
```

### Para usar el SDK en tu app
```bash
npm install @neufitech/chatterbox-client
```

```typescript
import { ChatterboxTTS } from '@neufitech/chatterbox-client';

const tts = await ChatterboxTTS.create();
await tts.loadVoice('./voices/user.onnx');
const audio = await tts.synthesize("Hola mundo");
```

## 📖 Documentación

| Documento | Descripción |
|-----------|-------------|
| [Arquitectura](./ARCHITECTURE.md) | Diseño del sistema completo |
| [Hardware](./HARDWARE.md) | Tablets soportadas y requisitos |
| [Servidor](./server/README.md) | API de enrollment |
| [Client SDK](./client-sdk/README.md) | SDK para tablets |
| [Integración SAI](./integration/SAI.md) | Guía para app SAI |
| [Roadmap](./ROADMAP.md) | Fases del proyecto |

## 🔬 Estado del Proyecto

| Fase | Estado | Descripción |
|------|--------|-------------|
| Fase 0 | ✅ | Documentación y setup |
| Fase 1 | 🔄 | Research ONNX |
| Fase 2 | ⏳ | Mejoras al servidor |
| Fase 3 | ⏳ | Client SDK |
| Fase 4 | ⏳ | Integración SAI |
| Fase 5 | ⏳ | Testing y producción |

## 📝 Licencia

[Definir licencia]

## 👥 Contribuidores

- Neufitech Team
