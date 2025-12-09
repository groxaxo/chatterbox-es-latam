# Hardware Soportado

## Dispositivos Target

Este proyecto está optimizado para tablets **Microsoft Surface Pro** usadas en aplicaciones de Comunicación Aumentativa Alternativa (AAC).

## Matriz de Compatibilidad

| Dispositivo | CPU | RAM | Aceleración | TTS Engine | Performance |
|-------------|-----|-----|-------------|------------|-------------|
| **Surface Pro 11 Copilot+** | Snapdragon X Elite | 16GB | ✅ NPU (45 TOPS) | Chatterbox ONNX | ⭐⭐⭐ Excelente |
| **Surface Pro 9 i7** | i7-1265U (12th Gen) | 16GB | ✅ iGPU | Chatterbox ONNX | ⭐⭐ Bueno |
| **Surface Pro 9 i5** | i5-1245U (12th Gen) | 8GB | ⚠️ CPU only | Chatterbox ONNX | ⭐ Aceptable |
| **Tablets anteriores** | Variado | <8GB | ❌ | Web Speech API | Fallback |

## Detección Automática de Capacidades

El Client SDK detecta automáticamente qué backend usar:

```typescript
type TTSCapability = 'npu' | 'cpu' | 'fallback';

async function detectCapability(): Promise<TTSCapability> {
  // 1. Detectar NPU (Surface Pro 11)
  if (await hasQualcommNPU()) {
    return 'npu';
  }
  
  // 2. Detectar suficiente RAM para ONNX CPU
  const memory = navigator.deviceMemory || 4;
  if (memory >= 8) {
    return 'cpu';
  }
  
  // 3. Fallback para dispositivos limitados
  return 'fallback';
}
```

## Detalles por Dispositivo

### Surface Pro 11 Copilot+ (Recomendado)

**Especificaciones probadas**:
- Microsoft Surface Pro 11 13"
- Snapdragon X Elite
- 16GB RAM
- 512GB SSD
- Windows 11 Pro

**Aceleración NPU**:
- Qualcomm Hexagon NPU
- 45 TOPS de capacidad
- Soporte via ONNX Runtime QNN EP

**Performance esperado**:
- Latencia: <200ms
- Uso de memoria: ~500MB
- Batería: Optimizado para NPU

### Surface Pro 9 i7

**Especificaciones probadas**:
- Microsoft Surface Pro 9 13"
- Intel Core i7-1265U (12th Gen, 10 núcleos)
- 16GB RAM
- 512GB SSD
- Windows 11 Pro

**Aceleración**:
- Intel Iris Xe Graphics (iGPU)
- Puede usar DirectML para aceleración
- Fallback a CPU si DirectML no disponible

**Performance esperado**:
- Latencia: 300-500ms
- Uso de memoria: ~600MB
- Batería: Consumo moderado

### Surface Pro 9 i5

**Especificaciones probadas**:
- Microsoft Surface Pro 9 13"
- Intel Core i5-1245U (12th Gen, 10 núcleos)
- 8GB RAM
- 256GB SSD
- Windows 11 Pro

**Aceleración**:
- CPU only (RAM limitada para iGPU)

**Performance esperado**:
- Latencia: 400-700ms
- Uso de memoria: ~500MB
- Batería: Consumo moderado-alto

**Notas**:
- 8GB de RAM es el mínimo para ONNX inference
- Puede experimentar lag ocasional
- Considerar quantización INT8

### Tablets Anteriores (Fallback)

Cualquier tablet que no cumpla los requisitos mínimos usará **Web Speech API** del sistema operativo.

**Requisitos para fallback**:
- Windows 10/11
- Voces de español instaladas

**Limitaciones del fallback**:
- No usa voz personalizada
- Solo voces predefinidas (hombre/mujer)
- Calidad variable según voces instaladas

## Requisitos de Software

### Para Client SDK

```
Node.js >= 18.0
npm >= 9.0
Windows 10/11

# Dependencias nativas
onnxruntime-node >= 1.16.0
```

### Para NPU (Surface Pro 11)

```
# ONNX Runtime con Qualcomm QNN
onnxruntime-qnn >= 1.16.0

# Drivers de NPU actualizados
Windows Update al día
```

### Para DirectML (Surface Pro 9)

```
# ONNX Runtime con DirectML
onnxruntime-directml >= 1.16.0

# Drivers de gráficos actualizados
Intel Graphics Driver >= 31.0
```

## Benchmarks

> ⚠️ **Nota**: Estos benchmarks son estimaciones. Los valores reales se documentarán en [research/BENCHMARK_RESULTS.md](./research/BENCHMARK_RESULTS.md) después de la Fase 1.

### Texto corto (~10 palabras)

| Dispositivo | Backend | Latencia | Uso RAM |
|-------------|---------|----------|---------|
| Pro 11 NPU | QNN | ~150ms | ~400MB |
| Pro 9 i7 | DirectML | ~350ms | ~550MB |
| Pro 9 i5 | CPU | ~500ms | ~500MB |
| Fallback | Web Speech | ~50ms | N/A |

### Texto largo (~50 palabras)

| Dispositivo | Backend | Latencia | Uso RAM |
|-------------|---------|----------|---------|
| Pro 11 NPU | QNN | ~400ms | ~500MB |
| Pro 9 i7 | DirectML | ~800ms | ~600MB |
| Pro 9 i5 | CPU | ~1200ms | ~550MB |
| Fallback | Web Speech | ~100ms | N/A |

## Recomendaciones

### Para nuevos despliegues
- **Recomendado**: Surface Pro 11 Copilot+
- **Alternativa**: Surface Pro 9 i7 (16GB)

### Para tablets existentes
1. Verificar RAM disponible (mínimo 8GB)
2. Actualizar drivers de gráficos
3. Probar con texto corto primero
4. Si latencia > 1s, usar fallback

### Optimizaciones futuras
- Quantización INT8 para reducir uso de memoria
- Streaming de audio para reducir latencia percibida
- Caching de frases comunes
