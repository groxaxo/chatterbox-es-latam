# Fallback a Web Speech API

Cuando el dispositivo no tiene suficiente potencia para inferencia local, el SDK automáticamente usa Web Speech API como fallback.

## Cuándo se usa Fallback

El SDK detecta automáticamente si debe usar fallback basándose en:

1. **RAM insuficiente**: < 8GB
2. **CPU/GPU no soportado**: Dispositivos muy antiguos
3. **ONNX Runtime no disponible**: Falta de dependencias nativas
4. **Error de carga de modelo**: Modelo corrupto o incompatible

## Comportamiento

### API Transparente

El fallback es transparente para el código consumidor:

```typescript
// Este código funciona igual en ambos casos
const tts = await ChatterboxTTS.create();
await tts.speak("Hola mundo");

// Verificar qué backend se está usando
if (tts.getCapability() === 'webspeech') {
  console.log('Usando fallback Web Speech API');
}
```

### Diferencias

| Característica | Chatterbox ONNX | Web Speech Fallback |
|----------------|-----------------|---------------------|
| Voz personalizada | ✅ Sí | ❌ No |
| Calidad | Alta (neural) | Variable (sistema) |
| Latencia | 200-800ms | ~50ms |
| Offline | ✅ Sí | Depende del sistema |
| Voces disponibles | La del usuario | Hombre/Mujer sistema |

## Configuración de Fallback

### Voces del Sistema

En fallback, se usan las voces del sistema operativo:

```typescript
// Configuración de voz en fallback
interface WebSpeechConfig {
  // Preferencia de voz
  preferredVoice: 'hombre' | 'mujer';
  
  // Locale
  lang: string;  // default: 'es-MX'
  
  // Volumen
  volume: number;  // 0.0-1.0
  
  // Velocidad
  rate: number;  // 0.1-10, default: 1.0
  
  // Tono
  pitch: number;  // 0-2, default: 1.0
}
```

### Voces Preferidas

El SDK busca estas voces en orden de preferencia:

**Para "mujer"**:
1. `Microsoft Sabina - Spanish (Mexico)`
2. `Microsoft Helena - Spanish (Spain)`
3. Primera voz en español disponible

**Para "hombre"**:
1. `Microsoft Raul - Spanish (Mexico)`
2. `Microsoft Pablo - Spanish (Spain)`
3. Primera voz en español disponible

## Forzar Fallback

Para testing o dispositivos específicos:

```typescript
const tts = await ChatterboxTTS.create({
  backend: 'webspeech'  // Forzar fallback
});
```

## Detectar Fallback

```typescript
const tts = await ChatterboxTTS.create();

if (tts.getCapability() === 'webspeech') {
  // Mostrar mensaje al usuario
  showNotification(
    'Tu dispositivo no soporta voz personalizada. ' +
    'Usando voz del sistema.'
  );
  
  // Ocultar opciones de voz personalizada en UI
  hideCustomVoiceOptions();
}
```

## Migración de Código Existente

Si ya usas Web Speech API directamente:

### Antes (Web Speech API)
```typescript
function speak(text: string) {
  const utterance = new SpeechSynthesisUtterance(text);
  const voices = window.speechSynthesis.getVoices();
  
  // Seleccionar voz
  if (config.voices === 'mujer') {
    utterance.voice = voices.find(v => 
      v.name.includes('Sabina')
    ) || voices[0];
  }
  
  utterance.volume = config.volume;
  window.speechSynthesis.speak(utterance);
}
```

### Después (Chatterbox SDK)
```typescript
import { ChatterboxTTS } from '@neufitech/chatterbox-client';

const tts = await ChatterboxTTS.create();

// Si hay voz personalizada, cargarla
if (config.customVoiceId && tts.getCapability() !== 'webspeech') {
  await tts.loadVoice(`./voices/${config.customVoiceId}.onnx`);
}

async function speak(text: string) {
  await tts.speak(text, { volume: config.volume });
}
```

## Requisitos del Sistema para Fallback

### Windows 10/11
- Voces de español instaladas
- Actualizar en: Configuración → Hora e idioma → Voz

### Voces Recomendadas
Instalar desde Windows Settings:
- Español (España)
- Español (México)

## Limitaciones

1. **Sin voz personalizada**: No se puede usar la voz del usuario
2. **Calidad variable**: Depende de las voces instaladas
3. **Sin control de modelo**: No se puede ajustar temperature, etc.
4. **Dependencia de sistema**: Requiere voces de Windows instaladas

## Troubleshooting

### No hay voces disponibles

```typescript
const voices = window.speechSynthesis.getVoices();
if (voices.length === 0) {
  // Esperar a que carguen
  window.speechSynthesis.onvoiceschanged = () => {
    const voices = window.speechSynthesis.getVoices();
    console.log('Voces disponibles:', voices.map(v => v.name));
  };
}
```

### Voz no suena

1. Verificar volumen del sistema
2. Verificar que no haya otro audio bloqueando
3. Verificar permisos de audio en el navegador

### Voz incorrecta

Verificar idioma del sistema y voces instaladas:

```typescript
const voices = window.speechSynthesis.getVoices();
const spanishVoices = voices.filter(v => v.lang.startsWith('es'));
console.log('Voces en español:', spanishVoices.map(v => v.name));
```
