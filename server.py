# File: server.py
# Main FastAPI application for Chatterbox ES-LATAM TTS Server.
# Based on chatterbox-tts-server but adapted for Spanish LATAM model

import os
import io
import logging
import logging.handlers
import shutil
import time
import uuid
import yaml
import numpy as np
import librosa
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any, Literal
import webbrowser
import threading

from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    File,
    UploadFile,
    Form,
    BackgroundTasks,
)
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    StreamingResponse,
    FileResponse,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# Internal imports
from config import (
    config_manager,
    get_host,
    get_port,
    get_log_file_path,
    get_output_path,
    get_reference_audio_path,
    get_predefined_voices_path,
    get_ui_title,
    get_gen_default_temperature,
    get_gen_default_exaggeration,
    get_gen_default_cfg_weight,
    get_gen_default_seed,
    get_gen_default_speed_factor,
    get_gen_default_language,
    get_audio_sample_rate,
    get_full_config_for_template,
    get_audio_output_format,
)

import engine
from models import (
    CustomTTSRequest,
    ErrorResponse,
    UpdateStatusResponse,
)
import utils

from pydantic import BaseModel, Field


class OpenAISpeechRequest(BaseModel):
    model: str
    input_: str = Field(..., alias="input")
    voice: str
    response_format: Literal["wav", "opus", "mp3"] = "wav"
    speed: float = 1.0
    seed: Optional[int] = None


# Logging Configuration
log_file_path_obj = get_log_file_path()
log_file_max_size_mb = config_manager.get_int("server.log_file_max_size_mb", 10)
log_backup_count = config_manager.get_int("server.log_file_backup_count", 5)

log_file_path_obj.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.handlers.RotatingFileHandler(
            str(log_file_path_obj),
            maxBytes=log_file_max_size_mb * 1024 * 1024,
            backupCount=log_backup_count,
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("watchfiles").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Global Variables & Application Setup
startup_complete_event = threading.Event()


def _delayed_browser_open(host: str, port: int):
    """Opens web browser after startup"""
    try:
        startup_complete_event.wait(timeout=30)
        if not startup_complete_event.is_set():
            logger.warning("Server startup did not complete within timeout.")
            return

        time.sleep(1.5)
        display_host = "localhost" if host == "0.0.0.0" else host
        browser_url = f"http://{display_host}:{port}/"
        logger.info(f"Opening browser to: {browser_url}")
        webbrowser.open(browser_url)
    except Exception as e:
        logger.error(f"Failed to open browser: {e}", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages application startup and shutdown"""
    logger.info("Chatterbox ES-LATAM TTS Server: Initializing...")
    try:
        logger.info(f"Configuration loaded. Log file: {get_log_file_path()}")

        paths_to_ensure = [
            get_output_path(),
            get_reference_audio_path(),
            get_predefined_voices_path(),
            Path("ui"),
            config_manager.get_path(
                "paths.model_cache", "./model_cache", ensure_absolute=True
            ),
        ]
        for p in paths_to_ensure:
            p.mkdir(parents=True, exist_ok=True)

        if not engine.load_model():
            logger.critical(
                "CRITICAL: TTS Model failed to load. Server might not function correctly."
            )
        else:
            logger.info("TTS Model loaded successfully.")
            host_address = get_host()
            server_port = get_port()
            browser_thread = threading.Thread(
                target=lambda: _delayed_browser_open(host_address, server_port),
                daemon=True,
            )
            browser_thread.start()

        logger.info("Application startup complete.")
        startup_complete_event.set()
        yield
    except Exception as e_startup:
        logger.error(f"ERROR during startup: {e_startup}", exc_info=True)
        startup_complete_event.set()
        yield
    finally:
        logger.info("Application shutdown initiated...")
        logger.info("Application shutdown complete.")


# FastAPI Application Instance
app = FastAPI(
    title=get_ui_title(),
    description="Servidor TTS Chatterbox ES-LATAM con interfaz avanzada",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "null"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Static Files and HTML Templates
ui_static_path = Path(__file__).parent / "ui"
if ui_static_path.is_dir():
    app.mount("/ui", StaticFiles(directory=ui_static_path), name="ui_static_assets")
else:
    logger.warning(f"UI directory not found at '{ui_static_path}'.")

if (ui_static_path / "vendor").is_dir():
    app.mount(
        "/vendor", StaticFiles(directory=ui_static_path / "vendor"), name="vendor_files"
    )

outputs_static_path = get_output_path(ensure_absolute=True)
try:
    app.mount(
        "/outputs",
        StaticFiles(directory=str(outputs_static_path)),
        name="generated_outputs",
    )
except RuntimeError as e:
    logger.error(f"Failed to mount /outputs directory: {e}")

templates = Jinja2Templates(directory=str(ui_static_path))


@app.get("/", include_in_schema=False)
async def root_ui():
    """Serve the main UI from the server root path."""
    index_file = ui_static_path / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="UI index file not found")
    return FileResponse(index_file)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": engine.MODEL_LOADED,
        "device": str(engine.model_device) if engine.model_device else "unknown",
    }


def get_available_voices_list():
    """Helper to list voices from the voices directory"""
    voices_path = get_predefined_voices_path()
    voices = []

    # Common audio extensions
    extensions = {".wav", ".mp3", ".opus", ".flac", ".m4a"}

    if voices_path.exists():
        for file in voices_path.iterdir():
            if file.is_file() and file.suffix.lower() in extensions:
                voices.append(
                    {"id": file.name, "name": file.stem.replace("_", " ").title()}
                )

    # Sort by name
    voices.sort(key=lambda x: x["name"])
    return voices


@app.get("/v1/audio/voices")
@app.get("/v1/voices")
async def list_voices():
    """List available voices for Open-WebUI compatibility"""
    return {"voices": get_available_voices_list()}


@app.get("/v1/audio/models")
@app.get("/v1/models")
async def list_models():
    """List available models for Open-WebUI / OpenAI compatibility"""
    # For this server, we mostly use a single model identified as 'chatterbox-es-latam'
    # but we also expose 'tts-1' for default compatibility.
    models_list = [
        {
            "id": "chatterbox-es-latam",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "chatterbox",
        },
        {
            "id": "tts-1",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "openai",
        },
    ]

    # Open-WebUI might expect a simple list under "models" or the OpenAI "data" format
    return {"models": models_list, "data": models_list, "object": "list"}


@app.post("/v1/audio/speech")
async def openai_compatible_tts(request: OpenAISpeechRequest):
    """OpenAI-compatible TTS endpoint"""
    logger.info(f"OpenAI API request: model={request.model}, voice={request.voice}")

    # Map request to internal format
    voice_path = get_predefined_voices_path() / request.voice
    if not voice_path.exists():
        # Try adding .wav extension
        voice_path = get_predefined_voices_path() / f"{request.voice}.wav"
        if not voice_path.exists():
            raise HTTPException(
                status_code=404, detail=f"Voice '{request.voice}' not found"
            )

    # Generate audio
    params = {
        "temperature": get_gen_default_temperature(),
        "exaggeration": get_gen_default_exaggeration(),
        "cfg_weight": get_gen_default_cfg_weight(),
        "seed": request.seed if request.seed else get_gen_default_seed(),
        "speed_factor": request.speed,
        "language": get_gen_default_language(),
    }

    audio_array, sample_rate = engine.generate(
        text=request.input_, voice_source_path=str(voice_path), **params
    )

    if audio_array is None:
        raise HTTPException(status_code=500, detail="Audio generation failed")

    # Encode audio
    audio_bytes = utils.encode_audio(
        audio_array, sample_rate, output_format=request.response_format
    )

    if audio_bytes is None:
        raise HTTPException(status_code=500, detail="Audio encoding failed")

    media_type_map = {"wav": "audio/wav", "opus": "audio/opus", "mp3": "audio/mpeg"}

    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type=media_type_map.get(request.response_format, "audio/wav"),
    )


@app.post("/tts")
async def custom_tts(request: CustomTTSRequest):
    """Custom TTS endpoint with advanced features"""
    logger.info(
        f"TTS request: mode={request.voice_mode}, text_length={len(request.text)}"
    )

    # Determine voice source
    if request.voice_mode == "predefined":
        if not request.predefined_voice_id:
            raise HTTPException(status_code=400, detail="predefined_voice_id required")
        voice_path = get_predefined_voices_path() / request.predefined_voice_id
    else:  # clone mode
        if not request.reference_audio_filename:
            raise HTTPException(
                status_code=400, detail="reference_audio_filename required"
            )
        voice_path = get_reference_audio_path() / request.reference_audio_filename

    if not voice_path.exists():
        raise HTTPException(
            status_code=404, detail=f"Voice file not found: {voice_path}"
        )

    # Prepare generation parameters
    params = {
        "temperature": request.temperature
        if request.temperature is not None
        else get_gen_default_temperature(),
        "exaggeration": request.exaggeration
        if request.exaggeration is not None
        else get_gen_default_exaggeration(),
        "cfg_weight": request.cfg_weight
        if request.cfg_weight is not None
        else get_gen_default_cfg_weight(),
        "seed": request.seed if request.seed is not None else get_gen_default_seed(),
        "speed_factor": request.speed_factor
        if request.speed_factor is not None
        else get_gen_default_speed_factor(),
        "language": request.language
        if request.language
        else get_gen_default_language(),
    }

    # Generate audio (single pass or chunked by sentence boundaries)
    text_chunks = [request.text]
    if request.split_text:
        chunk_size = request.chunk_size if request.chunk_size is not None else 120
        chunked_text = utils.chunk_text_by_sentences(request.text, chunk_size)
        if chunked_text:
            text_chunks = chunked_text
        logger.info(
            f"Chunking enabled: generated {len(text_chunks)} chunk(s) with chunk_size={chunk_size}"
        )

    generated_chunks = []
    sample_rate = None
    for chunk in text_chunks:
        chunk_audio, chunk_sample_rate = engine.generate(
            text=chunk, voice_source_path=str(voice_path), **params
        )
        if chunk_audio is None:
            raise HTTPException(status_code=500, detail="Audio generation failed")
        if sample_rate is None:
            sample_rate = chunk_sample_rate
        elif chunk_sample_rate != sample_rate:
            raise HTTPException(
                status_code=500,
                detail="Audio generation failed due to sample rate mismatch across chunks",
            )
        generated_chunks.append(np.asarray(chunk_audio).squeeze())

    audio_array = (
        generated_chunks[0]
        if len(generated_chunks) == 1
        else np.concatenate(generated_chunks)
    )

    # Encode audio
    output_format = (
        request.output_format if request.output_format else get_audio_output_format()
    )
    audio_bytes = utils.encode_audio(
        audio_array, sample_rate, output_format=output_format
    )

    if audio_bytes is None:
        raise HTTPException(status_code=500, detail="Audio encoding failed")

    media_type_map = {"wav": "audio/wav", "opus": "audio/opus", "mp3": "audio/mpeg"}

    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type=media_type_map.get(output_format, "audio/wav"),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=get_host(), port=get_port())
