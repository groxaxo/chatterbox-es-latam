# Deployment Guide

## Opciones de Deployment

| Opción | Uso | GPU | Costo |
|--------|-----|-----|-------|
| **Local** | Desarrollo | Opcional | Gratis |
| **Docker** | Desarrollo/Staging | Opcional | Gratis |
| **RunPod** | Producción | ✅ | ~$0.20/hr |
| **AWS/GCP** | Producción enterprise | ✅ | Variable |

---

## Local Development

### Requisitos
- Python 3.10+
- CUDA 11.8+ (opcional, para GPU)
- 8GB RAM (16GB recomendado)

### Setup

```bash
# Clonar repo
git clone https://github.com/tu-usuario/chatterbox-es-latam.git
cd chatterbox-es-latam

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar
cp server/.env.example server/.env
# Editar server/.env

# Ejecutar
cd server
uvicorn main:app --reload --port 8000
```

### Variables de Entorno

```env
PROJECT_NAME="Chatterbox ES-LATAM API"
API_V1_STR="/api/v1"
MODEL_PATH="../checkpoints_lora/merged_model"
DEVICE="cuda"  # "cpu" si no hay GPU
SAMPLE_RATE=24000
```

---

## Docker Deployment

### Dockerfile

```dockerfile
# Dockerfile
FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY server/ ./server/
COPY checkpoints_lora/ ./checkpoints_lora/

# Crear directorios de datos
RUN mkdir -p server/data/audio_input server/data/audio_output

# Variables de entorno
ENV MODEL_PATH="/app/checkpoints_lora/merged_model"
ENV DEVICE="cuda"

# Puerto
EXPOSE 8000

# Comando
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./server/data:/app/server/data
    environment:
      - MODEL_PATH=/app/checkpoints_lora/merged_model
      - DEVICE=cuda
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped
```

### Comandos

```bash
# Build
docker-compose build

# Run
docker-compose up -d

# Logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## RunPod Deployment

[RunPod](https://runpod.io) es ideal para producción con GPU.

### Setup

1. **Crear cuenta** en runpod.io

2. **Crear Pod**:
   - Template: `runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel`
   - GPU: RTX 3090 o A4000 (mínimo)
   - Disk: 50GB+

3. **Configurar Pod**:

```bash
# Conectar via SSH
ssh root@<pod-ip>

# Clonar repo
git clone https://github.com/tu-usuario/chatterbox-es-latam.git
cd chatterbox-es-latam

# Setup
pip install -r requirements.txt

# Descargar modelo (si no está en repo)
# python scripts/download_model.py

# Ejecutar
cd server
nohup uvicorn main:app --host 0.0.0.0 --port 8000 &
```

4. **Exponer puerto**:
   - En RunPod dashboard, exponer puerto 8000
   - Obtendrás URL pública: `https://xxxxx-8000.proxy.runpod.net`

### Persistencia

Para que los datos persistan entre reinicios:

```bash
# Guardar en volumen persistente
ln -s /workspace/data /root/chatterbox-es-latam/server/data
```

---

## AWS Deployment

### EC2 con GPU

1. **Instancia recomendada**: `g4dn.xlarge` (T4 GPU)

2. **AMI**: Deep Learning AMI (Ubuntu)

3. **Security Groups**:
   - Inbound: 8000 (API), 22 (SSH)

4. **Setup**:

```bash
# SSH a instancia
ssh -i key.pem ubuntu@<ip>

# Activar conda
source activate pytorch

# Clonar y ejecutar
git clone https://github.com/tu-usuario/chatterbox-es-latam.git
cd chatterbox-es-latam
pip install -r requirements.txt
cd server
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Con Load Balancer (Producción)

```
[Route 53] → [ALB] → [EC2 g4dn.xlarge]
                   → [EC2 g4dn.xlarge] (backup)
```

---

## Nginx Reverse Proxy

Para producción con HTTPS:

```nginx
# /etc/nginx/sites-available/chatterbox
server {
    listen 80;
    server_name api.tudominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name api.tudominio.com;

    ssl_certificate /etc/letsencrypt/live/api.tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.tudominio.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Para uploads grandes (audio)
        client_max_body_size 50M;
    }
}
```

---

## Monitoreo

### Health Check

```bash
# Verificar que el servidor está corriendo
curl http://localhost:8000/health
```

### Logs

```bash
# Docker
docker-compose logs -f

# Systemd
journalctl -u chatterbox -f

# Archivo
tail -f /var/log/chatterbox/app.log
```

### Métricas (Futuro)

- Prometheus + Grafana para métricas
- Sentry para error tracking

---

## Troubleshooting

### CUDA out of memory

```bash
# Verificar uso de GPU
nvidia-smi

# Reducir batch size o usar modelo más pequeño
```

### Puerto en uso

```bash
# Encontrar proceso
lsof -i :8000

# Matar proceso
kill -9 <PID>
```

### Modelo no carga

```bash
# Verificar path
ls -la checkpoints_lora/merged_model/

# Verificar permisos
chmod -R 755 checkpoints_lora/
```
