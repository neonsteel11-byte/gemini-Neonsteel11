"""
High-CTR cartoon image generation with optimized thumbnails.
"""
import sys, time, os, requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from urllib.parse import quote

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}?width={w}&height={h}&nologo=true&model=flux&enhance=true&seed={seed}"

def _validate_and_save(img_bytes: bytes, output_path: str, size: tuple):
    try:
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        img.save(output_path, "PNG")
    except Exception as e:
        print(f"FATAL: Image corrupt: {e}", file=sys.stderr)
        sys.exit(1)

def _generate_pollinations(prompt: str, output_path: str, size: tuple, seed: int = 42):
    url = POLLINATIONS_URL.format(prompt=quote(prompt), w=size[0], h=size[1], seed=seed)
    resp = requests.get(url, timeout=90)
    if resp.status_code == 200:
        _validate_and_save(resp.content, output_path, size)

def generate_image(prompt: str, output_path: str, size: tuple = (1920, 1080), seed: int = 42):
    if not prompt:
        sys.exit(1)
    prompt = prompt + ", simple flat vector cartoon, bold outlines, bright colors, no text"
    _generate_pollinations(prompt, output_path, size, seed)

def generate_narrator(output_path: str, size: tuple = (500, 800)):
    prompt = "cute friendly cartoon narrator mascot, solid green background hex 00FF00"
    generate_image(prompt, output_path, size)

def generate_thumbnail(invention: str, inventor: str, output_path: str, size: tuple = (1280, 720)):
    """
    HIGH-CTR THUMBNAIL FORMULA:
    - Shocked/exaggerated cartoon face (emotional hook)
    - The invention visible (curiosity)
    - Bold contrasting colors
    - 3-4 words MAX of punchy text
    """
    # Generate shocked face + invention
    prompt = (
        f"extreme close-up cartoon face with MOUTH WIDE OPEN in shock, "
        f"eyes popping out, exaggerated surprised expression, "
        f"holding {invention} in hand, "
        f"flat vector cartoon illustration, bold black outlines, "
        f"bright RED and YELLOW background for maximum contrast, "
        f"no text, no logos"
    )
    _generate_pollinations(prompt, output_path, size, seed=999)
    
    # Add HIGH-CTR text overlay
    img = Image.open(output_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    
    # BIG BOLD TEXT - Top third of frame
    text = f"ACCIDENT!\n{invention.upper()[:15]}"
    font_size = int(size[1] * 0.18)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Position: Upper left (proven best for CTR)
    x, y = int(size[0] * 0.03), int(size[1] * 0.05)
    
    # White text with BLACK outline (maximum contrast)
    draw.text((x, y), text, font=font, fill="white", stroke_width=6, stroke_fill="black")
    
    img.save(output_path, "JPEG", quality=95)
    print("      [✓] Generated HIGH-CTR thumbnail with shocked face + bold text")

def download_real_image(image_url: str, output_path: str, size: tuple) -> bool:
    try:
        resp = requests.get(image_url, timeout=15)
        if resp.status_code == 200:
            _validate_and_save(resp.content, output_path, size)
            return True
    except:
        pass
    return False
