import inspect
from chatterbox.tts import ChatterboxTTS

print("Inspecting ChatterboxTTS.generate...")
try:
    sig = inspect.signature(ChatterboxTTS.generate)
    print(f"Signature: {sig}")
    print(f"Docstring: {ChatterboxTTS.generate.__doc__}")
except Exception as e:
    print(f"Could not inspect signature: {e}")
