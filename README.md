# Chatterbox ES-LATAM

<div align="center">

**Sistema de Text-to-Speech personalizado para español latinoamericano**

*Optimizado para aplicaciones de Comunicación Aumentativa Alternativa (AAC)*

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 🎯 Objetivo

Permitir que personas con discapacidades del habla puedan comunicarse usando **su propia voz clonada**, con inferencia rápida en tablets Surface.

## 🏗️ Arquitectura

```
┌─────────────────────────────────────┐
│     SERVIDOR (GPU Potente)          │
│  • Procesa audio del usuario        │
│  • Genera Voice ID optimizado       │
└──────────────────┬──────────────────┘
                   │ Descarga
                   ▼
┌─────────────────────────────────────┐
│     TABLET SURFACE                  │
│  • Inferencia ONNX local            │
│  • Reproducción rápida (<500ms)     │
│  • Fallback a Web Speech API        │
└─────────────────────────────────────┘
```

## 📁 Estructura del Proyecto

```
chatterbox-es-latam/
├── docs/                    # 📚 Documentación completa
├── server/                  # 🖥️ Servidor FastAPI (enrollment)
├── training/                # 🎓 Scripts de fine-tuning LoRA
├── client-sdk/              # 📱 SDK para tablets (ONNX) [WIP]
├── client/                  # 🔧 Scripts de exportación ONNX
└── web/                     # 🌐 Demo web
```

## 🚀 Quick Start

```bash
# 1. Clonar e instalar
git clone https://github.com/tu-usuario/chatterbox-es-latam.git
cd chatterbox-es-latam
pip install -r requirements.txt

# 2. Iniciar servidor
cd server
uvicorn main:app --reload --port 8000

# 3. Probar API
curl http://localhost:8000/health
```

Ver [documentación completa](./docs/README.md) para más detalles.

## 📖 Documentación

| Documento | Descripción |
|-----------|-------------|
| [📋 Overview](./docs/README.md) | Introducción y visión general |
| [🏗️ Arquitectura](./docs/ARCHITECTURE.md) | Diseño del sistema |
| [💻 Hardware](./docs/HARDWARE.md) | Tablets soportadas |
| [⚡ Quick Start](./docs/QUICKSTART.md) | Guía rápida |
| [🖥️ Server API](./docs/server/API.md) | Referencia de endpoints |
| [📱 Client SDK](./docs/client-sdk/README.md) | SDK para tablets |
| [🔗 Integración SAI](./docs/integration/SAI.md) | Guía para app SAI |
| [📅 Roadmap](./docs/ROADMAP.md) | Fases del proyecto |

## 🔬 Estado del Proyecto

| Fase | Estado | Descripción |
|------|--------|-------------|
| Fase 0 | ✅ Completada | Documentación y setup |
| Fase 1 | 🔄 En progreso | Research ONNX |
| Fase 2 | ⏳ Pendiente | Mejoras al servidor |
| Fase 3 | ⏳ Pendiente | Client SDK |
| Fase 4 | ⏳ Pendiente | Integración SAI |
| Fase 5 | ⏳ Pendiente | Testing y producción |

## 🛠️ Componentes

### Servidor de Enrollment
Procesa audio del usuario y genera Voice ID para inferencia local.

```bash
cd server
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Training (LoRA)
Fine-tuning del modelo Chatterbox para español LATAM.

```bash
cd training
python lora_es_latam.py
```

### Client SDK (En desarrollo)
SDK TypeScript para inferencia ONNX en tablets.

```typescript
import { ChatterboxTTS } from '@neufitech/chatterbox-client';

const tts = await ChatterboxTTS.create();
await tts.loadVoice('./voices/user.onnx');
await tts.speak("Hola mundo");
```

## 📋 Requisitos

### Servidor
- Python 3.10+
- CUDA 11.8+ (para GPU)
- 8GB+ VRAM

### Client (Tablets)
- Windows 10/11
- 8GB+ RAM
- Surface Pro 9/11 recomendado

## 👥 Contribuir

1. Fork el repositorio
2. Crear branch (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver [LICENSE](LICENSE) para detalles.

## 🙏 Agradecimientos

- [Resemble AI](https://github.com/resemble-ai/chatterbox) por Chatterbox TTS
- Equipo de Neufitech
