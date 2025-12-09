import requests
import sys
import os

def test_enrollment(audio_path):
    url = "http://localhost:8000/api/v1/enroll"
    
    if not os.path.exists(audio_path):
        print(f"Error: File {audio_path} not found.")
        return

    print(f"Sending {audio_path} to {url}...")
    
    with open(audio_path, "rb") as f:
        files = {"file": ("test_audio.wav", f, "audio/wav")}
        try:
            response = requests.post(url, files=files)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Enrollment Successful!")
                print(f"Voice ID Length: {len(data['voice_id'])}")
                print(f"Duration: {data['duration']:.2f}s")
                print(f"Status: {data['status']}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Is the server running? (uvicorn server.main:app --reload)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_server.py <path_to_audio.wav>")
    else:
        test_enrollment(sys.argv[1])
