# Chatterbox LoRA Fine-Tuning (Español Rioplatense)

Este repositorio contiene todo lo necesario para realizar un fine-tuning (LoRA) del modelo **Chatterbox TTS** utilizando el dataset **Orpheus LATAM** (voces argentinas).

El objetivo es adaptar el modelo multilingüe de Resemble AI para que genere audio con acento rioplatense natural.

## 📂 Estructura del Proyecto

```
chatterbox-es-latam/
├── src/
│   ├── lora_es_latam.py    # Script principal de entrenamiento
│   ├── dataset_orpheus.py  # Procesamiento del dataset Orpheus
│   └── test_inference.py   # Script para probar el modelo entrenado
├── runpod_train.sh         # Script de automatización para RunPod
├── fix_pkuseg.bat          # Script de corrección de instalación para Windows
├── requirements.txt        # Dependencias del proyecto
└── README.md               # Esta documentación
```

## 🚀 Instalación Local (Windows)

### 1. Prerrequisitos
- Python 3.10 o 3.11
- GPU NVIDIA (Recomendado: 16GB+ VRAM para training, 8GB+ para inferencia)
- [Git](https://git-scm.com/) instalado

### 2. Configuración

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/franclarke/chatterbox-es-latam.git
    cd chatterbox-es-latam
    ```

2.  **Crear entorno virtual:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instalar dependencias (IMPORTANTE):**
    Debido a un problema de compatibilidad con la librería `pkuseg` en Windows, debés seguir este orden exacto:

    ```cmd
    # 1. Instalar herramientas base
    pip install numpy cython setuptools wheel

    # 2. Ejecutar el script de corrección (compila pkuseg localmente)
    fix_pkuseg.bat

    # 3. Instalar el resto de dependencias
    pip install -r requirements.txt
    ```

4.  **Login en HuggingFace:**
    Necesario para descargar el modelo base y el dataset.
    ```bash
    huggingface-cli login
    ```

## ☁️ Entrenamiento en RunPod

Este repositorio está optimizado para correr en **RunPod** (pods con GPU NVIDIA, ej: A40, A6000, A100).

1.  **Crear Pod:** Elegí una imagen base de PyTorch (ej: `runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04`).
2.  **Subir código:** Podés clonar el repo o subir los archivos directamente.
3.  **Ejecutar entrenamiento:**
    Hemos preparado un script que instala todo, arregla dependencias y lanza el entrenamiento automáticamente.

    ```bash
    chmod +x runpod_train.sh
    ./runpod_train.sh
    ```

    *Este script guardará los logs en `logs/train_log.txt` para que puedas cerrar la terminal sin detener el proceso.*

## 🛠️ Uso

### Entrenamiento (Fine-Tuning)
Para iniciar el entrenamiento manualmente:
```bash
python -m src.lora_es_latam
```
*Configuraciones como `BATCH_SIZE`, `EPOCHS`, `LEARNING_RATE` se pueden editar directamente en `src/lora_es_latam.py`.*

### Inferencia (Prueba)
Una vez finalizado el entrenamiento, se generará la carpeta `checkpoints_lora/merged_model`. Para probarlo:

1.  Abrí `src/test_inference.py` y editá el texto si deseás.
2.  Ejecutá:
    ```bash
    python src/test_inference.py
    ```
3.  El audio generado se guardará como `test_es_ar.wav`.

## 📊 Monitoreo
Durante el entrenamiento, se genera un archivo `training_metrics.png` que se actualiza en tiempo real con gráficos de:
- Loss (Entrenamiento y Validación)
- Learning Rate
- Gradientes

## 🐛 Solución de Problemas Comunes

- **Error `pkuseg` / `numpy`:** Asegurate de haber corrido `fix_pkuseg.bat` (Windows) o usar `runpod_train.sh` (Linux) que manejan la compilación manual de esta librería.
- **Error `torchcodec`:** Si aparece este error, es porque `datasets` no detectó `soundfile`. Asegurate de haber instalado `requirements.txt` completo.
- **OOM (Out of Memory):** Reducí el `BATCH_SIZE` en `src/lora_es_latam.py` a 1.