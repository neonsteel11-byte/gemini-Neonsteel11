"""
Generates voiceover with word-level timings for karaoke-style captions.
Priority: ElevenLabs (premium quality) → Edge TTS (unlimited free fallback).
"""
import os
import sys
import subprocess
import asyncio
import requests
import edge_tts

# ElevenLabs Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "").strip()
# Default to "Rachel" (21m00Tcm4TlvDq8ikWAM) or "Adam" (pNInz6obpgDQGcFmaJgB)
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

# Edge TTS Configuration (Fallback)
EDGE_VOICE = os.getenv("EDGE_VOICE", "en-US-AvaMultilingualNeural")
EDGE_RATE = os.getenv("EDGE_RATE", "+4%")
EDGE_PITCH = os.getenv("EDGE_PITCH", "+2Hz")


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


def _parse_elevenlabs_alignment(alignment, text):
    """Parses ElevenLabs character-level alignment into word-level timings."""
    chars = alignment.get('characters', [])
    starts = alignment.get('character_start_times_seconds', [])
    ends = alignment.get('character_end_times_seconds', [])
    
    words = []
    current_word = ""
    word_start = 0.0
    
    for i, char in enumerate(chars):
        if char == " " or char in [".", ",", "!", "?", ":", ";"]:
            if current_word:
                # Find the actual end time of the last character in this word
                word_end = ends[i-1] if i > 0 else starts[i]
                words.append({"text": current_word, "start": word_start, "end": word_end})
                current_word = ""
        else:
            if not current_word:
                word_start = starts[i]
            current_word += char
            
    if current_word:
        words.append({"text": current_word, "start": word_start, "end": ends[-1] if ends else word_start + 0.5})
        
    return words


def _elevenlabs_tts(text: str, output_path: str):
    """Attempts to generate audio via ElevenLabs with word timestamps."""
    if not ELEVENLABS_API_KEY:
        return None
        
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/with-timestamps"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            data = resp.json()
            # Decode base64 audio
            import base64
            audio_bytes = base64.b64decode(data.get("audio_base64", ""))
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            
            # Parse word timings
            alignment = data.get("alignment", {})
            words = _parse_elevenlabs_alignment(alignment, text)
            return words
        else:
            print(f"      [WARNING] ElevenLabs API returned {resp.status_code}: {resp.text[:100]}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"      [WARNING] ElevenLabs request failed: {e}", file=sys.stderr)
        return None


async def _edge_tts_save_with_timing(text: str, output_path: str, voice: str, rate: str):
    """Fallback: Generates audio via Edge TTS with word timings."""
    communicate = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    words = []
    with open(output_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / 10_000_000  # 100-ns units -> seconds
                dur = chunk["duration"] / 10_000_000
                words.append({"text": chunk["text"], "start": start, "end": start + dur})
    return words


def generate_voiceover(text: str, output_path: str):
    """
    Returns (duration, words) where words is a list of
    {"text": str, "start": float, "end": float} for karaoke-style captions.
    Tries ElevenLabs first, falls back to Edge TTS if it fails or lacks credits.
    """
    print(f"      Processing audio file generation...")
    words = []
    used_engine = "Edge TTS"
    
    # 1. Try ElevenLabs (Premium)
    if ELEVENLABS_API_KEY:
        print("      Attempting ElevenLabs (premium voice)...")
        words = _elevenlabs_tts(text, output_path)
        if words:
            used_engine = "ElevenLabs"
            print("      ✓ ElevenLabs generation successful")
        else:
            print("      ElevenLabs failed or out of credits. Falling back to Edge TTS...", file=sys.stderr)
    
    # 2. Fallback to Edge TTS (Unlimited Free)
    if not words:
        try:
            print("      Attempting Edge TTS (free fallback)...")
            words = asyncio.run(_edge_tts_save_with_timing(text, output_path, EDGE_VOICE, EDGE_RATE))
            used_engine = "Edge TTS"
            print("      ✓ Edge TTS generation successful")
        except Exception as e:
            print(f"FATAL: Both ElevenLabs and Edge TTS failed: {e}", file=sys.stderr)
            sys.exit(1)

    # Validate output
    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        print(f"FATAL: {output_path} was not created or is empty.", file=sys.stderr)
        sys.exit(1)

    duration = _get_duration(output_path)
    
    if not words:
        print(f"      [WARNING] 0 word timings captured -- karaoke captions will be MISSING "
              f"for this scene.", file=sys.stderr)
        
    print(f"      Voice: {used_engine}, {len(words)} word timings captured")
    return duration, words
