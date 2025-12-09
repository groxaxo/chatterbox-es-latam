# Roadmap del Proyecto

## Visión General

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           TIMELINE                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Fase 0        Fase 1         Fase 2         Fase 3         Fase 4     │
│   ┌───┐        ┌───┐          ┌───┐          ┌───┐          ┌───┐       │
│   │ ✓ │──────►│ ▶ │─────────►│   │─────────►│   │─────────►│   │       │
│   └───┘        └───┘          └───┘          └───┘          └───┘       │
│   Docs         ONNX           Server         Client         SAI         │
│   Setup        Research       Improve        SDK            Integr.     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Fase 0: Documentación y Setup ✅ COMPLETADA

**Objetivo**: Establecer base sólida de documentación y estructura del proyecto.

### Tasks Completadas
- [x] Explorar estructura actual del proyecto
- [x] Analizar componentes del servidor
- [x] Analizar app SAI para integración
- [x] Crear plan de implementación
- [x] Obtener aprobación del usuario
- [x] Limpiar repo (eliminar código ajeno)
- [x] Crear estructura `/docs`
- [x] Documentación core (README, ARCHITECTURE, HARDWARE)

### Deliverables
- `/docs/README.md`
- `/docs/ARCHITECTURE.md`
- `/docs/HARDWARE.md`
- `/docs/ROADMAP.md`
- `/docs/server/*`
- `/docs/client-sdk/*`
- `/docs/integration/*`

---

## Fase 1: ONNX Research 🔄 EN PROGRESO

**Objetivo**: Determinar viabilidad de inferencia local en tablets Surface.

### Tasks
- [ ] Investigar export de Chatterbox a ONNX
  - Analizar arquitectura del modelo
  - Identificar componentes exportables
  - Documentar limitaciones
- [ ] Setup ONNX Runtime en Windows
  - Probar `onnxruntime-node`
  - Probar `onnxruntime-directml`
  - Probar `onnxruntime-qnn`
- [ ] Escribir script de exportación
  - Exportar encoder
  - Exportar decoder
  - Exportar LLM (si aplicable)
- [ ] Benchmark en Surface Pro 11
  - Medir latencia con NPU
  - Medir uso de memoria
  - Probar diferentes longitudes de texto
- [ ] Benchmark en Surface Pro 9
  - Medir latencia CPU
  - Medir latencia DirectML
  - Determinar umbral de usabilidad
- [ ] Documentar hallazgos

### Deliverables
- `/docs/research/ONNX_EXPORT.md`
- `/docs/research/BENCHMARK_RESULTS.md`
- `/scripts/export_to_onnx.py`
- `/scripts/benchmark.py`

### Criterios de Éxito
| Métrica | Target | Mínimo Aceptable |
|---------|--------|------------------|
| Latencia Pro 11 (NPU) | <200ms | <400ms |
| Latencia Pro 9 (CPU) | <500ms | <800ms |
| Uso de memoria | <500MB | <800MB |
| Tamaño modelo ONNX | <300MB | <500MB |

### Riesgos
- **Alto**: Modelo no exportable a ONNX
  - Mitigación: Evaluar alternativas (TorchScript, OpenVINO)
- **Medio**: Latencia inaceptable
  - Mitigación: Quantización, optimización, streaming

---

## Fase 2: Mejoras al Servidor ⏳ PENDIENTE

**Objetivo**: Optimizar servidor para producción y compatibilidad con client SDK.

### Tasks
- [ ] Optimizar endpoint `/enroll`
  - Output compatible con ONNX client
  - Mejor manejo de errores
  - Validación de audio
- [ ] Nuevo endpoint `/download-voice`
  - Descarga segura de Voice ID
  - Compresión de archivos
- [ ] Docker setup
  - Dockerfile optimizado
  - docker-compose para desarrollo
  - Documentación de deploy
- [ ] Rate limiting y seguridad
  - Límites por IP/usuario
  - Validación de inputs
- [ ] Storage persistente
  - Integración S3/GCS (opcional)
  - Backup de Voice IDs

### Deliverables
- Endpoints actualizados
- `Dockerfile`
- `docker-compose.yml`
- `/docs/server/DEPLOYMENT.md`

---

## Fase 3: Client SDK ⏳ PENDIENTE

**Objetivo**: Crear SDK TypeScript para inferencia local en tablets.

### Tasks
- [ ] Crear estructura `/client-sdk`
  - Package.json
  - TypeScript config
  - Build system
- [ ] Implementar core
  - Wrapper ONNX Runtime
  - Gestión de modelos
  - Audio processing
- [ ] Implementar VoiceManager
  - Descargar voces del servidor
  - Almacenar localmente
  - CRUD de voces
- [ ] Implementar fallback
  - Detección de capacidades
  - Web Speech API wrapper
  - Transición seamless
- [ ] Testing
  - Unit tests
  - Integration tests
  - E2E en tablets reales
- [ ] Publicar a npm
  - `@neufitech/chatterbox-client`

### Deliverables
- `/client-sdk/` completo
- Package en npm
- `/docs/client-sdk/API.md`

### API Prevista
```typescript
// Inicialización
const tts = await ChatterboxTTS.create({
  modelsPath: './models',
  backend: 'auto' // 'npu' | 'cpu' | 'fallback'
});

// Gestión de voces
await tts.downloadVoice(serverUrl, 'voice_id');
await tts.loadVoice('./voices/user.onnx');
const voices = await tts.listVoices();

// Síntesis
const audio = await tts.synthesize("Hola mundo");
await tts.speak("Hola mundo"); // Síntesis + reproducción

// Info
const capability = tts.getCapability(); // 'npu' | 'cpu' | 'fallback'
const isReady = tts.isReady();
```

---

## Fase 4: Integración SAI ⏳ PENDIENTE

**Objetivo**: Integrar TTS personalizado en la app SAI.

### Tasks
- [ ] Crear branch `feature/chatterbox-tts` en SAI
- [ ] Modificar config state
  - Nuevos campos para voz personalizada
  - Estado de TTS engine
- [ ] Crear servicios
  - `ChatterboxTTS.ts`
  - `VoiceManager.ts`
- [ ] Modificar preload.ts
  - Exponer nuevas funciones IPC
- [ ] Modificar componentes TTS
  - `ButtonAnimation.tsx`
  - `TecladoConIA.tsx`
  - `TecladoConIA2.tsx`
- [ ] Crear UI de configuración
  - Subir audio para enrollment
  - Seleccionar voz activa
  - Ver estado de descargas
- [ ] Testing en tablets reales

### Deliverables
- Branch lista para merge
- `/docs/integration/SAI.md` actualizado
- Video demo

### Cambios en SAI

#### `renderer/atoms/config.ts`
```typescript
interface AppConfig {
  // Existentes
  voices: string; // "hombre" | "mujer" | "custom:{id}"
  
  // Nuevos
  ttsEngine: 'webspeech' | 'chatterbox';
  customVoices: CustomVoice[];
  activeVoiceId?: string;
  ttsCapability: 'npu' | 'cpu' | 'fallback';
}
```

#### `main/preload.ts`
```typescript
// Nuevas funciones a exponer
chatterboxSpeak: (text: string) => Promise<void>,
downloadVoice: (voiceId: string) => Promise<void>,
listLocalVoices: () => Promise<CustomVoice[]>,
deleteLocalVoice: (voiceId: string) => Promise<void>,
```

---

## Fase 5: Testing y Producción ⏳ PENDIENTE

**Objetivo**: Validar en hardware real y preparar para producción.

### Tasks
- [ ] Testing exhaustivo
  - Surface Pro 11 (NPU)
  - Surface Pro 9 i7 (DirectML)
  - Surface Pro 9 i5 (CPU)
  - Tablet vieja (fallback)
- [ ] Optimización basada en feedback
- [ ] Sistema de updates
  - Actualizar modelos OTA
  - Versionado de Voice IDs
- [ ] Documentación para usuarios finales
  - Guía para pacientes
  - Guía para terapeutas
  - Troubleshooting

### Deliverables
- Test reports
- Documentación de usuario
- Release v1.0

---

## Dependencias entre Fases

```
Fase 0 ──► Fase 1 ──► Fase 2
              │         │
              │         ▼
              └──────► Fase 3 ──► Fase 4 ──► Fase 5
```

- **Fase 1** bloquea Fase 3 (necesitamos saber si ONNX es viable)
- **Fase 2** y **Fase 3** pueden hacerse en paralelo
- **Fase 4** requiere Fase 3 completada
- **Fase 5** requiere todas las anteriores

---

## Timeline Estimado

| Fase | Duración Estimada | Fecha Inicio | Fecha Fin |
|------|-------------------|--------------|-----------|
| Fase 0 | 1 día | Dic 9 | Dic 9 ✅ |
| Fase 1 | 3-5 días | Dic 10 | Dic 14 |
| Fase 2 | 2-3 días | Dic 15 | Dic 17 |
| Fase 3 | 5-7 días | Dic 15 | Dic 21 |
| Fase 4 | 3-5 días | Dic 22 | Dic 26 |
| Fase 5 | 3-5 días | Dic 27 | Dic 31 |

> ⚠️ Estas fechas son estimaciones. La Fase 1 (ONNX Research) puede extenderse si se encuentran bloqueantes técnicos.
