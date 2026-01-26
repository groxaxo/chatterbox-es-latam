import wave
import math
import struct

sample_rate = 44100
duration = 1.0  # seconds
frequency = 440.0  # Hz

num_samples = int(sample_rate * duration)
audio_data = []

for i in range(num_samples):
    sample = 32767 * math.sin(2 * math.pi * frequency * i / sample_rate)
    audio_data.append(int(sample))

with wave.open("voices/default.wav", "w") as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    for sample in audio_data:
        wav_file.writeframes(struct.pack("h", sample))

print("Created voices/default.wav")
