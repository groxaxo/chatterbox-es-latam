# Quick Start

Guía rápida para comenzar con Chatterbox ES-LATAM.

## Desarrollo Local

### Requisitos
- Python 3.10+
- Node.js 18+
- GPU con CUDA (opcional, para servidor)

### 1. Clonar Repositorio

```bash
git clone https://github.com/tu-usuario/chatterbox-es-latam.git
cd chatterbox-es-latam
```

### 2. Iniciar Servidor

```bash
# Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
cd server
uvicorn main:app --reload --port 8000
```

Servidor disponible en: http://localhost:8000

### 3. Probar API

```bash
# Health check
curl http://localhost:8000/health

# Ver documentación API
# Abrir en navegador: http://localhost:8000/docs
```

### 4. Demo Web

```bash
# En otra terminal
cd web
npm install
npm run dev
```

Demo disponible en: http://localhost:5173

## Uso Básico

### Enrollar una Voz

```bash
curl -X POST "http://localhost:8000/api/v1/enroll" \
  -F "file=@mi_voz.wav" \
  -F "name=Mi Voz"
```

### Generar Audio (Demo)

```bash
curl -X POST "http://localhost:8000/api/v1/infer" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hola mundo", "voice_id": "voice_xxx"}'
```

## Próximos Pasos

1. [Configurar servidor para producción](./server/DEPLOYMENT.md)
2. [Entrenar modelo personalizado](./server/TRAINING.md)
3. [Integrar en tu aplicación](./integration/SAI.md)

## Troubleshooting

### "CUDA not available"
El servidor funcionará en CPU (más lento). Para GPU:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### "Model not found"
Verificar que el modelo está en la ruta correcta:
```bash
ls checkpoints_lora/merged_model/
```

### Puerto en uso
```bash
# Cambiar puerto
uvicorn main:app --port 8001
```
