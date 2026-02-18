# File: engine.py
# Core TTS model loading and speech generation logic.

import gc
import logging
import random
import inspect
import numpy as np
import torch
import torch.nn as nn
from typing import Optional, Tuple
from pathlib import Path

from chatterbox.tts import ChatterboxTTS  # Main TTS engine class
from chatterbox.models.s3gen.const import (
    S3GEN_SR,
)  # Default sample rate from the engine

# Defensive Turbo import - Turbo may not be available in older package versions
try:
    from chatterbox.tts_turbo import ChatterboxTurboTTS

    TURBO_AVAILABLE = True
except ImportError:
    ChatterboxTurboTTS = None
    TURBO_AVAILABLE = False

# Defensive bitsandbytes import for NF4 quantization
try:
    import bitsandbytes as bnb

    BNB_AVAILABLE = True
except ImportError:
    bnb = None
    BNB_AVAILABLE = False

# Import the singleton config_manager
from config import (
    config_manager,
    get_gpu_enable_tf32,
    get_gpu_cudnn_benchmark,
    get_gpu_use_bf16_inference,
    get_gpu_use_nf4_quantization,
    get_gpu_use_torch_compile,
)

logger = logging.getLogger(__name__)

# Log Turbo availability status at module load time
if TURBO_AVAILABLE:
    logger.info("ChatterboxTurboTTS is available in the installed chatterbox package.")
else:
    logger.info("ChatterboxTurboTTS not available in installed chatterbox package.")

if BNB_AVAILABLE:
    logger.info("bitsandbytes is available for NF4 quantization.")
else:
    logger.info("bitsandbytes not installed. NF4 quantization unavailable.")


def _apply_cuda_optimizations():
    """
    Applies GPU optimizations for CUDA devices.
    TF32 provides ~3x speedup on Ampere+ (compute capability >= 8.0, e.g. RTX 3090).
    On older architectures, TF32 flags are safely ignored.
    """
    if not torch.cuda.is_available():
        return

    # TF32 - provides ~3x speedup for float32 matmuls on Ampere+ with minimal precision loss
    if get_gpu_enable_tf32():
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        logger.info("Enabled TF32 tensor cores for Ampere+ GPU acceleration.")

    # cuDNN benchmark - auto-tunes convolution algorithms for consistent input sizes
    if get_gpu_cudnn_benchmark():
        torch.backends.cudnn.benchmark = True
        logger.info("Enabled cuDNN benchmark mode for convolution auto-tuning.")


def _quantize_model_nf4(model):
    """
    Replaces nn.Linear layers in the model with bitsandbytes Linear4bit (NF4)
    to reduce VRAM usage by ~4x while preserving quality.

    Only quantizes layers that are large enough to benefit.
    """
    if not BNB_AVAILABLE:
        logger.warning(
            "NF4 quantization requested but bitsandbytes is not installed. "
            "Install with: pip install bitsandbytes>=0.42.0"
        )
        return model

    device = next(model.parameters()).device
    quantized_count = 0
    # Skip tiny layers where quantization overhead outweighs VRAM savings
    min_features = config_manager.get_int("gpu_optimizations.nf4_min_features", 128)

    for name, module in list(model.named_modules()):
        for child_name, child in list(module.named_children()):
            if isinstance(child, nn.Linear):
                if child.in_features < min_features or child.out_features < min_features:
                    continue

                has_bias = child.bias is not None
                nf4_layer = bnb.nn.Linear4bit(
                    child.in_features,
                    child.out_features,
                    bias=has_bias,
                    compute_dtype=torch.bfloat16,
                    quant_type="nf4",
                )
                nf4_layer.weight = bnb.nn.Params4bit(
                    child.weight.data,
                    requires_grad=False,
                    quant_type="nf4",
                )
                if has_bias:
                    nf4_layer.bias = child.bias

                nf4_layer = nf4_layer.to(device)
                setattr(module, child_name, nf4_layer)
                quantized_count += 1

    logger.info(f"NF4 quantization applied to {quantized_count} linear layers.")
    return model

# Model selector whitelist - maps config values to model types
MODEL_SELECTOR_MAP = {
    # Original model selectors
    "chatterbox": "original",
    "original": "original",
    "resembleai/chatterbox": "original",
    # Turbo model selectors
    "chatterbox-turbo": "turbo",
    "turbo": "turbo",
    "resembleai/chatterbox-turbo": "turbo",
    # ES-LATAM model selectors (custom trained)
    "chatterbox-es-latam": "custom",
    "es-latam": "custom",
}

# Paralinguistic tags supported by Turbo model
TURBO_PARALINGUISTIC_TAGS = [
    "laugh",
    "chuckle",
    "sigh",
    "gasp",
    "cough",
    "clear throat",
    "sniff",
    "groan",
    "shush",
]

# --- Global Module Variables ---
chatterbox_model: Optional[ChatterboxTTS] = None
MODEL_LOADED: bool = False
model_device: Optional[str] = (
    None  # Stores the resolved device string ('cuda' or 'cpu')
)
_use_bf16_inference: bool = False  # Cached BF16 inference flag, set during model loading

# Track which model type is loaded
loaded_model_type: Optional[str] = None  # "original", "turbo", or "custom"
loaded_model_class_name: Optional[str] = None  # "ChatterboxTTS" or "ChatterboxTurboTTS"


def set_seed(seed_value: int):
    """
    Sets the seed for torch, random, and numpy for reproducibility.
    This is called if a non-zero seed is provided for generation.
    """
    torch.manual_seed(seed_value)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed_value)
        torch.cuda.manual_seed_all(seed_value)  # if using multi-GPU
    if torch.backends.mps.is_available():
        torch.mps.manual_seed(seed_value)
    random.seed(seed_value)
    np.random.seed(seed_value)
    logger.info(f"Global seed set to: {seed_value}")


def _test_cuda_functionality() -> bool:
    """
    Tests if CUDA is actually functional, not just available.

    Returns:
        bool: True if CUDA works, False otherwise.
    """
    if not torch.cuda.is_available():
        return False

    try:
        test_tensor = torch.tensor([1.0])
        test_tensor = test_tensor.cuda()
        test_tensor = test_tensor.cpu()
        return True
    except Exception as e:
        logger.warning(f"CUDA functionality test failed: {e}")
        return False


def _test_mps_functionality() -> bool:
    """
    Tests if MPS is actually functional, not just available.

    Returns:
        bool: True if MPS works, False otherwise.
    """
    if not torch.backends.mps.is_available():
        return False

    try:
        test_tensor = torch.tensor([1.0])
        test_tensor = test_tensor.to("mps")
        test_tensor = test_tensor.cpu()
        return True
    except Exception as e:
        logger.warning(f"MPS functionality test failed: {e}")
        return False


def _get_model_class(selector: str) -> tuple:
    """
    Determines which model class to use based on the config selector value.

    Args:
        selector: The value from config model.repo_id

    Returns:
        Tuple of (model_class, model_type_string)

    Raises:
        ImportError: If Turbo is selected but not available in the package
    """
    selector_normalized = selector.lower().strip()
    model_type = MODEL_SELECTOR_MAP.get(selector_normalized)

    if model_type == "turbo":
        if not TURBO_AVAILABLE:
            raise ImportError(
                f"Model selector '{selector}' requires ChatterboxTurboTTS, "
                f"but it is not available in the installed chatterbox package. "
                f"Please update the chatterbox-tts package to the latest version, "
                f"or use 'chatterbox' to select the original model."
            )
        logger.info(
            f"Model selector '{selector}' resolved to Turbo model (ChatterboxTurboTTS)"
        )
        return ChatterboxTurboTTS, "turbo"

    if model_type == "original":
        logger.info(
            f"Model selector '{selector}' resolved to Original model (ChatterboxTTS)"
        )
        return ChatterboxTTS, "original"

    if model_type == "custom":
        logger.info(
            f"Model selector '{selector}' resolved to Custom ES-LATAM model (ChatterboxTTS)"
        )
        return ChatterboxTTS, "custom"

    # Unknown selector - default to original with warning
    logger.warning(
        f"Unknown model selector '{selector}'. "
        f"Valid values: chatterbox, chatterbox-turbo, chatterbox-es-latam, original, turbo, es-latam, "
        f"ResembleAI/chatterbox, ResembleAI/chatterbox-turbo. "
        f"Defaulting to original ChatterboxTTS model."
    )
    return ChatterboxTTS, "original"


def get_model_info() -> dict:
    """
    Returns information about the currently loaded model.
    Used by the API to expose model details to the UI.

    Returns:
        Dictionary containing model information
    """
    is_cuda = model_device == "cuda"
    return {
        "loaded": MODEL_LOADED,
        "type": loaded_model_type,  # "original", "turbo", or "custom"
        "class_name": loaded_model_class_name,
        "device": model_device,
        "sample_rate": chatterbox_model.sr if chatterbox_model else None,
        "supports_paralinguistic_tags": loaded_model_type == "turbo",
        "available_paralinguistic_tags": (
            TURBO_PARALINGUISTIC_TAGS if loaded_model_type == "turbo" else []
        ),
        "turbo_available_in_package": TURBO_AVAILABLE,
        "gpu_optimizations": {
            "tf32_enabled": is_cuda and get_gpu_enable_tf32(),
            "cudnn_benchmark": is_cuda and get_gpu_cudnn_benchmark(),
            "bf16_inference": is_cuda and get_gpu_use_bf16_inference(),
            "nf4_quantization": is_cuda and get_gpu_use_nf4_quantization(),
            "torch_compile": is_cuda and get_gpu_use_torch_compile(),
            "bitsandbytes_available": BNB_AVAILABLE,
        },
    }


def load_model() -> bool:
    """
    Loads the TTS model.
    This version directly attempts to load from the Hugging Face repository (or its cache)
    using `from_pretrained`, bypassing the local `paths.model_cache` directory.
    Updates global variables `chatterbox_model`, `MODEL_LOADED`, and `model_device`.

    Returns:
        bool: True if the model was loaded successfully, False otherwise.
    """
    global chatterbox_model, MODEL_LOADED, model_device
    global loaded_model_type, loaded_model_class_name, _use_bf16_inference

    if MODEL_LOADED:
        logger.info("TTS model is already loaded.")
        return True

    try:
        # Determine processing device with robust CUDA detection and intelligent fallback
        device_setting = config_manager.get_string("tts_engine.device", "auto")

        if device_setting == "auto":
            if _test_cuda_functionality():
                resolved_device_str = "cuda"
                logger.info("CUDA functionality test passed. Using CUDA.")
            elif _test_mps_functionality():
                resolved_device_str = "mps"
                logger.info("MPS functionality test passed. Using MPS.")
            else:
                resolved_device_str = "cpu"
                logger.info("CUDA and MPS not functional or not available. Using CPU.")

        elif device_setting == "cuda":
            if _test_cuda_functionality():
                resolved_device_str = "cuda"
                logger.info("CUDA requested and functional. Using CUDA.")
            else:
                resolved_device_str = "cpu"
                logger.warning(
                    "CUDA was requested in config but functionality test failed. "
                    "PyTorch may not be compiled with CUDA support. "
                    "Automatically falling back to CPU."
                )

        elif device_setting == "mps":
            if _test_mps_functionality():
                resolved_device_str = "mps"
                logger.info("MPS requested and functional. Using MPS.")
            else:
                resolved_device_str = "cpu"
                logger.warning(
                    "MPS was requested in config but functionality test failed. "
                    "PyTorch may not be compiled with MPS support. "
                    "Automatically falling back to CPU."
                )

        elif device_setting == "cpu":
            resolved_device_str = "cpu"
            logger.info("CPU device explicitly requested in config. Using CPU.")

        else:
            logger.warning(
                f"Invalid device setting '{device_setting}' in config. "
                f"Defaulting to auto-detection."
            )
            if _test_cuda_functionality():
                resolved_device_str = "cuda"
            elif _test_mps_functionality():
                resolved_device_str = "mps"
            else:
                resolved_device_str = "cpu"
            logger.info(f"Auto-detection resolved to: {resolved_device_str}")

        model_device = resolved_device_str
        logger.info(f"Final device selection: {model_device}")

        # Apply CUDA GPU optimizations (TF32, cuDNN benchmark) before model loading
        if model_device == "cuda":
            _apply_cuda_optimizations()

        # Get the model selector from config
        model_selector = config_manager.get_string(
            "model.repo_id", "chatterbox-es-latam"
        )

        logger.info(f"Model selector from config: '{model_selector}'")

        try:
            # Determine which model class to use
            model_class, model_type = _get_model_class(model_selector)

            logger.info(
                f"Initializing {model_class.__name__} on device '{model_device}'..."
            )
            logger.info(f"Model type: {model_type}")
            if model_type == "turbo":
                logger.info(
                    f"Turbo model supports paralinguistic tags: {TURBO_PARALINGUISTIC_TAGS}"
                )

            # Resolve well-known aliases to explicit HuggingFace repo IDs.
            selector_normalized = model_selector.lower().strip()
            repo_aliases = {
                "chatterbox": "ResembleAI/chatterbox",
                "original": "ResembleAI/chatterbox",
                "resembleai/chatterbox": "ResembleAI/chatterbox",
                "chatterbox-turbo": "ResembleAI/chatterbox-turbo",
                "turbo": "ResembleAI/chatterbox-turbo",
                "resembleai/chatterbox-turbo": "ResembleAI/chatterbox-turbo",
            }
            resolved_repo_id = repo_aliases.get(selector_normalized, model_selector)
            logger.info(f"Resolved model repo/path for loading: '{resolved_repo_id}'")

            # Load from_pretrained, passing repo/path only when the installed API supports it.
            pretrained_signature = inspect.signature(model_class.from_pretrained)
            if "repo_id" in pretrained_signature.parameters:
                chatterbox_model = model_class.from_pretrained(
                    device=model_device, repo_id=resolved_repo_id
                )
            elif "pretrained_model_name_or_path" in pretrained_signature.parameters:
                chatterbox_model = model_class.from_pretrained(
                    device=model_device,
                    pretrained_model_name_or_path=resolved_repo_id,
                )
            elif "model_id" in pretrained_signature.parameters:
                chatterbox_model = model_class.from_pretrained(
                    device=model_device, model_id=resolved_repo_id
                )
            else:
                logger.warning(
                    "from_pretrained does not accept repo/path selection in this chatterbox version; "
                    "loading default pretrained weights."
                )
                chatterbox_model = model_class.from_pretrained(device=model_device)

            # Apply NF4 quantization if enabled (reduces VRAM ~4x on CUDA)
            if model_device == "cuda" and get_gpu_use_nf4_quantization():
                logger.info("Applying NF4 4-bit quantization to model...")
                _quantize_model_nf4(chatterbox_model)

            # Apply torch.compile if enabled (PyTorch 2.x JIT optimization)
            if model_device == "cuda" and get_gpu_use_torch_compile():
                try:
                    if hasattr(chatterbox_model, "t3") and hasattr(
                        chatterbox_model.t3, "tfmr"
                    ):
                        chatterbox_model.t3.tfmr = torch.compile(
                            chatterbox_model.t3.tfmr
                        )
                        logger.info(
                            "Applied torch.compile to transformer backbone."
                        )
                except Exception as e_compile:
                    logger.warning(
                        f"torch.compile failed (non-fatal): {e_compile}"
                    )

            # Store model metadata
            loaded_model_type = model_type
            loaded_model_class_name = model_class.__name__

            logger.info(f"Successfully loaded {model_class.__name__} on {model_device}")
            logger.info(f"Model sample rate: {chatterbox_model.sr} Hz")
        except ImportError as e_import:
            logger.error(
                f"Failed to load model due to import error: {e_import}",
                exc_info=True,
            )
            chatterbox_model = None
            MODEL_LOADED = False
            return False
        except Exception as e_hf:
            logger.error(
                f"Failed to load model using from_pretrained: {e_hf}",
                exc_info=True,
            )
            chatterbox_model = None
            MODEL_LOADED = False
            return False

        MODEL_LOADED = True
        # Cache BF16 inference flag to avoid per-call config lookups
        _use_bf16_inference = model_device == "cuda" and get_gpu_use_bf16_inference()
        if chatterbox_model:
            logger.info(
                f"TTS Model loaded successfully on {model_device}. Engine sample rate: {chatterbox_model.sr} Hz."
            )
        else:
            logger.error(
                "Model loading sequence completed, but chatterbox_model is None. This indicates an unexpected issue."
            )
            MODEL_LOADED = False
            return False

        return True

    except Exception as e:
        logger.error(
            f"An unexpected error occurred during model loading: {e}", exc_info=True
        )
        chatterbox_model = None
        MODEL_LOADED = False
        return False


def synthesize(
    text: str,
    audio_prompt_path: Optional[str] = None,
    temperature: float = 0.8,
    exaggeration: float = 0.5,
    cfg_weight: float = 0.5,
    seed: int = 0,
) -> Tuple[Optional[torch.Tensor], Optional[int]]:
    """
    Synthesizes audio from text using the loaded TTS model.

    Args:
        text: The text to synthesize.
        audio_prompt_path: Path to an audio file for voice cloning or predefined voice.
        temperature: Controls randomness in generation.
        exaggeration: Controls expressiveness.
        cfg_weight: Classifier-Free Guidance weight.
        seed: Random seed for generation. If 0, default randomness is used.
              If non-zero, a global seed is set for reproducibility.

    Returns:
        A tuple containing the audio waveform (torch.Tensor) and the sample rate (int),
        or (None, None) if synthesis fails.
    """
    global chatterbox_model

    if not MODEL_LOADED or chatterbox_model is None:
        logger.error("TTS model is not loaded. Cannot synthesize audio.")
        return None, None

    try:
        # Set seed globally if a specific seed value is provided and is non-zero.
        if seed != 0:
            logger.info(f"Applying user-provided seed for generation: {seed}")
            set_seed(seed)
        else:
            logger.info(
                "Using default (potentially random) generation behavior as seed is 0."
            )

        logger.debug(
            f"Synthesizing with params: audio_prompt='{audio_prompt_path}', temp={temperature}, "
            f"exag={exaggeration}, cfg_weight={cfg_weight}, seed_applied_globally_if_nonzero={seed}"
        )

        # Call the core model's generate method, with optional BF16 autocast for Ampere GPUs
        if _use_bf16_inference:
            with torch.amp.autocast("cuda", dtype=torch.bfloat16):
                wav_tensor = chatterbox_model.generate(
                    text=text,
                    audio_prompt_path=audio_prompt_path,
                    temperature=temperature,
                    exaggeration=exaggeration,
                    cfg_weight=cfg_weight,
                )
        else:
            wav_tensor = chatterbox_model.generate(
                text=text,
                audio_prompt_path=audio_prompt_path,
                temperature=temperature,
                exaggeration=exaggeration,
                cfg_weight=cfg_weight,
            )

        # The ChatterboxTTS.generate method already returns a CPU tensor.
        # Convert to numpy array for compatibility with utils.encode_audio
        if isinstance(wav_tensor, torch.Tensor):
            wav_tensor = wav_tensor.numpy()

        return wav_tensor, chatterbox_model.sr

    except Exception as e:
        logger.error(f"Error during TTS synthesis: {e}", exc_info=True)
        return None, None


def generate(
    text: str,
    voice_source_path: Optional[str] = None,
    temperature: float = 0.8,
    exaggeration: float = 0.5,
    cfg_weight: float = 0.5,
    seed: int = 0,
    speed_factor: float = 1.0,
    language: str = "es",
) -> Tuple[Optional[torch.Tensor], Optional[int]]:
    """
    Wrapper for synthesize to match server.py expectation.
    """
    wav_tensor, sr = synthesize(
        text=text,
        audio_prompt_path=voice_source_path,
        temperature=temperature,
        exaggeration=exaggeration,
        cfg_weight=cfg_weight,
        seed=seed,
    )

    if wav_tensor is not None and speed_factor != 1.0:
        import utils

        wav_tensor, sr = utils.apply_speed_factor(wav_tensor, sr, speed_factor)

    return wav_tensor, sr


def reload_model() -> bool:
    """
    Unloads the current model, clears GPU memory, and reloads the model
    based on the current configuration. Used for hot-swapping models
    without restarting the server process.

    Returns:
        bool: True if the new model loaded successfully, False otherwise.
    """
    global \
        chatterbox_model, \
        MODEL_LOADED, \
        model_device, \
        loaded_model_type, \
        loaded_model_class_name

    logger.info("Initiating model hot-swap/reload sequence...")

    # 1. Unload existing model
    if chatterbox_model is not None:
        logger.info("Unloading existing TTS model from memory...")
        del chatterbox_model
        chatterbox_model = None

    # 2. Reset state flags
    MODEL_LOADED = False
    loaded_model_type = None
    loaded_model_class_name = None

    # 3. Force Python Garbage Collection
    gc.collect()
    logger.info("Python garbage collection completed.")

    # 4. Clear GPU Cache (CUDA)
    if torch.cuda.is_available():
        logger.info("Clearing CUDA cache...")
        torch.cuda.empty_cache()

    # 5. Clear GPU Cache (MPS - Apple Silicon)
    if torch.backends.mps.is_available():
        try:
            torch.mps.empty_cache()
            logger.info("Cleared MPS cache.")
        except AttributeError:
            # Older PyTorch versions may not have mps.empty_cache()
            logger.debug(
                "torch.mps.empty_cache() not available in this PyTorch version."
            )

    # 6. Reload model from the (now updated) configuration
    logger.info("Memory cleared. Reloading model from updated config...")
    return load_model()


# --- End File: engine.py ---
