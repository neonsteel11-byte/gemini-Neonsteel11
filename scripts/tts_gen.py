import os
import sys
import subprocess
from gtts import gTTS
from config import ELEVENLABS_API_KEY
import requests

ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

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
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
        headers = {"Accept": "audio/mpeg", "Content-Type": "application/json", "xi-api-key": ELEVENLABS_API_KEY}
        data = {"text": text, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
        except Exception as e:
            print(f"      [WARNING] ElevenLabs request failed ({e}). Falling back to gTTS.", file=sys.stderr)
            response = None

        if response is not None:
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print("      Voice: ElevenLabs (premium)")
                return _get_duration(output_path)
            else:
                print(f"      [WARNING] ElevenLabs returned {response.status_code}: "
                      f"{response.text[:200]} -- falling back to gTTS. Check your key/quota "
                      f"at elevenlabs.io if you want premium voice.", file=sys.stderr)

    tts = gTTS(text=text, lang='en', tld='com')
    tts.save(output_path)
    print("      Voice: gTTS (free fallback)")
    return _get_duration(output_path)
