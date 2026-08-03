"""
Generates cartoon/animated scene images.
Priority: Replicate (best quality) → Pollinations (free fallback).
NEVER uses real photos - ALWAYS cartoon illustrations.
"""
import sys, time, os, requests
from io import BytesIO
from PIL import Image
from urllib.parse import quote
from config import GEMINI_IMAGE_MODE, GEMINI_API_KEY

PEXELS_API_KEY = os.getenv('PEXELS_API_KEY', '')
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN', '')
USE_PEXELS = os.getenv('USE_PEXELS', 'false').lower() == 'true'  # Disabled
USE_REPLICATE = os.getenv('USE_REPLICATE', 'true').lower() == 'true'

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}?width={w}&height={h}&nologo=true&model=flux&enhance=true&seed={seed}"

# CONSISTENT CARTOON STYLE - Applied to EVERY image
CONSISTENT_STYLE = (
    "simple flat vector cartoon illustration, bold black outlines, "
    "bright saturated colors, clean minimalist whiteboard animation style, "
    "expressive character poses and gestures, no photorealism, no grain, "
    "no shadows, no gradients, no complex details, no text, no logos"
)

def _validate_and_save(img_bytes: bytes, output_path: str, size: tuple):
    try:
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        img.save(output_path, "PNG")
    except Exception as e:
        print(f"FATAL: Image corrupt: {e}", file=sys.stderr)
        sys.exit(1)

def _generate_replicate(prompt: str, output_path: str, size: tuple) -> bool:
    """Generate high-quality cartoon via Replicate (Flux model)."""
    if not REPLICATE_API_TOKEN or not USE_REPLICATE:
        return False
    
    try:
        import replicate
        print("      [→] Generating cartoon via Replicate AI...")
        output = replicate.run(
            "black-forest-labs/flux-schnell",
            input={
                "prompt": prompt + ", " + CONSISTENT_STYLE,
                "width": size[0],
                "height": size[1],
                "num_outputs": 1,
                "num_inference_steps": 4
            }
        )
        if output and len(output) > 0:
            img_resp = requests.get(output[0], timeout=90)
            if img_resp.status_code == 200:
                _validate_and_save(img_resp.content, output_path, size)
                print("      [✓ Replicate] Generated cartoon image")
                return True
    except Exception as e:
        print(f"      [!] Replicate error: {e}")
    return False

def _generate_pollinations(prompt: str, output_path: str, size: tuple, seed: int = 42):
    """Fallback: Free Pollinations.ai for cartoon generation."""
    full_prompt = prompt + ", " + CONSISTENT_STYLE
    url = POLLINATIONS_URL.format(prompt=quote(full_prompt), w=size[0], h=size[1], seed=seed)
    try:
        print("      [→] Generating cartoon via Pollinations (free)...")
        resp = requests.get(url, timeout=90)
        if resp.status_code == 200:
            _validate_and_save(resp.content, output_path, size)
            print("      [✓ Pollinations] Generated cartoon image")
        else:
            print(f"FATAL: Pollinations failed (HTTP {resp.status_code})", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"FATAL: Pollinations error: {e}", file=sys.stderr)
        sys.exit(1)

def generate_image(prompt: str, output_path: str, size: tuple = (1920, 1080), seed: int = 42):
    """Generate cartoon image - ALWAYS, never real photos."""
    if not prompt:
        sys.exit(1)
    
    print(f"      Generating cartoon: {prompt[:60]}...")
    
    # Try Replicate first (better quality)
    if USE_REPLICATE and _generate_replicate(prompt, output_path, size):
        return
    
    # Fallback to Pollinations (free)
    _generate_pollinations(prompt, output_path, size, seed)

def generate_narrator(output_path: str, size: tuple = (500, 800)):
    """Generate consistent mascot character."""
    prompt = (
        "a cute friendly cartoon narrator mascot character, full body, "
        "standing pose, big expressive eyes, wearing simple clothes, "
        "solid pure green background hex 00FF00, no text"
    )
    generate_image(prompt, output_path, size)

def generate_thumbnail(title: str, output_path: str, size: tuple = (1280, 720)):
    """Generate cartoon thumbnail with shocked expression."""
    prompt = (
        "extreme close-up cartoon face reacting with shock and amazement, "
        "wide eyes, mouth open, exaggerated surprised expression, "
        "flat vector illustration, bold black outlines, bright colors"
    )
    generate_image(prompt, output_path, size)
    
    # Add text overlay
    img = Image.open(output_path).convert("RGB")
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(size[1] * 0.16))
    except:
        font = ImageFont.load_default()
    draw.text((int(size[0]*0.05), int(size[1]*0.08)), title.upper()[:24], font=font, fill="white", stroke_width=4, stroke_fill="black")
    img.save(output_path, "JPEG", quality=95)

def download_real_image(image_url: str, output_path: str, size: tuple) -> bool:
    """
    DISABLED: We don't use real photos anymore.
    All scenes use cartoon illustrations for consistency.
    """
    print("      [!] Real photo download disabled - using cartoon generation instead")
    return False
