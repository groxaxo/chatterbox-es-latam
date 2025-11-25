# Chatterbox ES LATAM

Este repositorio contiene el código para realizar **LoRA fine-tuning** del modelo `ResembleAI/chatterbox-multilingual`.

## Dataset
Se utiliza el dataset **Orpheus LATAM** (`GianDiego/latam-spanish-speech-orpheus-tts-24khz`) para entrenar el modelo en español latinoamericano.

## Output
El proceso de entrenamiento produce:
1. Un **LoRA adapter** que puede ser cargado sobre el modelo base.
2. Un **modelo mergeado** listo para inferencia.