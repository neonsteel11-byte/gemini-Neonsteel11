"""
Generates a scene image. Default: Pollinations.ai (free, no API key).
Upgrade path: set GEMINI_IMAGE_MODE=true in .env to use Gemini's image model instead
(needs billing enabled on your Google AI Studio project).

Every image is opened with Pillow after download to confirm it's a REAL,
valid image and not an error page or truncated file saved with a .png name --
that mismatch is a classic cause of "video" output that's actually broken/blank.
"""
import sys
import time
import requests
from io import BytesIO
from PIL import Image
from urllib.parse import quote
from config import GEMINI_IMAGE_MODE, GEMINI_API_KEY

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}?width={w}&height={h}&nologo=true&model=flux&enhance=true"


def _validate_and_save(img_bytes: bytes, output_path: str, size: tuple):
    try:
        img = Image.open(BytesIO(img_bytes))
        img.verify()  # raises if corrupt
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
    except Exception as e:
        print(f"FATAL: downloaded image for {output_path} is corrupt/invalid: {e}",
              file=sys.stderr)
        sys.exit(1)

    if img.size[0] < 50 or img.size[1] < 50:
        print(f"FATAL: image for {output_path} is suspiciously tiny: {img.size}",
              file=sys.stderr)
        sys.exit(1)

    img = img.resize(size, Image.LANCZOS)
    img.save(output_path, "PNG")


def _generate_pollinations(prompt: str, output_path: str, size: tuple, retries: int = 3):
    w, h = size
    url = POLLINATIONS_URL.format(prompt=quote(prompt), w=w, h=h)

    last_error = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=60)
            if resp.status_code == 200 and resp.content:
                _validate_and_save(resp.content, output_path, size)
                return
            last_error = f"HTTP {resp.status_code}"
        except Exception as e:
            last_error = str(e)
        print(f"  retry {attempt}/{retries} for image ({last_error})...", file=sys.stderr)
        time.sleep(2)

    print(f"FATAL: image generation failed after {retries} retries for "
          f"'{prompt[:60]}...': {last_error}", file=sys.stderr)
    sys.exit(1)


def _generate_gemini_image(prompt: str, output_path: str, size: tuple):
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash-image")
    response = model.generate_content(prompt)

    image_parts = [p for p in response.candidates[0].content.parts
                    if hasattr(p, "inline_data") and p.inline_data]
    if not image_parts:
        print(f"FATAL: Gemini image model returned no image for prompt "
              f"'{prompt[:60]}...'", file=sys.stderr)
        sys.exit(1)

    _validate_and_save(image_parts[0].inline_data.data, output_path, size)


def generate_image(prompt: str, output_path: str, size: tuple = (1920, 1080)):
    """
    Generates one scene image at output_path, resized to `size`.
    Exits the whole program on failure -- see module docstring for why.
    """
    if not prompt or not prompt.strip():
        print(f"FATAL: empty image prompt for {output_path}.", file=sys.stderr)
        sys.exit(1)

    if GEMINI_IMAGE_MODE:
        _generate_gemini_image(prompt, output_path, size)
    else:
        _generate_pollinations(prompt, output_path, size)


if __name__ == "__main__":
    generate_image(
        "a cartoon bull and bear arm wrestling on a trading floor, comic style",
        "output/test_image.png",
        (1920, 1080)
    )
    print("Saved output/test_image.png")
