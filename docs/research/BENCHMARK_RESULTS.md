# Benchmark Results

> ⚠️ **Estado**: Pendiente de ejecución (Fase 1)

Este documento contendrá los resultados de benchmarks en hardware real.

## Metodología

### Dispositivos de Test

| Dispositivo | CPU | RAM | Aceleración |
|-------------|-----|-----|-------------|
| Surface Pro 11 | Snapdragon X Elite | 16GB | NPU |
| Surface Pro 9 i7 | i7-1265U | 16GB | DirectML |
| Surface Pro 9 i5 | i5-1245U | 8GB | CPU |

### Métricas

- **Latencia**: Tiempo desde input hasta primer audio
- **Throughput**: Caracteres/segundo
- **Memoria**: RAM usada durante inferencia
- **Batería**: Impacto en autonomía

### Casos de Prueba

| ID | Texto | Palabras | Caracteres |
|----|-------|----------|------------|
| T1 | "Hola" | 1 | 4 |
| T2 | "Buenos días, ¿cómo estás?" | 4 | 24 |
| T3 | "Quiero ir al baño, por favor" | 6 | 30 |
| T4 | Texto largo (~50 palabras) | 50 | ~300 |

## Resultados

### Surface Pro 11 (NPU)

| Test | Latencia | Memoria | Notas |
|------|----------|---------|-------|
| T1 | - | - | |
| T2 | - | - | |
| T3 | - | - | |
| T4 | - | - | |

### Surface Pro 9 i7 (DirectML)

| Test | Latencia | Memoria | Notas |
|------|----------|---------|-------|
| T1 | - | - | |
| T2 | - | - | |
| T3 | - | - | |
| T4 | - | - | |

### Surface Pro 9 i5 (CPU)

| Test | Latencia | Memoria | Notas |
|------|----------|---------|-------|
| T1 | - | - | |
| T2 | - | - | |
| T3 | - | - | |
| T4 | - | - | |

## Comparación con Web Speech API

| Test | Chatterbox (mejor) | Web Speech | Diferencia |
|------|-------------------|------------|------------|
| T1 | - | ~50ms | |
| T2 | - | ~70ms | |
| T3 | - | ~80ms | |
| T4 | - | ~150ms | |

## Optimizaciones Probadas

### Quantización INT8

| Dispositivo | Antes | Después | Mejora |
|-------------|-------|---------|--------|
| Pro 11 | - | - | |
| Pro 9 i7 | - | - | |
| Pro 9 i5 | - | - | |

### Modelo Size

| Versión | Tamaño | Notas |
|---------|--------|-------|
| FP32 | - | |
| FP16 | - | |
| INT8 | - | |

## Gráficos

```
[ Pendiente: Gráficos de latencia por dispositivo ]
```

## Conclusiones

[ Pendiente ]

## Recomendaciones

[ Pendiente ]

## Scripts de Benchmark

```bash
# TODO: Agregar script de benchmark
python scripts/benchmark.py --device npu --iterations 10
```

## Raw Data

[ Link a CSV con datos crudos ]
