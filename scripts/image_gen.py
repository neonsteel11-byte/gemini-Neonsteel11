"""
Generates cartoon/animated scene images. Priority: Pexels → Replicate → Pollinations.
"""
import sys, time, os, requests
from io import BytesIO
from PIL import Image
from urllib.parse import quote

PEXELS_API_KEY = os.getenv('PEXELS_API_KEY', '')
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN', '')
USE_PEXELS = os.getenv('USE_PEXELS', 'true').lower() == 'true'
USE_REPLICATE = os.getenv('USE_REPLICATE', 'true').lower() == 'true'

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}?width={w}&height={h}&nologo=true&model=flux&enhance=true&seed={seed}"

def _validate_and_save(img_bytes: bytes, output_path: str, size: tuple):
    try:
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        img.save(output_path, "PNG")
        print(f"      [✓] Saved image to {output_path}")
    except Exception as e:
        print(f"      [!] Image validation failed: {e}", file=sys.stderr)

def _search_pexels(prompt: str, output_path: str, size: tuple) -> bool:
    if not PEXELS_API_KEY or not USE_PEXELS: return False
    search_terms = prompt.lower().replace('cartoon', '').replace('illustration', '').strip()[:100]
    try:
        resp = requests.get(f'https://api.pexels.com/v1/search?query={quote(search_terms)}&per_page=1', headers={'Authorization': PEXELS_API_KEY}, timeout=15)
        if resp.status_code == 200 and resp.json().get('photos'):
            img_resp = requests.get(resp.json()['photos'][0]['src']['large'], timeout=15)
            if img_resp.status_code == 200:
                _validate_and_save(img_resp.content, output_path, size)
                return True
    except: pass
    return False

def _generate_replicate(prompt: str, output_path: str, size: tuple) -> bool:
    if not REPLICATE_API_TOKEN or not USE_REPLICATE: return False
    try:
        import replicate
        output = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt, "width": size[0], "height": size[1], "num_outputs": 1})
        if output:
            img_resp = requests.get(output[0], timeout=90)
            if img_resp.status_code == 200:
                _validate_and_save(img_resp.content, output_path, size)
                return True
    except: pass
    return False

def _generate_pollinations(prompt: str, output_path: str, size: tuple, seed: int = 42):
    url = POLLINATIONS_URL.format(prompt=quote(prompt), w=size[0], h=size[1], seed=seed)
    for attempt in range(3):
        try:
            print(f"      [→] Pollinations attempt {attempt+1}/3...")
            resp = requests.get(url, timeout=120)
            if resp.status_code == 200 and len(resp.content) > 1000:
                _validate_and_save(resp.content, output_path, size)
                return
        except Exception as e:
            print(f"      [!] Pollinations error: {e}")
            time.sleep(2)
    print(f"      [FATAL] Pollinations failed after 3 attempts for {output_path}", file=sys.stderr)

def generate_image(prompt: str, output_path: str, size: tuple = (1920, 1080), seed: int = 42):
    if not prompt: sys.exit(1)
    prompt = prompt + ", simple flat vector cartoon, bold outlines, bright colors, no text"
    print(f"      Generating image: {prompt[:50]}...")
    
    if USE_PEXELS and _search_pexels(prompt, output_path, size): return
    if USE_REPLICATE and _generate_replicate(prompt, output_path, size): return
    
    _generate_pollinations(prompt, output_path, size, seed)
    if not os.path.exists(output_path):
        print(f"      [FATAL] Image generation completely failed for {output_path}", file=sys.stderr)
        sys.exit(1)

def generate_narrator(output_path: str, size: tuple = (500, 800)):
    generate_image("cute friendly cartoon narrator mascot, solid green background hex 00FF00", output_path, size)

def generate_thumbnail(title: str, output_path: str, size: tuple = (1280, 720)):
    generate_image("extreme close-up cartoon face reacting with shock, wide eyes, flat vector illustration, bold black outlines, deep navy blue background", output_path, size)
    img = Image.open(output_path).convert("RGB")
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(size[1] * 0.16))
    except: font = ImageFont.load_default()
    draw.text((int(size[0]*0.05), int(size[1]*0.08)), title.upper()[:24], font=font, fill="white", stroke_width=4, stroke_fill="black")
    img.save(output_path, "JPEG", quality=95)

def download_real_image(image_url: str, output_path: str, size: tuple) -> bool:
    try:
        resp = requests.get(image_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200 and len(resp.content) > 1000:
            _validate_and_save(resp.content, output_path, size)
            return True
    except: pass
    return False
