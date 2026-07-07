import os
import sys
from dotenv import load_dotenv

load_dotenv(override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip().replace("\n", "").replace("\r", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "").strip().replace("\n", "").replace("\r", "")
GEMINI_IMAGE_MODE = os.getenv("GEMINI_IMAGE_MODE", "false").lower() == "true"

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

USE_VERTEX = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() == "true"
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "").strip()
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1").strip()

YT_CLIENT_ID = os.getenv("YT_CLIENT_ID", "").strip()
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET", "").strip()
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN", "").strip()

LONGFORM_SIZE = (1920, 1080)
SHORTS_SIZE = (1080, 1920)
OUTPUT_DIR = "output"

def require_script_provider():
    if not GROQ_API_KEY and not USE_VERTEX and not GEMINI_API_KEY:
        print("FATAL: no script-generation provider configured. Set GROQ_API_KEY "
              "(recommended, free, no billing) or GEMINI_API_KEY or Vertex AI.",
              file=sys.stderr)
        sys.exit(1)
