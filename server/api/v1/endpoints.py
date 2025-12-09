import os
import time
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from ...schemas.enrollment import VoiceEnrollmentResponse, ErrorResponse, VoiceMetadata, InferenceRequest, InferenceResponse, InferenceHistoryItem
from ...services.audio_processor import audio_processor
from ...services.voice_encoder import voice_encoder_service
from ...services.storage_service import storage_service
from ...services.inference_service import inference_service
from ...core.config import settings

router = APIRouter()

@router.post("/enroll", response_model=VoiceEnrollmentResponse, responses={400: {"model": ErrorResponse}})
async def enroll_voice(
    file: UploadFile = File(...),
    name: str = Form(...)
):
    """
    Enroll a new voice from an audio file.
    """
    start_time = time.time()
    
    # 1. Process Audio
    wav, duration = await audio_processor.process_upload(file)
    
    # 2. Compute Embedding (Still useful for future ONNX, even if PyTorch uses ref audio)
    embedding = voice_encoder_service.compute_embedding(wav)
    
    # 3. Save Reference Audio
    import soundfile as sf
    timestamp = int(time.time())
    safe_name = "".join([c for c in name if c.isalnum() or c in ('-', '_')]).lower()
    ref_filename = f"ref_{safe_name}_{timestamp}.wav"
    ref_path = os.path.join(storage_service.audio_input_dir, ref_filename)
    sf.write(ref_path, wav, settings.SAMPLE_RATE)
    
    enrollment_time = time.time() - start_time
    
    # 4. Persist
    metadata = storage_service.save_voice(
        name=name,
        embedding=embedding,
        enrollment_time=enrollment_time,
        ref_audio_path=ref_filename
    )
    
    return VoiceEnrollmentResponse(
        voice_id=embedding,
        metadata=metadata,
        status="success"
    )

@router.get("/voices", response_model=List[VoiceMetadata])
def list_voices():
    return storage_service.list_voices()

@router.delete("/voices/{voice_id}")
def delete_voice(voice_id: str):
    storage_service.delete_voice(voice_id)
    return {"status": "success", "message": "Voice deleted"}

@router.post("/infer", response_model=InferenceResponse)
def infer_audio(request: InferenceRequest):
    # 1. Get Metadata to find ref audio
    metadata = storage_service.get_voice_metadata(request.voice_id)
    if metadata is None:
        raise HTTPException(status_code=404, detail="Voice not found")
        
    if not metadata.ref_audio_path:
        raise HTTPException(status_code=400, detail="Voice has no reference audio for inference")
        
    full_ref_path = os.path.join(storage_service.audio_input_dir, metadata.ref_audio_path)
    if not os.path.exists(full_ref_path):
        raise HTTPException(status_code=404, detail="Reference audio file missing")

    # 2. Generate Dual
    try:
        results = inference_service.generate_dual(
            text=request.text,
            ref_audio_path=full_ref_path,
            temperature=request.temperature
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")
        
    # 3. Save Audio & History
    saved_paths = storage_service.save_inference_dual(
        lora_wav=results["lora"][0],
        base_wav=results["base"][0],
        sample_rate=24000,
        text=request.text,
        voice_id=request.voice_id,
        lora_time=results["lora"][1],
        base_time=results["base"][1]
    )
    
    url_lora = f"/static/output/{os.path.basename(saved_paths['lora_path'])}"
    url_base = f"/static/output/{os.path.basename(saved_paths['base_path'])}"
    
    return InferenceResponse(
        audio_url_lora=url_lora,
        inference_time_lora=results["lora"][1],
        audio_url_base=url_base,
        inference_time_base=results["base"][1],
        status="success"
    )

@router.get("/history", response_model=List[InferenceHistoryItem])
def list_history():
    return storage_service.list_history()

@router.delete("/history/{history_id}")
def delete_history(history_id: str):
    storage_service.delete_history_item(history_id)
    return {"status": "success", "message": "History item deleted"}

