import requests
import json

BASE_URL = "http://0.0.0.0:8004"


def test_openai_compat():
    print(
        f"\nTesting OpenAI Compatibility (voice='alloy') at {BASE_URL}/v1/audio/speech..."
    )
    payload = {
        "model": "tts-1",
        "input": "Hola, esto es una prueba de compatibilidad con OpenAI usando la voz alloy.",
        "voice": "alloy",
        "response_format": "mp3",
        "speed": 1.0,
    }

    try:
        response = requests.post(f"{BASE_URL}/v1/audio/speech", json=payload)

        if response.status_code == 200:
            print(f"✅ OpenAI Compat Test passed!")
            print(f"   Audio size: {len(response.content)} bytes")
            return True
        else:
            print(
                f"❌ OpenAI Compat Test failed with status code: {response.status_code}"
            )
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ OpenAI Compat Test failed with error: {e}")
        return False


if __name__ == "__main__":
    test_openai_compat()
