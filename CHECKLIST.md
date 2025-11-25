# Checklist de Verificación Manual

Antes de lanzar el entrenamiento en Runpod o en tu máquina local, asegurate de completar estos pasos para evitar errores costosos.

## 1. Verificación de Dependencias
- [ ] **Instalación:** Ejecutá `pip install -r requirements.txt` y verificá que no haya errores de conflictos.
- [ ] **HuggingFace Login:** Ejecutá `huggingface-cli login` y asegurate de tener acceso.

## 2. Verificación de Datos (Dry Run)
- [ ] **Dataset Download:** Ejecutá este pequeño script en python para verificar que el dataset baja y se puede leer:
    ```python
    from datasets import load_dataset
    ds = load_dataset("GianDiego/latam-spanish-speech-orpheus-tts-24khz", split="train", streaming=True)
    print(next(iter(ds)))
    ```
- [ ] **Dataset Class:** Verificá que `src/dataset_orpheus.py` procese bien un item. Creá un archivo `test_dataset.py`:
    ```python
    from datasets import load_dataset
    from src.dataset_orpheus import HFOrpheusDataset
    from chatterbox.tts import ChatterboxTTS
    
    model = ChatterboxTTS.from_pretrained("ResembleAI/chatterbox-multilingual")
    ds = load_dataset("GianDiego/latam-spanish-speech-orpheus-tts-24khz", split="train")
    my_ds = HFOrpheusDataset(ds, model.tokenizer)
    item = my_ds[0]
    print("Audio shape:", item['audio'].shape)
    print("Text:", item['text'])
    ```
    *Debería imprimir shapes consistentes (aprox 20s * 24000 = 480000 muestras).*

## 3. Verificación de Entrenamiento (Short Run)
- [ ] **Prueba de 1 Epoch:** Editá `src/lora_es_latam.py` temporalmente:
    - `EPOCHS = 1`
    - `dataset.select(range(10))` (para usar solo 10 muestras)
    - Ejecutá `python -m src.lora_es_latam`.
    - **Objetivo:** Verificar que no explote por memoria (OOM) o errores de dimensiones en `compute_loss`.

## 4. Verificación de Inferencia
- [ ] **Test Script:** Si el paso 3 generó `checkpoints_lora/merged_model`, ejecutá `python src/test_inference.py`.
- [ ] **Audio Check:** Escuchá `test_es_ar.wav`. No importan la calidad (será mala con 1 epoch), solo que se genere audio válido (no silencio, no estática pura).

## 5. Configuración Final
- [ ] **Restaurar Valores:** Si hiciste el paso 3, acordate de volver `EPOCHS` y el dataset a sus valores originales en `src/lora_es_latam.py`.
- [ ] **Runpod Script:** Verificá que `runpod_train.sh` tenga permisos de ejecución (`chmod +x runpod_train.sh`).

## 6. Monitoreo
- [ ] **Logs:** Ubicá dónde se guardan los logs (`logs/train_log.txt`) y tené a mano el comando para verlos en vivo (`tail -f logs/train_log.txt`).
