import os
import sys
from dotenv import load_dotenv

load_dotenv(override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip().replace("\n", "").replace("\r", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "").strip().replace("\n", "").replace("\r", "")
GEMINI_IMAGE_MODE = os.getenv("GEMINI_IMAGE_MODE", "false").lower() == "true"

USE_VERTEX = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() == "true"
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "").strip()
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1").strip()

YT_CLIENT_ID = os.getenv("YT_CLIENT_ID", "").strip()
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET", "").strip()
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN", "").strip()

LONGFORM_SIZE = (1920, 1080)
SHORTS_SIZE = (1080, 1920)
OUTPUT_DIR = "output"

def require_gemini_key():
    # Vertex AI mode authenticates via service account, not an API key --
    # only enforce the key requirement in standard AI Studio mode.
    if USE_VERTEX:
        if not GOOGLE_CLOUD_PROJECT:
            print("FATAL: GOOGLE_GENAI_USE_VERTEXAI is true but GOOGLE_CLOUD_PROJECT is missing.",
                  file=sys.stderr)
            sys.exit(1)
        return
    if not GEMINI_API_KEY:
        print("FATAL: GEMINI_API_KEY is missing.", file=sys.stderr)
        sys.exit(1)
