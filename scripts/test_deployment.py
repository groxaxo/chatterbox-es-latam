import requests
import json
import time

BASE_URL = "http://0.0.0.0:8004"


def test_health():
    print(f"Testing Health Check at {BASE_URL}/health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ Health check failed with status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed with error: {e}")
        return False


def test_tts_generation():
    print(f"\nTesting TTS Generation at {BASE_URL}/v1/audio/speech...")
    payload = {
        "model": "chatterbox-es-latam",
        "input": "Hola, esto es una prueba con la voz de Brenda.",
        "voice": "brenda",
        "response_format": "wav",
        "speed": 1.0,
    }

    start_time = time.time()
    try:
        response = requests.post(f"{BASE_URL}/v1/audio/speech", json=payload)
        end_time = time.time()

        if response.status_code == 200:
            audio_size = len(response.content)
            print(f"✅ TTS Generation passed!")
            print(f"   Time taken: {end_time - start_time:.2f} seconds")
            print(f"   Audio size: {audio_size} bytes")

            with open("test_output.wav", "wb") as f:
                f.write(response.content)
            print("   Saved audio to test_output.wav")
            return True
        else:
            print(f"❌ TTS Generation failed with status code: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ TTS Generation failed with error: {e}")
        return False


if __name__ == "__main__":
    health_ok = test_health()
    if health_ok:
        test_tts_generation()
