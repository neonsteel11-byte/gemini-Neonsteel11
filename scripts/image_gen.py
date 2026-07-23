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

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}?width={w}&height={h}&nologo=true&model=flux&enhance=true&seed={seed}"


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


def _generate_pollinations(prompt: str, output_path: str, size: tuple, retries: int = 5, seed: int = 42):
    w, h = size
    url = POLLINATIONS_URL.format(prompt=quote(prompt), w=w, h=h, seed=seed)

    last_error = None
    delay = 3
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=90)
            if resp.status_code == 200 and resp.content:
                _validate_and_save(resp.content, output_path, size)
                return
            last_error = f"HTTP {resp.status_code}"
        except Exception as e:
            last_error = str(e)
        print(f"  retry {attempt}/{retries} for image ({last_error}), waiting {delay}s...", file=sys.stderr)
        time.sleep(delay)
        delay = min(delay * 2, 30)

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


CARTOON_STYLE_SUFFIX = (
    ", clean flat vector illustration in the style of Kurzgesagt -- simple bold "
    "shapes, minimal clean geometry, bold thin outlines, NOT overly detailed or "
    "textured. 'Luminous Blueprint' brand palette: deep navy blue backgrounds, "
    "glowing warm amber/gold accent highlights (lightbulb glow, spark effects), "
    "subtle thin circuit-line decorative accents. Bright, vibrant, clean colors -- "
    "no grain, no gritty texture, no dark muddy tones, no photorealistic human "
    "faces (stylized simple character faces only)."
)
# ALWAYS appended, no matter what the LLM already wrote -- this is a safety
# backstop, not a style choice, so it must never be conditionally skipped.
SAFETY_SUFFIX = (
    ", absolutely no readable text or signage of any kind, no logos, no brand "
    "names, generic fictional unnamed characters only, do NOT depict any real "
    "person's face or likeness including CEOs or executives"
)

def generate_image(prompt: str, output_path: str, size: tuple = (1920, 1080), seed: int = 42):
    """
    Generates one scene image at output_path, resized to `size`.
    Every prompt is hard-locked to a cartoon style and safety constraints
    regardless of what the script-generation model produced.
    Exits the whole program on failure -- see module docstring for why.
    """
    if not prompt or not prompt.strip():
        print(f"FATAL: empty image prompt for {output_path}.", file=sys.stderr)
        sys.exit(1)

    if "cartoon" not in prompt.lower():
        prompt = prompt.strip() + CARTOON_STYLE_SUFFIX
    prompt = prompt.strip() + SAFETY_SUFFIX

    if GEMINI_IMAGE_MODE:
        _generate_gemini_image(prompt, output_path, size)
    else:
        _generate_pollinations(prompt, output_path, size, seed=seed)


def generate_narrator(output_path: str, size: tuple = (500, 800)):
    """
    Generates one consistent cartoon mascot/host character on a solid green
    background, for later chroma-keying into a corner overlay in video_builder.
    Generated ONCE per video (not per scene) so the same character appears
    throughout, like a recurring host.
    """
    prompt = (
        "a cute friendly cartoon finance narrator mascot character, full body, "
        "standing pose, mid-explanation hand gesture, big expressive eyes, "
        "flat vector cartoon illustration, bold black outlines, bright colors, "
        "SOLID PURE GREEN BACKGROUND color hex 00FF00, no shadows, no gradients, "
        "no text, no logos, centered in frame"
    )
    generate_image(prompt, output_path, size)


def generate_thumbnail(company: str, hook_text: str, output_path: str, size: tuple = (1280, 720)):
    """
    Generates a custom YouTube thumbnail: a close-up, exaggerated-expression
    cartoon face (shock/excitement -- proven to lift CTR 20-30%) with bold
    high-contrast text burned on top via Pillow (more reliable than trusting
    an AI image model to render legible text).
    """
    from PIL import ImageDraw, ImageFont

    prompt = (
        f"extreme close-up cartoon face reacting with shock and excitement, "
        f"wide eyes, mouth open, exaggerated expression, flat vector illustration, "
        f"bold black outlines, deep navy blue background with glowing warm amber "
        f"rim lighting on the face, clean flat colors, no grain, no photorealistic "
        f"shading, no text, no logos"
    )
    generate_image(prompt, output_path, size)

    img = Image.open(output_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    width, height = img.size

    font_size = int(height * 0.16)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    text = hook_text.upper()[:24]  # keep it short -- 3-4 words performs best
    # Position in upper-left two-thirds of frame, avoiding bottom-right
    # duration-badge overlap
    x, y = int(width * 0.05), int(height * 0.08)

    stroke_width = max(3, font_size // 12)
    draw.text((x, y), text, font=font, fill="white",
               stroke_width=stroke_width, stroke_fill="black")

    img.save(output_path, "JPEG", quality=95)


def generate_thumbnail(company: str, hook_text: str, output_path: str, size: tuple = (1280, 720)):
    """
    Generates a custom YouTube thumbnail: a close-up, exaggerated-expression
    cartoon face (shock/excitement -- proven to lift CTR 20-30%) with bold
    high-contrast text burned on top via Pillow (more reliable than trusting
    an AI image model to render legible text).
    """
    from PIL import ImageDraw, ImageFont

    prompt = (
        f"extreme close-up cartoon face reacting with shock and excitement, "
        f"wide eyes, mouth open, exaggerated expression, flat vector illustration, "
        f"bold black outlines, deep navy blue background with glowing warm amber "
        f"rim lighting on the face, clean flat colors, no grain, no photorealistic "
        f"shading, no text, no logos"
    )
    generate_image(prompt, output_path, size)

    img = Image.open(output_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    width, height = img.size

    font_size = int(height * 0.16)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    text = hook_text.upper()[:24]  # keep it short -- 3-4 words performs best
    # Position in upper-left two-thirds of frame, avoiding bottom-right
    # duration-badge overlap
    x, y = int(width * 0.05), int(height * 0.08)

    stroke_width = max(3, font_size // 12)
    draw.text((x, y), text, font=font, fill="white",
               stroke_width=stroke_width, stroke_fill="black")

    img.save(output_path, "JPEG", quality=95)


def download_real_image(image_url: str, output_path: str, size: tuple) -> bool:
    """
    Downloads and validates a REAL image (e.g. from Wikipedia) instead of
    generating one. Returns True on success, False on failure (caller should
    fall back to AI generation in that case -- non-fatal here).
    """
    if not image_url:
        return False
    try:
        resp = requests.get(image_url, timeout=30, headers={"User-Agent": "FinanceInventionBot/1.0"})
        if resp.status_code != 200 or not resp.content:
            return False
        _validate_and_save(resp.content, output_path, size)
        return True
    except Exception as e:
        print(f"      [WARNING] Real image download failed ({e}), will use AI fallback.", file=sys.stderr)
        return False


if __name__ == "__main__":
    generate_image(
        "a cartoon bull and bear arm wrestling on a trading floor, comic style",
        "output/test_image.png",
        (1920, 1080)
    )
    print("Saved output/test_image.png")
