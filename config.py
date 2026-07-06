"""
Central config. Loads .env and validates required keys exist.
Fails LOUDLY at startup instead of letting a missing key cause
a silent downstream failure (like the black-screen bug).
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv(override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "").strip()
GEMINI_IMAGE_MODE = os.getenv("GEMINI_IMAGE_MODE", "false").lower() == "true"

# YouTube OAuth via refresh token (works in CI with no browser/local files needed)
YT_CLIENT_ID = os.getenv("YT_CLIENT_ID", "").strip()
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET", "").strip()
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN", "").strip()

# Video dimensions
LONGFORM_SIZE = (1920, 1080)
SHORTS_SIZE = (1080, 1920)

OUTPUT_DIR = "output"
ASSETS_DIR = "assets"


def require_gemini_key():
    if not GEMINI_API_KEY:
        print("FATAL: GEMINI_API_KEY is missing. Set it in your .env file "
              "or as a GitHub Actions secret. Get a free key at "
              "https://aistudio.google.com/app/apikey", file=sys.stderr)
        sys.exit(1)
