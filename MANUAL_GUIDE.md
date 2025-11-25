# Guía Manual: Chatterbox ES LATAM

Esta guía te explica paso a paso cómo utilizar este repositorio para entrenar un modelo TTS con acento argentino usando el dataset Orpheus.

## 1. Preparación del Entorno

### Requisitos Previos
- Python 3.10+
- GPU NVIDIA (Recomendado: 16GB+ VRAM para training, 8GB+ para inferencia)
- Cuenta en HuggingFace (para descargar el dataset y modelo base)

### Instalación
1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/franclarke/chatterbox-es-latam.git
    cd chatterbox-es-latam
    ```

2.  **Crear entorno virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    # o
    .\venv\Scripts\activate   # Windows
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## 2. El Dataset: Orpheus LATAM

Utilizamos `GianDiego/latam-spanish-speech-orpheus-tts-24khz`.
- **Fuente:** HuggingFace Datasets.
- **Características:** Audio 24kHz, texto transcrito, metadatos de hablante.
- **Filtrado:** El script `src/lora_es_latam.py` filtra automáticamente por `nationality="AR"` para obtener solo voces argentinas.

**Nota:** No necesitas descargar el dataset manualmente; el script lo hace automáticamente la primera vez que se ejecuta (se guarda en `~/.cache/huggingface`).

## 3. Entrenamiento (Fine-Tuning)

El entrenamiento utiliza LoRA (Low-Rank Adaptation) para adaptar el modelo multilingüe al acento argentino.

### Ejecución Local
```bash
python -m src.lora_es_latam
```

### Ejecución en Runpod (Recomendado)
Si usas un pod en la nube:
1.  Subí todo el contenido del repo.
2.  Dale permisos de ejecución al script:
    ```bash
    chmod +x runpod_train.sh
    ```
3.  Ejecutalo:
    ```bash
    ./runpod_train.sh
    ```
    Esto guardará los logs en `logs/train_log.txt` para que puedas cerrar la terminal sin cortar el proceso.

### Monitoreo
El script genera un archivo `training_metrics.png` que se actualiza en tiempo real con gráficos de Loss, Learning Rate, etc. Podés abrirlo periódicamente para ver el progreso.

## 4. Checkpoints y Modelo Final

Durante el entrenamiento, se guardan checkpoints en `checkpoints_lora/`.
Al finalizar, se generan dos cosas importantes:

1.  **`checkpoints_lora/final_lora_adapter.pt`**: Solo los pesos del adaptador (liviano).
2.  **`checkpoints_lora/merged_model/`**: El modelo completo con los pesos fusionados. **Este es el que usaremos para inferencia.**

## 5. Inferencia (Prueba)

Una vez que tengas el modelo entrenado en `checkpoints_lora/merged_model`:

1.  Abrí `src/test_inference.py`.
2.  Editá el texto si querés probar otra frase:
    ```python
    text = "Che, me voy al laburo en bondi..."
    ```
3.  Ejecutalo:
    ```bash
    python src/test_inference.py
    ```
4.  Escuchá el archivo generado: `test_es_ar.wav`.

## Solución de Problemas Comunes

- **Out of Memory (OOM):** Bajá el `BATCH_SIZE` en `src/lora_es_latam.py` (línea 43) a 1.
- **Dataset Error:** Si falla la descarga, verificá tu conexión y que `huggingface_hub` esté logueado (`huggingface-cli login`).
- **Audio ruidoso:** Puede que el entrenamiento necesite más epochs o que el learning rate sea muy alto. Ajustá `EPOCHS` y `LEARNING_RATE` en el script.
