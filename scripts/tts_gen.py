import os
import sys
import subprocess
from gtts import gTTS
from config import ELEVENLABS_API_KEY
import requests

def _get_duration(filepath):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", filepath],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return float(result.stdout.strip())
    except FileNotFoundError:
        pass
    
    if os.path.exists(filepath):
        size_bytes = os.path.getsize(filepath)
        return max(round(size_bytes / 16000.0, 2), 2.5)
    return 5.0

def generate_voiceover(text: str, output_path: str) -> float:
    print(f"      Processing audio file generation layer...")
    if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 10:
        try:
            url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
            headers = {"Accept": "audio/mpeg", "Content-Type": "application/json", "xi-api-key": ELEVENLABS_API_KEY}
            data = {"text": text, "model_id": "eleven_monolingual_v1", "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}}
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return _get_duration(output_path)
        except Exception as e:
            print(f"      [Warning] ElevenLabs failed ({e}). Using gTTS...")

    tts = gTTS(text=text, lang='en', tld='com')
    tts.save(output_path)
    return _get_duration(output_path)
