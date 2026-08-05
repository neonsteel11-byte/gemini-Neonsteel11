import sys, time, os, requests
from io import BytesIO
from PIL import Image
from urllib.parse import quote

PEXELS_API_KEY = os.getenv('PEXELS_API_KEY', '')
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN', '')

def _validate_and_save(img_bytes: bytes, output_path: str, size: tuple):
    try:
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        img = img.resize(size, Image.Resampling.LANCZOS)
        img.save(output_path, "PNG")
        return True
    except Exception as e:
        print(f"      [!] Image save failed: {e}")
        return False

def generate_image(prompt: str, output_path: str, size: tuple = (1920, 1080), seed: int = 42):
    if not prompt:
        sys.exit(1)
    
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
    
    # LAST RESORT FALLBACK: Use Picsum to prevent crash
    print("      [WARNING] Pollinations failed. Using fallback placeholder image.")
    try:
        fallback_url = f"https://picsum.photos/seed/{seed}/{size[0]}/{size[1]}"
        resp = requests.get(fallback_url, timeout=30)
        if resp.status_code == 200:
            _validate_and_save(resp.content, output_path, size)
            print(f"      [✓] Fallback image saved: {output_path}")
            return
    except Exception as e:
        print(f"      [!] Fallback failed: {e}")
        
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
