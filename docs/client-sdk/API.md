# Client SDK API Reference

> ⚠️ **Estado**: API planificada (Fase 3). Puede cambiar durante implementación.

## ChatterboxTTS

Clase principal para síntesis de voz.

### Constructor

```typescript
static async create(options?: TTSOptions): Promise<ChatterboxTTS>
```

**Opciones**:
```typescript
interface TTSOptions {
  // Path donde se almacenan los modelos ONNX
  modelsPath?: string;  // default: './models'
  
  // Backend preferido
  backend?: 'auto' | 'npu' | 'directml' | 'cpu' | 'webspeech';
  
  // Configuración de audio
  sampleRate?: number;  // default: 24000
  
  // Logging
  debug?: boolean;  // default: false
}
```

**Ejemplo**:
```typescript
const tts = await ChatterboxTTS.create({
  modelsPath: './assets/models',
  backend: 'auto',
  debug: true
});
```

---

### Métodos

#### loadVoice

Carga un archivo de voz local.

```typescript
async loadVoice(voicePath: string): Promise<void>
```

**Parámetros**:
- `voicePath`: Path al archivo `.onnx` o `.npy`

**Ejemplo**:
```typescript
await tts.loadVoice('./voices/usuario.onnx');
```

**Errores**:
- `VoiceNotFoundError`: Archivo no existe
- `InvalidVoiceError`: Formato inválido

---

#### downloadVoice

Descarga una voz desde el servidor.

```typescript
async downloadVoice(
  serverUrl: string, 
  voiceId: string,
  options?: DownloadOptions
): Promise<string>
```

**Parámetros**:
- `serverUrl`: URL base del servidor
- `voiceId`: ID de la voz a descargar
- `options`: Opciones adicionales

**Retorna**: Path local donde se guardó la voz

**Ejemplo**:
```typescript
const localPath = await tts.downloadVoice(
  'https://api.example.com',
  'voice_123456'
);
// localPath = './voices/voice_123456.onnx'
```

---

#### synthesize

Sintetiza texto a audio buffer.

```typescript
async synthesize(text: string, options?: SynthesisOptions): Promise<AudioBuffer>
```

**Parámetros**:
- `text`: Texto a sintetizar
- `options`: Opciones de síntesis

**Opciones**:
```typescript
interface SynthesisOptions {
  temperature?: number;  // 0.1-1.0, default: 0.7
  topP?: number;         // 0.1-1.0, default: 0.9
  maxLength?: number;    // Máximo de tokens
}
```

**Retorna**: `AudioBuffer` con el audio generado

**Ejemplo**:
```typescript
const audio = await tts.synthesize("Hola mundo", {
  temperature: 0.5
});

// Reproducir
const audioContext = new AudioContext();
const source = audioContext.createBufferSource();
source.buffer = audio;
source.connect(audioContext.destination);
source.start();
```

---

#### speak

Sintetiza y reproduce directamente.

```typescript
async speak(text: string, options?: SpeakOptions): Promise<void>
```

**Parámetros**:
- `text`: Texto a sintetizar
- `options`: Opciones de síntesis + volumen

**Opciones**:
```typescript
interface SpeakOptions extends SynthesisOptions {
  volume?: number;  // 0.0-1.0, default: 1.0
}
```

**Ejemplo**:
```typescript
await tts.speak("Buenos días", { volume: 0.8 });
```

---

#### stop

Detiene la reproducción actual.

```typescript
stop(): void
```

---

#### getCapability

Retorna la capacidad detectada del dispositivo.

```typescript
getCapability(): TTSCapability
```

**Retorna**:
```typescript
type TTSCapability = 'npu' | 'directml' | 'cpu' | 'webspeech';
```

**Ejemplo**:
```typescript
const cap = tts.getCapability();
console.log(`Usando backend: ${cap}`);
// "Usando backend: npu"
```

---

#### isReady

Verifica si el TTS está listo para usar.

```typescript
isReady(): boolean
```

---

#### getCurrentVoice

Obtiene información de la voz cargada.

```typescript
getCurrentVoice(): VoiceInfo | null
```

**Retorna**:
```typescript
interface VoiceInfo {
  id: string;
  name: string;
  path: string;
  loadedAt: Date;
}
```

---

## VoiceManager

Gestión de voces locales.

### Métodos

#### listVoices

Lista todas las voces locales.

```typescript
async listVoices(): Promise<LocalVoice[]>
```

**Retorna**:
```typescript
interface LocalVoice {
  id: string;
  name: string;
  path: string;
  size: number;      // bytes
  createdAt: Date;
}
```

---

#### deleteVoice

Elimina una voz local.

```typescript
async deleteVoice(voiceId: string): Promise<void>
```

---

#### getVoiceInfo

Obtiene información de una voz.

```typescript
async getVoiceInfo(voiceId: string): Promise<LocalVoice | null>
```

---

#### getStorageUsage

Obtiene el espacio usado por voces.

```typescript
async getStorageUsage(): Promise<StorageInfo>
```

**Retorna**:
```typescript
interface StorageInfo {
  totalBytes: number;
  voiceCount: number;
}
```

---

## Utilidades

### detectCapability

Detecta la capacidad del dispositivo.

```typescript
async function detectCapability(): Promise<TTSCapability>
```

**Ejemplo**:
```typescript
import { detectCapability } from '@neufitech/chatterbox-client';

const cap = await detectCapability();
if (cap === 'webspeech') {
  console.log('Dispositivo no soporta inferencia local');
}
```

---

### isSupported

Verifica si Chatterbox TTS es soportado.

```typescript
function isSupported(): boolean
```

---

## Tipos

```typescript
// Capacidad del dispositivo
type TTSCapability = 'npu' | 'directml' | 'cpu' | 'webspeech';

// Opciones de inicialización
interface TTSOptions {
  modelsPath?: string;
  backend?: 'auto' | TTSCapability;
  sampleRate?: number;
  debug?: boolean;
}

// Opciones de síntesis
interface SynthesisOptions {
  temperature?: number;
  topP?: number;
  maxLength?: number;
}

// Opciones de speak
interface SpeakOptions extends SynthesisOptions {
  volume?: number;
}

// Información de voz
interface VoiceInfo {
  id: string;
  name: string;
  path: string;
  loadedAt: Date;
}

// Voz local
interface LocalVoice {
  id: string;
  name: string;
  path: string;
  size: number;
  createdAt: Date;
}

// Info de almacenamiento
interface StorageInfo {
  totalBytes: number;
  voiceCount: number;
}
```

---

## Errores

```typescript
class ChatterboxError extends Error {
  code: string;
}

class VoiceNotFoundError extends ChatterboxError {
  code = 'VOICE_NOT_FOUND';
}

class InvalidVoiceError extends ChatterboxError {
  code = 'INVALID_VOICE';
}

class SynthesisError extends ChatterboxError {
  code = 'SYNTHESIS_FAILED';
}

class NetworkError extends ChatterboxError {
  code = 'NETWORK_ERROR';
}
```

---

## Eventos

```typescript
// Eventos disponibles
tts.on('synthesisStart', (text: string) => {});
tts.on('synthesisEnd', (duration: number) => {});
tts.on('error', (error: ChatterboxError) => {});
tts.on('voiceLoaded', (voice: VoiceInfo) => {});
```
