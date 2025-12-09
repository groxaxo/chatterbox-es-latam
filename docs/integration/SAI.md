# Integración con SAI

Guía paso a paso para integrar Chatterbox TTS en la aplicación SAI (Sistema de Comunicación Aumentativa).

## Visión General

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAMBIOS EN SAI                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐ │
│   │ Config State    │  │ TTS Service     │  │ UI Settings    │ │
│   │ (atoms/config)  │  │ (lib/)          │  │ (components/)  │ │
│   └────────┬────────┘  └────────┬────────┘  └───────┬────────┘ │
│            │                    │                   │           │
│            ▼                    ▼                   ▼           │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │              ButtonAnimation / Teclados                  │  │
│   │                    (Usan TTS)                           │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Preparación

### 1. Fork y Branch

```bash
# Clonar SAI (si no lo tienes)
git clone https://github.com/LucasGlave/SAI.git
cd SAI

# Crear branch para integración
git checkout -b feature/chatterbox-tts
```

### 2. Instalar Dependencias

```bash
# Instalar Client SDK
npm install @neufitech/chatterbox-client

# O si el package no está publicado aún, link local:
cd ../chatterbox-es-latam/client-sdk
npm link
cd ../SAI
npm link @neufitech/chatterbox-client
```

## Cambios Requeridos

### Archivo 1: `renderer/atoms/config.ts`

**Cambios**: Agregar campos para TTS personalizado.

```typescript
// renderer/atoms/config.ts
import { atom } from "recoil";

// NUEVO: Tipo para voz personalizada
interface CustomVoice {
  id: string;
  name: string;
  path: string;
  createdAt: string;
}

interface AppConfig {
  // ... campos existentes ...
  
  teclado: {
    bg_white: boolean;
    vocals_and_numbers: boolean;
    order_alfabetic: boolean;
    sound_press: boolean;
    predictor: boolean;
  };
  comunicacion_libre: {
    items_per_page: number;
    bg_white: boolean;
    type_font: string;
  };
  volume: number;
  activation: number;
  voices: string;  // "hombre" | "mujer" | "custom:{id}"
  eyeTracker: boolean;
  // ... otros campos existentes ...

  // NUEVOS CAMPOS para Chatterbox TTS
  ttsEngine: 'webspeech' | 'chatterbox';
  ttsCapability: 'npu' | 'directml' | 'cpu' | 'webspeech' | null;
  customVoices: CustomVoice[];
  activeCustomVoiceId: string | null;
  chatterboxServerUrl: string;
}

const currentConfigState = atom<AppConfig>({
  key: "currentConfigState",
  default: {
    // ... valores existentes ...
    teclado: {
      bg_white: false,
      vocals_and_numbers: false,
      order_alfabetic: false,
      sound_press: false,
      predictor: false,
    },
    comunicacion_libre: {
      items_per_page: 40,
      bg_white: false,
      type_font: "mixta",
    },
    volume: 3,
    activation: 3,
    voices: "mujer",
    eyeTracker: true,
    eyetrackerProvider: "JOACO",
    globalMousePointerVisible: true,
    localMousePointerVisible: true,
    smoothingFactor: "low",
    frameRate: "30",
    eyetrackerCalibration: { eye: "", points: 9 },
    
    // NUEVOS valores por defecto
    ttsEngine: 'webspeech',  // Fallback por defecto
    ttsCapability: null,      // Se detecta al iniciar
    customVoices: [],
    activeCustomVoiceId: null,
    chatterboxServerUrl: 'https://api.chatterbox.example.com',
  },
  effects: [localStorageEffect("config")],
});

export { currentConfigState };
export type { AppConfig, CustomVoice };
```

---

### Archivo 2: `renderer/lib/ChatterboxTTS.ts` (NUEVO)

**Crear**: Wrapper del SDK para SAI.

```typescript
// renderer/lib/ChatterboxTTS.ts
import { 
  ChatterboxTTS as ChatterboxSDK,
  TTSCapability,
  detectCapability 
} from '@neufitech/chatterbox-client';

class ChatterboxTTSService {
  private static instance: ChatterboxTTSService;
  private tts: ChatterboxSDK | null = null;
  private capability: TTSCapability = 'webspeech';
  private isInitialized = false;

  private constructor() {}

  static getInstance(): ChatterboxTTSService {
    if (!ChatterboxTTSService.instance) {
      ChatterboxTTSService.instance = new ChatterboxTTSService();
    }
    return ChatterboxTTSService.instance;
  }

  async initialize(): Promise<TTSCapability> {
    if (this.isInitialized) {
      return this.capability;
    }

    try {
      // Detectar capacidad del dispositivo
      this.capability = await detectCapability();
      
      // Solo inicializar SDK si no es webspeech
      if (this.capability !== 'webspeech') {
        this.tts = await ChatterboxSDK.create({
          modelsPath: './chatterbox-models',
          backend: 'auto',
          debug: process.env.NODE_ENV === 'development'
        });
      }
      
      this.isInitialized = true;
      return this.capability;
    } catch (error) {
      console.error('Error inicializando Chatterbox:', error);
      this.capability = 'webspeech';
      return 'webspeech';
    }
  }

  getCapability(): TTSCapability {
    return this.capability;
  }

  isReady(): boolean {
    return this.isInitialized;
  }

  async loadVoice(voicePath: string): Promise<void> {
    if (!this.tts) {
      throw new Error('Chatterbox TTS no disponible');
    }
    await this.tts.loadVoice(voicePath);
  }

  async downloadVoice(serverUrl: string, voiceId: string): Promise<string> {
    if (!this.tts) {
      throw new Error('Chatterbox TTS no disponible');
    }
    return await this.tts.downloadVoice(serverUrl, voiceId);
  }

  async speak(text: string, volume: number = 1.0): Promise<void> {
    if (!this.tts) {
      // Fallback a Web Speech
      return this.speakWebSpeech(text, volume);
    }
    
    await this.tts.speak(text, { volume });
  }

  private speakWebSpeech(text: string, volume: number): Promise<void> {
    return new Promise((resolve, reject) => {
      const utterance = new SpeechSynthesisUtterance(text);
      const config = JSON.parse(localStorage.getItem('config') || '{}');
      
      const voices = window.speechSynthesis.getVoices();
      if (voices.length > 0) {
        let selectedVoice;
        if (config.voices === 'hombre') {
          selectedVoice = voices.find(v => 
            v.name.includes('Raul') || v.name.includes('Pablo')
          );
        } else {
          selectedVoice = voices.find(v => 
            v.name.includes('Sabina') || v.name.includes('Helena')
          );
        }
        utterance.voice = selectedVoice || voices[0];
      }
      
      utterance.volume = volume;
      utterance.onend = () => resolve();
      utterance.onerror = (e) => reject(e);
      
      window.speechSynthesis.speak(utterance);
    });
  }

  stop(): void {
    if (this.tts) {
      this.tts.stop();
    }
    window.speechSynthesis.cancel();
  }
}

export const chatterboxTTS = ChatterboxTTSService.getInstance();
export default chatterboxTTS;
```

---

### Archivo 3: `renderer/lib/VoiceManager.ts` (NUEVO)

**Crear**: Gestión de voces personalizadas.

```typescript
// renderer/lib/VoiceManager.ts
import { CustomVoice } from '../atoms/config';
import chatterboxTTS from './ChatterboxTTS';

const VOICES_STORAGE_KEY = 'chatterbox_voices';
const VOICES_DIR = './chatterbox-voices';

class VoiceManagerService {
  private static instance: VoiceManagerService;

  private constructor() {}

  static getInstance(): VoiceManagerService {
    if (!VoiceManagerService.instance) {
      VoiceManagerService.instance = new VoiceManagerService();
    }
    return VoiceManagerService.instance;
  }

  async enrollVoice(
    serverUrl: string,
    audioFile: File,
    name: string
  ): Promise<CustomVoice> {
    // 1. Subir audio al servidor para enrollment
    const formData = new FormData();
    formData.append('file', audioFile);
    formData.append('name', name);

    const response = await fetch(`${serverUrl}/api/v1/enroll`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error en enrollment');
    }

    const result = await response.json();
    
    // 2. Descargar el Voice ID generado
    const voiceId = result.metadata.id;
    const localPath = await chatterboxTTS.downloadVoice(serverUrl, voiceId);

    // 3. Guardar metadata local
    const voice: CustomVoice = {
      id: voiceId,
      name: name,
      path: localPath,
      createdAt: new Date().toISOString(),
    };

    await this.saveVoiceLocally(voice);
    
    return voice;
  }

  async listVoices(): Promise<CustomVoice[]> {
    const stored = localStorage.getItem(VOICES_STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  }

  async deleteVoice(voiceId: string): Promise<void> {
    const voices = await this.listVoices();
    const updated = voices.filter(v => v.id !== voiceId);
    localStorage.setItem(VOICES_STORAGE_KEY, JSON.stringify(updated));
    
    // TODO: Eliminar archivo físico
    // await fs.unlink(voice.path);
  }

  async getVoice(voiceId: string): Promise<CustomVoice | null> {
    const voices = await this.listVoices();
    return voices.find(v => v.id === voiceId) || null;
  }

  private async saveVoiceLocally(voice: CustomVoice): Promise<void> {
    const voices = await this.listVoices();
    voices.push(voice);
    localStorage.setItem(VOICES_STORAGE_KEY, JSON.stringify(voices));
  }
}

export const voiceManager = VoiceManagerService.getInstance();
export default voiceManager;
```

---

### Archivo 4: `main/preload.ts`

**Modificar**: Exponer funciones de Chatterbox via IPC.

```typescript
// main/preload.ts
// ... código existente ...

const handler = {
  // ... funciones existentes ...
  
  // NUEVAS funciones para Chatterbox
  chatterboxSpeak: async (text: string, volume: number) => {
    const { chatterboxTTS } = await import('../renderer/lib/ChatterboxTTS');
    return chatterboxTTS.speak(text, volume);
  },
  
  chatterboxInit: async () => {
    const { chatterboxTTS } = await import('../renderer/lib/ChatterboxTTS');
    return chatterboxTTS.initialize();
  },
  
  chatterboxGetCapability: () => {
    const { chatterboxTTS } = require('../renderer/lib/ChatterboxTTS');
    return chatterboxTTS.getCapability();
  },
  
  chatterboxLoadVoice: async (voicePath: string) => {
    const { chatterboxTTS } = await import('../renderer/lib/ChatterboxTTS');
    return chatterboxTTS.loadVoice(voicePath);
  },

  // Modificar speak existente
  speak: (speakText: any) => {
    const config = JSON.parse(localStorage.getItem("config") || "{}");
    
    // Si hay voz personalizada activa, usar Chatterbox
    if (config.ttsEngine === 'chatterbox' && config.activeCustomVoiceId) {
      const { chatterboxTTS } = require('../renderer/lib/ChatterboxTTS');
      const volumeMap = { 1: 0.2, 2: 0.4, 3: 0.6, 4: 0.8, 5: 1.0 };
      return chatterboxTTS.speak(speakText, volumeMap[config.volume] || 1);
    }
    
    // Fallback: Web Speech API (código existente)
    const speech = new SpeechSynthesisUtterance(speakText);
    // ... resto del código existente ...
  },
};
```

---

### Archivo 5: `renderer/components/ButtonAnimation.tsx`

**Modificar**: Sección de TTS (líneas ~264-287).

```typescript
// renderer/components/ButtonAnimation.tsx
// ... imports existentes ...
import chatterboxTTS from "../lib/ChatterboxTTS";

// En handleExecuteFunctions, reemplazar la sección de speakText:

if (speakText) {
  const volumeMap = {
    1: 0.2,
    2: 0.4,
    3: 0.6,
    4: 0.8,
    5: 1.0,
  };
  const volume = volumeMap[config.volume] || 1;

  // NUEVO: Usar Chatterbox si está configurado
  if (config.ttsEngine === 'chatterbox' && 
      config.ttsCapability !== 'webspeech' &&
      config.activeCustomVoiceId) {
    try {
      await chatterboxTTS.speak(speakText, volume);
    } catch (error) {
      console.error('Chatterbox TTS error, falling back:', error);
      // Fallback a Web Speech
      fallbackWebSpeech(speakText, volume, config);
    }
  } else if (window.ipc) {
    // IPC speak (ya modificado en preload)
    window.ipc.speak(speakText);
  } else {
    // Web Speech API directo
    fallbackWebSpeech(speakText, volume, config);
  }
}

// Función helper para fallback
function fallbackWebSpeech(text: string, volume: number, config: any) {
  const speech = new SpeechSynthesisUtterance(text);
  const voices = window.speechSynthesis.getVoices();
  if (voices.length > 0) {
    const selectedVoice =
      config["voices"] === "hombre"
        ? voices.find(v => v.name.includes("Raul") || v.name.includes("Pablo"))
        : voices.find(v => v.name.includes("Sabina") || v.name.includes("Helena"));
    speech.voice = selectedVoice || voices[0];
  }
  speech.volume = volume;
  window.speechSynthesis.speak(speech);
}
```

---

### Archivo 6: Componente de Configuración (NUEVO)

**Crear**: UI para gestionar voces personalizadas.

> ⚠️ **Nota**: Este componente debe integrarse en la página de configuración existente de SAI.

```typescript
// renderer/components/settings/VoiceSettings.tsx
import React, { useState, useEffect } from 'react';
import { useRecoilState } from 'recoil';
import { currentConfigState, CustomVoice } from '../../atoms/config';
import { voiceManager } from '../../lib/VoiceManager';
import chatterboxTTS from '../../lib/ChatterboxTTS';

export function VoiceSettings() {
  const [config, setConfig] = useRecoilState(currentConfigState);
  const [voices, setVoices] = useState<CustomVoice[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [capability, setCapability] = useState<string | null>(null);

  useEffect(() => {
    loadVoices();
    initCapability();
  }, []);

  const loadVoices = async () => {
    const localVoices = await voiceManager.listVoices();
    setVoices(localVoices);
  };

  const initCapability = async () => {
    const cap = await chatterboxTTS.initialize();
    setCapability(cap);
    setConfig(prev => ({ ...prev, ttsCapability: cap }));
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    try {
      const voice = await voiceManager.enrollVoice(
        config.chatterboxServerUrl,
        file,
        file.name.replace(/\.[^/.]+$/, '')
      );
      setVoices(prev => [...prev, voice]);
      
      // Activar la nueva voz
      setConfig(prev => ({
        ...prev,
        ttsEngine: 'chatterbox',
        activeCustomVoiceId: voice.id,
      }));
    } catch (error) {
      console.error('Error uploading voice:', error);
      alert('Error al procesar la voz. Intenta de nuevo.');
    } finally {
      setIsUploading(false);
    }
  };

  const selectVoice = async (voiceId: string | null) => {
    if (voiceId) {
      const voice = voices.find(v => v.id === voiceId);
      if (voice) {
        await chatterboxTTS.loadVoice(voice.path);
      }
    }
    
    setConfig(prev => ({
      ...prev,
      ttsEngine: voiceId ? 'chatterbox' : 'webspeech',
      activeCustomVoiceId: voiceId,
    }));
  };

  const deleteVoice = async (voiceId: string) => {
    await voiceManager.deleteVoice(voiceId);
    setVoices(prev => prev.filter(v => v.id !== voiceId));
    
    if (config.activeCustomVoiceId === voiceId) {
      setConfig(prev => ({
        ...prev,
        ttsEngine: 'webspeech',
        activeCustomVoiceId: null,
      }));
    }
  };

  // Si el dispositivo no soporta Chatterbox, solo mostrar opciones básicas
  if (capability === 'webspeech') {
    return (
      <div className="voice-settings">
        <h3>Configuración de Voz</h3>
        <p className="warning">
          Tu dispositivo no soporta voz personalizada. 
          Usando voces del sistema.
        </p>
        <VoiceSelector 
          value={config.voices}
          onChange={(v) => setConfig(prev => ({ ...prev, voices: v }))}
        />
      </div>
    );
  }

  return (
    <div className="voice-settings">
      <h3>Configuración de Voz</h3>
      
      {/* Estado del dispositivo */}
      <div className="capability-badge">
        Aceleración: {capability?.toUpperCase()}
      </div>

      {/* Selector de modo */}
      <div className="mode-selector">
        <label>
          <input
            type="radio"
            checked={config.ttsEngine === 'webspeech'}
            onChange={() => selectVoice(null)}
          />
          Voces del sistema (Hombre/Mujer)
        </label>
        <label>
          <input
            type="radio"
            checked={config.ttsEngine === 'chatterbox'}
            onChange={() => {}}
            disabled={voices.length === 0}
          />
          Mi voz personalizada
        </label>
      </div>

      {/* Voces del sistema */}
      {config.ttsEngine === 'webspeech' && (
        <VoiceSelector 
          value={config.voices}
          onChange={(v) => setConfig(prev => ({ ...prev, voices: v }))}
        />
      )}

      {/* Voces personalizadas */}
      {config.ttsEngine === 'chatterbox' && (
        <div className="custom-voices">
          <h4>Mis Voces</h4>
          
          {voices.map(voice => (
            <div key={voice.id} className="voice-item">
              <input
                type="radio"
                checked={config.activeCustomVoiceId === voice.id}
                onChange={() => selectVoice(voice.id)}
              />
              <span>{voice.name}</span>
              <button onClick={() => deleteVoice(voice.id)}>🗑️</button>
            </div>
          ))}
          
          {voices.length === 0 && (
            <p>No hay voces personalizadas. Sube un audio para crear una.</p>
          )}
        </div>
      )}

      {/* Upload */}
      <div className="upload-section">
        <h4>Agregar Nueva Voz</h4>
        <p>Sube un audio de 10-30 segundos con tu voz.</p>
        <input
          type="file"
          accept="audio/*"
          onChange={handleFileUpload}
          disabled={isUploading}
        />
        {isUploading && <p>Procesando voz... esto puede tomar unos minutos.</p>}
      </div>
    </div>
  );
}

// Componente auxiliar para voces del sistema
function VoiceSelector({ value, onChange }: { 
  value: string; 
  onChange: (v: string) => void;
}) {
  return (
    <div className="system-voice-selector">
      <label>
        <input
          type="radio"
          checked={value === 'mujer'}
          onChange={() => onChange('mujer')}
        />
        Voz Mujer
      </label>
      <label>
        <input
          type="radio"
          checked={value === 'hombre'}
          onChange={() => onChange('hombre')}
        />
        Voz Hombre
      </label>
    </div>
  );
}
```

---

## Testing

### 1. Verificar detección de capacidades

```typescript
// En consola del navegador
const { chatterboxTTS } = require('./lib/ChatterboxTTS');
await chatterboxTTS.initialize();
console.log('Capacidad:', chatterboxTTS.getCapability());
```

### 2. Probar TTS

```typescript
await chatterboxTTS.speak('Hola, esto es una prueba');
```

### 3. Probar enrollment

1. Ir a Settings → Voz
2. Subir audio de prueba
3. Esperar procesamiento (~2-5 min)
4. Seleccionar voz y probar

### 4. Probar en ButtonAnimation

1. Configurar voz personalizada
2. Usar cualquier botón con `speakText`
3. Verificar que usa voz correcta

---

## Checklist de Integración

- [ ] Modificar `atoms/config.ts`
- [ ] Crear `lib/ChatterboxTTS.ts`
- [ ] Crear `lib/VoiceManager.ts`
- [ ] Modificar `main/preload.ts`
- [ ] Modificar `ButtonAnimation.tsx`
- [ ] Modificar `TecladoConIA.tsx`
- [ ] Modificar `TecladoConIA2.tsx`
- [ ] Crear componente `VoiceSettings.tsx`
- [ ] Integrar en página de configuración
- [ ] Testing en Surface Pro 11
- [ ] Testing en Surface Pro 9
- [ ] Testing de fallback

---

## Troubleshooting

### Error: "Chatterbox TTS no disponible"
- Verificar que el SDK está instalado
- Verificar que el dispositivo tiene suficiente RAM

### Error en enrollment
- Verificar URL del servidor
- Verificar que el audio es válido (WAV, 24kHz)
- Verificar conexión a internet

### Audio no suena
- Verificar volumen del sistema
- Verificar que la voz está cargada
- Probar fallback Web Speech
