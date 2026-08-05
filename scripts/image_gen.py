import sys, time, os, requests
from io import BytesIO
from PIL import Image
from urllib.parse import quote

PEXELS_API_KEY = os.getenv('PEXELS_API_KEY', '')
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN', '')

def generate_image(prompt, output_path, size=(1920,1080), seed=42):
    if not prompt:
        sys.exit(1)
    
    full = prompt + ", flat cartoon, bold outlines, bright colors, no text"
    url = f"https://image.pollinations.ai/prompt/{quote(full)}?width={size[0]}&height={size[1]}&seed={seed}"
    
    for attempt in range(3):
        try:
            print(f"      Image attempt {attempt+1}/3...")
            resp = requests.get(url, timeout=120)
            if resp.status_code == 200 and len(resp.content) > 5000:
                img = Image.open(BytesIO(resp.content)).convert("RGB")
                img = img.resize(size, Image.Resampling.LANCZOS)
                img.save(output_path, "PNG")
                print(f"      [✓] Saved: {output_path}")
                return
        except Exception as e:
            print(f"      [!] Attempt {attempt+1} failed: {e}")
            time.sleep(2)
    
    print(f"      [FATAL] Image failed", file=sys.stderr)
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
