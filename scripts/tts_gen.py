import os
import sys
import subprocess
import asyncio
import edge_tts

EDGE_VOICE = os.getenv("EDGE_VOICE", "en-US-EricNeural")
EDGE_RATE = os.getenv("EDGE_RATE", "+18%")

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

async def _edge_tts_save(text: str, output_path: str, voice: str, rate: str):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)

def generate_voiceover(text: str, output_path: str) -> float:
    print(f"      Processing audio file generation layer...")
    try:
        asyncio.run(_edge_tts_save(text, output_path, EDGE_VOICE, EDGE_RATE))
    except Exception as e:
        print(f"FATAL: edge-tts failed generating {output_path}: {e}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        print(f"FATAL: {output_path} was not created or is empty.", file=sys.stderr)
        sys.exit(1)

    print(f"      Voice: edge-tts ({EDGE_VOICE}, rate {EDGE_RATE})")
    return _get_duration(output_path)
