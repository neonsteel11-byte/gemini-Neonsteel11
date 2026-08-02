"""
Generates a scene image. Priority: Pexels → Replicate → Pollinations (free fallback).
Every image is validated with Pillow to ensure it's real and not corrupted.
"""
import sys
import time
import os
import requests
from io import BytesIO
from PIL import Image
from urllib.parse import quote
from config import GEMINI_IMAGE_MODE, GEMINI_API_KEY

# API Keys from GitHub Secrets
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY', '')
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN', '')

# Configuration flags
USE_PEXELS = os.getenv('USE_PEXELS', 'true').lower() == 'true'
USE_REPLICATE = os.getenv('USE_REPLICATE', 'true').lower() == 'true'

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}?width={w}&height={h}&nologo=true&model=flux&enhance=true&seed={seed}"

def _validate_and_save(img_bytes: bytes, output_path: str, size: tuple):
    """Validates and saves image, exits on failure."""
    try:
        img = Image.open(BytesIO(img_bytes))
        img.verify()
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
    except Exception as e:
        print(f"FATAL: downloaded image for {output_path} is corrupt/invalid: {e}", file=sys.stderr)
        sys.exit(1)
    
    if img.size[0] < 50 or img.size[1] < 50:
        print(f"FATAL: image for {output_path} is suspiciously tiny: {img.size}", file=sys.stderr)
        sys.exit(1)
    
    img = img.resize(size, Image.LANCZOS)
    img.save(output_path, "PNG")

def _search_pexels(prompt: str, output_path: str, size: tuple) -> bool:
    """Searches Pexels for stock photos. Returns True on success."""
    if not PEXELS_API_KEY or not USE_PEXELS:
        return False
    
    search_terms = prompt.lower()
    for term in ['cartoon', 'illustration', 'stick figure', 'drawing', 'animated']:
        search_terms = search_terms.replace(term, '')
    search_terms = search_terms.strip()[:100]
    
    headers = {'Authorization': PEXELS_API_KEY}
    url = f'https://api.pexels.com/v1/search?query={quote(search_terms)}&per_page=3'
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code != 200:
            return False
        
        data = resp.json()
        if not data.get('photos'):
            return False
        
        photo_url = data['photos'][0]['src']['large']
        img_resp = requests.get(photo_url, timeout=30)
        if img_resp.status_code == 200 and img_resp.content:
            _validate_and_save(img_resp.content, output_path, size)
            print(f"      [Pexels] Found stock photo for: {search_terms[:40]}")
            return True
        return False
    except Exception as e:
        print(f"      [WARNING] Pexels search failed: {e}")
        return False

def _generate_replicate(prompt: str, output_path: str, size: tuple) -> bool:
    """Generates image using Replicate API. Returns True on success."""
    if not REPLICATE_API_TOKEN or not USE_REPLICATE:
        return False
    
    w, h = size
    
    try:
        import replicate
        
        output = replicate.run(
            "black-forest-labs/flux-schnell",
            input={
                "prompt": prompt,
                "width": w,
                "height": h,
                "num_outputs": 1,
                "num_inference_steps": 4
            }
        )
        
        if output and len(output) > 0:
            img_url = output[0]
            img_resp = requests.get(img_url, timeout=90)
            if img_resp.status_code == 200 and img_resp.content:
                _validate_and_save(img_resp.content, output_path, size)
                print(f"      [Replicate] Generated AI image via Flux")
                return True
        
        return False
    except Exception as e:
        print(f"      [WARNING] Replicate generation failed: {e}")
        return False

def _generate_pollinations(prompt: str, output_path: str, size: tuple, retries: int = 5, seed: int = 42):
    """Fallback: Free Pollinations.ai generation."""
    w, h = size
    url = POLLINATIONS_URL.format(prompt=quote(prompt), w=w, h=h, seed=seed)
    
    last_error = None
    delay = 3
    
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=90)
            if resp.status_code == 200 and resp.content:
                _validate_and_save(resp.content, output_path, size)
                print(f"      [Pollinations] Generated free AI image")
                return
            last_error = f"HTTP {resp.status_code}"
        except Exception as e:
            last_error = str(e)
            print(f"  retry {attempt}/{retries} for image ({last_error}), waiting {delay}s...", file=sys.stderr)
            time.sleep(delay)
            delay = min(delay * 2, 30)
    
    print(f"FATAL: Pollinations failed after {retries} retries for "
          f"'{prompt[:60]}...': {last_error}", file=sys.stderr)
    sys.exit(1)

def _generate_gemini_image(prompt: str, output_path: str, size: tuple):
    """Last resort: Gemini Image Model (requires billing)."""
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash-image")
        response = model.generate_content(prompt)
        
        image_parts = [p for p in response.candidates[0].content.parts
                      if hasattr(p, "inline_data") and p.inline_data]
        
        if not image_parts:
            print(f"FATAL: Gemini returned no image for prompt '{prompt[:60]}...'", file=sys.stderr)
            sys.exit(1)
        
        _validate_and_save(image_parts[0].inline_data.data, output_path, size)
        print(f"      [Gemini] Generated image via paid API")
    except Exception as e:
        print(f"FATAL: Gemini image generation failed: {e}", file=sys.stderr)
        sys.exit(1)

CARTOON_STYLE_SUFFIX = (
    ", simple minimalist stick-figure illustration style, clean thin black outlines, "
    "basic geometric shapes, whiteboard-explainer-video aesthetic, expressive simple "
    "stick figure poses and gestures, minimal but clear detail on props/objects. "
    "'Luminous Blueprint' brand accents: occasional deep navy blue and warm amber/gold "
    "highlight colors used sparingly against a clean white or light background. "
    "Bright, clean, professional -- no grain, no gritty texture, no photorealistic "
    "faces, no logos, no clutter, no amateur or sloppy rendering."
)

SAFETY_SUFFIX = (
    ", absolutely no readable text or signage of any kind, no logos, no brand "
    "names, generic fictional unnamed characters only, do NOT depict any real "
    "person's face or likeness including CEOs or executives. Faces must be simple, "
    "symmetrical, clean cartoon style with normal proportions -- both eyes the same "
    "size and shape, no distorted or asymmetric features, no extra or malformed "
    "facial details, no uncanny or unsettling expressions."
)

def generate_image(prompt: str, output_path: str, size: tuple = (1920, 1080), seed: int = 42):
    """Generates one scene image with smart fallback chain: Pexels → Replicate → Pollinations → Gemini"""
    if not prompt or not prompt.strip():
        print(f"FATAL: empty image prompt for {output_path}.", file=sys.stderr)
        sys.exit(1)
    
    if "cartoon" not in prompt.lower():
        prompt = prompt.strip() + CARTOON_STYLE_SUFFIX
    prompt = prompt.strip() + SAFETY_SUFFIX
    
    print(f"      Generating image: {prompt[:80]}...")
    
    if USE_PEXELS and _search_pexels(prompt, output_path, size):
        return
    
    if USE_REPLICATE and _generate_replicate(prompt, output_path, size):
        return
    
    _generate_pollinations(prompt, output_path, size, seed=seed)
    
    if GEMINI_IMAGE_MODE:
        _generate_gemini_image(prompt, output_path, size)

def generate_narrator(output_path: str, size: tuple = (500, 800)):
    """Generates mascot character on green background."""
    prompt = (
        "a cute friendly cartoon finance narrator mascot character, full body, "
        "standing pose, mid-explanation hand gesture, big expressive eyes, "
        "flat vector cartoon illustration, bold black outlines, bright colors, "
        "SOLID PURE GREEN BACKGROUND color hex 00FF00, no shadows, no gradients, "
        "no text, no logos, centered in frame"
    )
    generate_image(prompt, output_path, size)

def generate_thumbnail(company: str, hook_text: str, output_path: str, size: tuple = (1280, 720)):
    """Generates YouTube thumbnail with text overlay."""
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
    
    text = hook_text.upper()[:24]
    x, y = int(width * 0.05), int(height * 0.08)
    stroke_width = max(3, font_size // 12)
    draw.text((x, y), text, font=font, fill="white",
              stroke_width=stroke_width, stroke_fill="black")
    img.save(output_path, "JPEG", quality=95)

def download_real_image(image_url: str, output_path: str, size: tuple) -> bool:
    """Downloads real image from URL."""
    if not image_url:
        return False
    
    try:
        resp = requests.get(image_url, timeout=30, headers={"User-Agent": "AccidentalGeniusBot/1.0"})
        if resp.status_code != 200 or not resp.content:
            return False
        _validate_and_save(resp.content, output_path, size)
        return True
    except Exception as e:
        print(f"      [WARNING] Real image download failed ({e}), using AI fallback.", file=sys.stderr)
        return False

if __name__ == "__main__":
    generate_image(
        "a cartoon bull and bear arm wrestling on a trading floor, comic style",
        "output/test_image.png",
        (1920, 1080)
    )
    print("Saved output/test_image.png")
