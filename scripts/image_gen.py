"""
Generates UNIQUE cartoon images for EVERY scene.
Retry logic ensures every image is created.
"""
import sys, time, os, requests
from io import BytesIO
from PIL import Image
from urllib.parse import quote

PEXELS_API_KEY = os.getenv('PEXELS_API_KEY', '')
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN', '')
USE_PEXELS = os.getenv('USE_PEXELS', 'true').lower() == 'true'
USE_REPLICATE = os.getenv('USE_REPLICATE', 'true').lower() == 'true'

def _validate_and_save(img_bytes: bytes, output_path: str, size: tuple):
    try:
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        img = img.resize(size, Image.Resampling.LANCZOS)
        img.save(output_path, "PNG")
        return True
    except Exception as e:
        print(f"      [!] Image save failed: {e}")
        return False

def _generate_pollinations(prompt: str, output_path: str, size: tuple, seed: int):
    """Generate image with 5 retry attempts."""
    full_prompt = prompt + ", simple flat vector cartoon illustration, bold black outlines, bright saturated colors, clean minimalist style, no text, no logos, no photorealism"
    url = f"https://image.pollinations.ai/prompt/{quote(full_prompt)}?width={size[0]}&height={size[1]}&nologo=true&model=flux&enhance=true&seed={seed}"
    
    for attempt in range(5):
        try:
            print(f"      [→] Image attempt {attempt+1}/5...")
            resp = requests.get(url, timeout=120)
            if resp.status_code == 200 and len(resp.content) > 5000:
                if _validate_and_save(resp.content, output_path, size):
                    print(f"      [✓] Image saved: {output_path}")
                    return True
        except Exception as e:
            print(f"      [!] Attempt {attempt+1} failed: {e}")
            time.sleep(3)
    
    print(f"      [FATAL] Image generation failed after 5 attempts", file=sys.stderr)
    return False

def generate_image(prompt: str, output_path: str, size: tuple = (1920, 1080), seed: int = 42):
    if not prompt:
        print("      [FATAL] Empty prompt", file=sys.stderr)
        sys.exit(1)
    
    print(f"      Generating: {prompt[:50]}...")
    
    # Try Pexels
    if USE_PEXELS and PEXELS_API_KEY:
        try:
            search = prompt.lower().replace('cartoon', '').replace('illustration', '')[:100]
            resp = requests.get(f'https://api.pexels.com/v1/search?query={quote(search)}&per_page=1', 
                              headers={'Authorization': PEXELS_API_KEY}, timeout=15)
            if resp.status_code == 200 and resp.json().get('photos'):
                img_url = resp.json()['photos'][0]['src']['large']
                img_resp = requests.get(img_url, timeout=15)
                if img_resp.status_code == 200 and _validate_and_save(img_resp.content, output_path, size):
                    print(f"      [✓] Pexels stock photo")
                    return
        except: pass
    
    # Try Replicate
    if USE_REPLICATE and REPLICATE_API_TOKEN:
        try:
            import replicate
            output = replicate.run("black-forest-labs/flux-schnell", 
                                 input={"prompt": prompt, "width": size[0], "height": size[1], "num_outputs": 1})
            if output:
                img_resp = requests.get(output[0], timeout=90)
                if img_resp.status_code == 200 and _validate_and_save(img_resp.content, output_path, size):
                    print(f"      [✓] Replicate AI")
                    return
        except: pass
    
    # Fallback to Pollinations (with 5 retries)
    if _generate_pollinations(prompt, output_path, size, seed):
        return
    
    print(f"      [FATAL] All image generation methods failed for {output_path}", file=sys.stderr)
    sys.exit(1)

def generate_narrator(output_path: str, size: tuple = (500, 800)):
    generate_image("cute friendly cartoon narrator mascot, solid green background hex 00FF00", output_path, size)

def generate_thumbnail(title: str, output_path: str, size: tuple = (1280, 720)):
    generate_image("extreme close-up cartoon face with shocked expression, wide eyes, mouth open, flat vector illustration, bold outlines, bright red and yellow background", output_path, size)
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
        if resp.status_code == 200 and len(resp.content) > 5000:
            return _validate_and_save(resp.content, output_path, size)
    except: pass
    return False
