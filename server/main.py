from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from .core.config import settings
from .api.v1 import endpoints
from .services.voice_encoder import voice_encoder_service
from .services.inference_service import inference_service

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files
# /static/output -> server/data/audio_output
# /static/input -> server/data/audio_input
output_dir = os.path.join("server", "data", "audio_output")
input_dir = os.path.join("server", "data", "audio_input")
os.makedirs(output_dir, exist_ok=True)
os.makedirs(input_dir, exist_ok=True)

app.mount("/static/output", StaticFiles(directory=output_dir), name="output")
app.mount("/static/input", StaticFiles(directory=input_dir), name="input")

# Routes
app.include_router(endpoints.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    # Pre-load models on startup
    voice_encoder_service.initialize()
    inference_service.initialize()

@app.get("/health")
def health_check():
    return {"status": "ok", "device": settings.DEVICE}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
