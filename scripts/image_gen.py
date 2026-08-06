import sys, time, os, requests
from io import BytesIO
from PIL import Image
from urllib.parse import quote

PEXELS_API_KEY = os.getenv('PEXELS_API_KEY', '')
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN', '')

HF_API_TOKEN = os.getenv('HF_API_TOKEN', '')

def generate_image_huggingface(prompt: str, output_path: str, size: tuple):
    """Generate an image using Hugging Face's Inference API (Stable Diffusion XL). Returns True on success."""
    if not HF_API_TOKEN:
        return False
    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {"inputs": prompt}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=90)
        if resp.status_code == 200 and len(resp.content) > 5000:
            return _validate_and_save(resp.content, output_path, size)
        else:
            print(f"      [!] HF image failed: HTTP {resp.status_code} - {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"      [!] HF image error: {e}")
        return False

def _validate_and_save(img_bytes: bytes, output_path: str, size: tuple):
    try:
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        img = img.resize(size, Image.Resampling.LANCZOS)
        img.save(output_path, "PNG")
        return True
    except Exception as e:
        print(f"      [!] Image save failed: {e}")
        return False

def generate_image(prompt: str, output_path: str, size: tuple = (1920, 1080), seed: int = 42, specific_object: str = None):
    if not prompt:
        sys.exit(1)
    
    if specific_object:
        full = f"{prompt}, featuring {specific_object}, flat cartoon, bold outlines, bright colors, no text"
    else:
        full = prompt + ", flat cartoon, bold outlines, bright colors, no text"
    url = f"https://image.pollinations.ai/prompt/{quote(full)}?width={size[0]}&height={size[1]}&model=flux&seed={seed}&nologo=true"
    
    for attempt in range(3):
        try:
            print(f"      Image attempt {attempt+1}/3...")
            resp = requests.get(url, timeout=120)
            if resp.status_code == 200 and len(resp.content) > 5000:
                if _validate_and_save(resp.content, output_path, size):
                    print(f"      [✓] Saved: {output_path}")
                    return
        except Exception as e:
            print(f"      [!] Attempt {attempt+1} failed: {e}")
            time.sleep(2)
    
    # LAST RESORT FALLBACK: Generate a clean title card instead of a random photo
    print("      [WARNING] Pollinations failed. Generating text title card fallback.")
    try:
        from PIL import Image, ImageDraw, ImageFont
        label = specific_object or prompt.split(",")[0][:40]
        img = Image.new("RGB", size, color=(30, 30, 60))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("assets/fonts/arialbd.ttf", 90)
        except Exception:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), label, font=font)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((size[0]-text_w)/2, (size[1]-text_h)/2), label, font=font, fill=(255, 255, 255))
        img.save(output_path)
        print(f"      [OK] Title card fallback saved: {output_path}")
        return
    except Exception as e:
        print(f"      [!] Title card fallback failed: {e}")
    print(f"      [FATAL] All image methods failed", file=sys.stderr)
    sys.exit(1)

def generate_narrator(path, size=(500,800)):
    generate_image("cartoon mascot, green background", path, size)

def generate_thumbnail(title, path, size=(1280,720)):
    generate_image("shocked cartoon face, bright colors", path, size)

def download_real_image(url, path, size):
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            img = Image.open(BytesIO(resp.content)).convert("RGB")
            img = img.resize(size, Image.Resampling.LANCZOS)
            img.save(path, "PNG")
            return True
    except: pass
    return False
