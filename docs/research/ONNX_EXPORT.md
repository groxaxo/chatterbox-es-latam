# ONNX Export Research

> ⚠️ **Estado**: Pendiente de investigación (Fase 1)

Este documento se completará durante la Fase 1 del proyecto.

## Objetivos

1. Determinar si Chatterbox TTS puede exportarse a ONNX
2. Identificar componentes exportables
3. Documentar limitaciones y workarounds
4. Crear scripts de exportación

## Preguntas a Responder

### Arquitectura del Modelo

- [ ] ¿Cuáles son los componentes principales de Chatterbox?
- [ ] ¿Qué partes son dinámicas (variable input size)?
- [ ] ¿Hay operaciones no soportadas por ONNX?

### Exportación

- [ ] ¿Se puede exportar el modelo completo?
- [ ] ¿Se debe exportar por partes?
- [ ] ¿Qué versión de ONNX opset se requiere?

### Optimización

- [ ] ¿Cuál es el tamaño del modelo ONNX?
- [ ] ¿Se puede aplicar quantización INT8?
- [ ] ¿Hay optimizaciones específicas para NPU?

## Investigación Preliminar

### Chatterbox Architecture

```
[ Pendiente: Diagrama de arquitectura ]
```

### Componentes

| Componente | Exportable | Notas |
|------------|------------|-------|
| VoiceEncoder | ? | |
| T3 (LLM) | ? | |
| S3Gen | ? | |
| Decoder | ? | |

## Scripts de Exportación

```python
# TODO: export_to_onnx.py
```

## Resultados

[ Pendiente ]

## Conclusiones

[ Pendiente ]

## Referencias

- [ONNX Documentation](https://onnx.ai/onnx/)
- [ONNX Runtime](https://onnxruntime.ai/)
- [PyTorch ONNX Export](https://pytorch.org/docs/stable/onnx.html)
- [Chatterbox TTS](https://github.com/resemble-ai/chatterbox)
