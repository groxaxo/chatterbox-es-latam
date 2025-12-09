# Arquitectura del Sistema

## Visión General

Chatterbox ES-LATAM implementa una arquitectura **híbrida cliente-servidor** optimizada para:
- **Procesamiento pesado** en servidor con GPU
- **Inferencia rápida** en tablets con CPU/NPU

## Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FLUJO COMPLETO                                  │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐         ┌──────────────────────────────────────────────┐
    │   USUARIO    │         │           SERVIDOR (RunPod/Cloud)            │
    │              │         │                                              │
    │  Graba audio ├────────►│  ┌────────────────────────────────────────┐  │
    │  de su voz   │  HTTP   │  │         ENROLLMENT PIPELINE            │  │
    │              │  POST   │  │                                        │  │
    └──────────────┘         │  │  1. Recibe audio (.wav/.mp3)           │  │
                             │  │  2. Procesa con modelo LoRA            │  │
                             │  │  3. Extrae embeddings de voz           │  │
                             │  │  4. Genera Voice ID (.onnx/.npy)       │  │
                             │  │                                        │  │
                             │  └────────────────────────────────────────┘  │
                             │                     │                        │
                             └─────────────────────┼────────────────────────┘
                                                   │
                                                   ▼ HTTP GET (descarga)
    ┌──────────────────────────────────────────────────────────────────────┐
    │                        TABLET SURFACE                                 │
    │                                                                       │
    │  ┌─────────────────────────────────────────────────────────────────┐ │
    │  │                    CLIENT SDK (ONNX Runtime)                    │ │
    │  │                                                                 │ │
    │  │   ┌──────────────┐    ┌───────────────┐    ┌───────────────┐   │ │
    │  │   │   Voice ID   │───►│  ONNX Model   │───►│ Audio Output  │   │ │
    │  │   │  (descargado)│    │  (inferencia) │    │   (speaker)   │   │ │
    │  │   └──────────────┘    └───────────────┘    └───────────────┘   │ │
    │  │                                                                 │ │
    │  │   Input: "Hola mundo"  ──────────────────►  Output: audio.wav  │ │
    │  │                                                                 │ │
    │  └─────────────────────────────────────────────────────────────────┘ │
    │                                                                       │
    │  ┌─────────────────────────────────────────────────────────────────┐ │
    │  │                    FALLBACK (Web Speech API)                    │ │
    │  │                                                                 │ │
    │  │   Para tablets sin suficiente potencia, usa TTS del sistema    │ │
    │  │                                                                 │ │
    │  └─────────────────────────────────────────────────────────────────┘ │
    └──────────────────────────────────────────────────────────────────────┘
```

## Componentes

### 1. Servidor de Enrollment

**Ubicación**: `/server`

**Responsabilidades**:
- Recibir audio del usuario
- Procesar con modelo Chatterbox + LoRA
- Generar Voice ID optimizado
- Almacenar y servir archivos

**Stack**:
- FastAPI (Python)
- PyTorch + Chatterbox
- CUDA para GPU

**Endpoints principales**:
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/enroll` | POST | Enrollar nueva voz |
| `/api/v1/voices` | GET | Listar voces |
| `/api/v1/voices/{id}/download` | GET | Descargar Voice ID |
| `/api/v1/infer` | POST | Inferencia en servidor (demo) |

### 2. Client SDK

**Ubicación**: `/client-sdk`

**Responsabilidades**:
- Cargar modelos ONNX
- Ejecutar inferencia local
- Gestionar voces descargadas
- Fallback a Web Speech API

**Stack**:
- TypeScript
- ONNX Runtime (onnxruntime-web o onnxruntime-node)
- DirectML para NPU (Windows)

**API**:
```typescript
interface ChatterboxTTS {
  create(options?: TTSOptions): Promise<ChatterboxTTS>;
  loadVoice(path: string): Promise<void>;
  synthesize(text: string): Promise<AudioBuffer>;
  getCapability(): 'npu' | 'cpu' | 'fallback';
}
```

### 3. Training Pipeline

**Ubicación**: `/training`

**Responsabilidades**:
- Fine-tuning con LoRA
- Datasets de español LATAM
- Exportación de checkpoints

**Archivos clave**:
- `lora_es_latam.py` - Script principal de training
- `dataset_orpheus.py` - Carga de datasets
- `create_merged_model.py` - Merge de LoRA weights

### 4. Web Demo

**Ubicación**: `/web`

**Responsabilidades**:
- UI para probar TTS
- Comparación LoRA vs Base model
- Gestión de voces

## Flujo de Datos

### Enrollment (una vez por usuario)

```
1. Usuario graba audio (5-30 segundos)
        │
        ▼
2. App envía audio al servidor
        │
        ▼
3. Servidor procesa:
   - VoiceEncoder extrae embeddings
   - S3Gen genera conditioning
   - Se crea Voice ID (.npy/.onnx)
        │
        ▼
4. Servidor almacena y retorna URL
        │
        ▼
5. App descarga Voice ID a storage local
```

### Inference (cada uso)

```
1. Usuario activa botón con texto
        │
        ▼
2. App detecta capacidad (NPU/CPU/fallback)
        │
        ├─────────────────────────────────────┐
        │                                     │
        ▼ (NPU/CPU)                           ▼ (fallback)
3a. Carga Voice ID                      3b. Web Speech API
        │                                     │
        ▼                                     │
4a. ONNX Runtime inference                    │
        │                                     │
        ▼                                     │
5a. Audio buffer generado                     │
        │                                     │
        └──────────────┬──────────────────────┘
                       │
                       ▼
              6. Reproduce audio
```

## Consideraciones de Performance

### Latencia Target

| Dispositivo | Backend | Latencia Target | Notas |
|-------------|---------|-----------------|-------|
| Surface Pro 11 | NPU (QNN) | <200ms | Mejor caso |
| Surface Pro 9 i7 | CPU | <400ms | Aceptable |
| Surface Pro 9 i5 | CPU | <600ms | Límite |
| Tablets viejas | Web Speech | ~50ms | Fallback |

### Optimizaciones Planificadas

1. **Quantización INT8** - Reducir tamaño del modelo
2. **Streaming** - Generar audio en chunks
3. **Caching** - Cache de frases comunes
4. **Lazy loading** - Cargar modelo bajo demanda

## Seguridad

### Datos sensibles
- Audio del usuario (temporal, se procesa y elimina)
- Voice ID (almacenado en servidor, encriptado)
- Voice ID local (almacenado en app data)

### Consideraciones
- HTTPS para todas las comunicaciones
- Voice ID no contiene audio recuperable
- Autenticación por usuario (futuro)
