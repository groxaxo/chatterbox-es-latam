# API Reference

Base URL: `http://localhost:8000/api/v1`

## Endpoints

### Health Check

```
GET /health
```

Verifica el estado del servidor.

**Response**:
```json
{
  "status": "ok",
  "device": "cuda"
}
```

---

### Enroll Voice

```
POST /api/v1/enroll
```

Registra una nueva voz a partir de un archivo de audio.

**Request** (multipart/form-data):
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `file` | File | Audio WAV/MP3 (5-30 segundos) |
| `name` | string | Nombre identificador de la voz |

**Response**:
```json
{
  "voice_id": "emb_abc123...",
  "metadata": {
    "id": "voice_1234567890",
    "name": "Juan",
    "created_at": "2024-12-09T10:30:00Z",
    "enrollment_time": 2.45,
    "ref_audio_path": "ref_juan_1234567890.wav"
  },
  "status": "success"
}
```

**Errores**:
| Código | Descripción |
|--------|-------------|
| 400 | Audio inválido o muy corto |
| 500 | Error de procesamiento |

**Ejemplo cURL**:
```bash
curl -X POST "http://localhost:8000/api/v1/enroll" \
  -F "file=@mi_voz.wav" \
  -F "name=Juan"
```

---

### List Voices

```
GET /api/v1/voices
```

Lista todas las voces registradas.

**Response**:
```json
[
  {
    "id": "voice_1234567890",
    "name": "Juan",
    "created_at": "2024-12-09T10:30:00Z",
    "enrollment_time": 2.45,
    "ref_audio_path": "ref_juan_1234567890.wav"
  },
  {
    "id": "voice_0987654321",
    "name": "María",
    "created_at": "2024-12-08T15:00:00Z",
    "enrollment_time": 1.89,
    "ref_audio_path": "ref_maria_0987654321.wav"
  }
]
```

---

### Delete Voice

```
DELETE /api/v1/voices/{voice_id}
```

Elimina una voz registrada.

**Path Parameters**:
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `voice_id` | string | ID de la voz |

**Response**:
```json
{
  "status": "success",
  "message": "Voice deleted"
}
```

---

### Inference (Demo)

```
POST /api/v1/infer
```

Genera audio TTS usando una voz registrada. 

> ⚠️ **Nota**: Este endpoint es para demo/testing. En producción, la inferencia se hace localmente en las tablets.

**Request** (JSON):
```json
{
  "text": "Hola, esto es una prueba",
  "voice_id": "voice_1234567890",
  "temperature": 0.7
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `text` | string | Texto a sintetizar |
| `voice_id` | string | ID de la voz a usar |
| `temperature` | float | Variabilidad (0.1-1.0, default: 0.7) |

**Response**:
```json
{
  "audio_url_lora": "/static/output/lora_1234567890.wav",
  "inference_time_lora": 1.234,
  "audio_url_base": "/static/output/base_1234567890.wav",
  "inference_time_base": 1.456,
  "status": "success"
}
```

**Errores**:
| Código | Descripción |
|--------|-------------|
| 404 | Voz no encontrada |
| 500 | Error de inferencia |

---

### List History

```
GET /api/v1/history
```

Lista el historial de inferencias.

**Response**:
```json
[
  {
    "id": "hist_1234567890",
    "text": "Hola mundo",
    "voice_id": "voice_1234567890",
    "lora_path": "lora_1234567890.wav",
    "base_path": "base_1234567890.wav",
    "lora_time": 1.234,
    "base_time": 1.456,
    "created_at": "2024-12-09T10:35:00Z"
  }
]
```

---

### Delete History Item

```
DELETE /api/v1/history/{history_id}
```

Elimina un elemento del historial.

**Response**:
```json
{
  "status": "success",
  "message": "History item deleted"
}
```

---

## Static Files

Los archivos de audio están disponibles en:

- **Input (referencias)**: `GET /static/input/{filename}`
- **Output (generados)**: `GET /static/output/{filename}`

---

## Schemas

### VoiceMetadata

```typescript
interface VoiceMetadata {
  id: string;
  name: string;
  created_at: string;       // ISO 8601
  enrollment_time: number;  // segundos
  ref_audio_path: string;
}
```

### InferenceRequest

```typescript
interface InferenceRequest {
  text: string;
  voice_id: string;
  temperature?: number;  // default: 0.7
}
```

### InferenceResponse

```typescript
interface InferenceResponse {
  audio_url_lora: string;
  inference_time_lora: number;
  audio_url_base: string;
  inference_time_base: number;
  status: string;
}
```

---

## Rate Limits

> ⚠️ **Pendiente**: Rate limiting se implementará en Fase 2.

Límites planificados:
- Enrollment: 10 requests/hora por IP
- Inference: 100 requests/hora por IP

---

## Errores Comunes

### 400 Bad Request
```json
{
  "detail": "Audio too short. Minimum 5 seconds required."
}
```

### 404 Not Found
```json
{
  "detail": "Voice not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Inference failed: CUDA out of memory"
}
```
