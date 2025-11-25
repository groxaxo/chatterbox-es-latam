#!/bin/bash

# Exit on error
set -e

# Create logs directory
mkdir -p logs

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run training with logging
echo "Starting training..."
# Use stdbuf to unbuffer output so it appears in log immediately
stdbuf -oL python -m src.lora_es_latam 2>&1 | tee logs/train_log.txt

echo "Training completed. Log saved to logs/train_log.txt"
