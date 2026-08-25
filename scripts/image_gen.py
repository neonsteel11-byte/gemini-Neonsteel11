import sys, time, os, requests
from io import BytesIO
from PIL import Image
from urllib.parse import quote

PEXELS_API_KEY = os.getenv('PEXELS_API_KEY', '')
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN', '')
HF_API_TOKEN = os.getenv('HF_API_TOKEN', '')


def _generate_image_pexels(search_term: str, output_path: str, size: tuple):
    """Try a real photo of the actual object/invention from Pexels. Returns True on success."""
    if not PEXELS_API_KEY or not search_term:
        return False
    try:
        resp = requests.get(
            'https://api.pexels.com/v1/search',
            headers={'Authorization': PEXELS_API_KEY},
            params={'query': search_term, 'per_page': 1, 'orientation': 'portrait' if size[1] > size[0] else 'landscape'},
            timeout=20
        )
        if resp.status_code == 200:
            data = resp.json()
            photos = data.get('photos', [])
            if photos:
                img_url = photos[0]['src']['large2x']
                img_resp = requests.get(img_url, timeout=20)
                if img_resp.status_code == 200:
                    if _validate_and_save(img_resp.content, output_path, size):
                        print(f'      [OK] Real Pexels photo saved: {output_path}')
                        return True
        return False
    except Exception as e:
        print(f'      [!] Pexels lookup failed: {e}')
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


def _generate_image_huggingface(full_prompt: str, output_path: str, size: tuple):
    if not HF_API_TOKEN:
        return False
    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(provider="together", api_key=HF_API_TOKEN)
        img = client.text_to_image(full_prompt, model="black-forest-labs/FLUX.1-schnell")
        img = img.convert("RGB").resize(size, Image.Resampling.LANCZOS)
        img.save(output_path, "PNG")
        print(f"      [OK] Hugging Face image saved: {output_path}")
        return True
    except Exception as e:
        print(f"      [!] Hugging Face image failed: {e}")
        return False


def _generate_image_pollinations(full_prompt: str, output_path: str, size: tuple, seed: int):
    url = f"https://image.pollinations.ai/prompt/{quote(full_prompt)}?width={size[0]}&height={size[1]}&model=flux&seed={seed}&nologo=true"
    for attempt in range(3):
        try:
            print(f"      Pollinations attempt {attempt+1}/3...")
            resp = requests.get(url, timeout=120)
            if resp.status_code == 200 and len(resp.content) > 5000:
                if _validate_and_save(resp.content, output_path, size):
                    print(f"      [OK] Pollinations image saved: {output_path}")
                    return True
        except Exception as e:
            print(f"      [!] Pollinations attempt {attempt+1} failed: {e}")
            time.sleep(2)
    return False


def _generate_title_card(label: str, output_path: str, size: tuple):
    print("      [WARNING] All image generation failed. Generating text title card fallback.")
    try:
        from PIL import ImageDraw, ImageFont
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
        return True
    except Exception as e:
        print(f"      [!] Title card fallback failed: {e}")
        return False


def generate_image(prompt: str, output_path: str, size: tuple = (1920, 1080), seed: int = 42, specific_object: str = None):
    if not prompt:
        sys.exit(1)

    if specific_object:
        full = f"{prompt}, featuring {specific_object}, realistic detailed illustration, natural lighting, high detail, no fantasy or sci-fi elements, no text"
    else:
        full = prompt + ", realistic photography style, natural lighting, high detail, no fantasy or sci-fi elements, no text"

    if specific_object and _generate_image_pexels(specific_object, output_path, size):
        return

    if _generate_image_huggingface(full, output_path, size):
        return

    if _generate_image_pollinations(full, output_path, size, seed):
        return

    label = specific_object or prompt.split(",")[0][:40]
    if _generate_title_card(label, output_path, size):
        return

    print(f"      [FATAL] All image methods failed", file=sys.stderr)
    sys.exit(1)


def generate_narrator(path, size=(500, 800)):
    generate_image("cartoon mascot, green background", path, size)


def generate_thumbnail(title, path, size=(1280, 720), specific_object=None):
    subject = specific_object or title
    prompt = f"YouTube thumbnail style, detailed cartoon illustration of {subject}, expressive shocked or excited face, both the person and the object clearly visible, bold dramatic lighting, high contrast, eye-catching, professional character art"
    generate_image(prompt, path, size, specific_object=subject)


def download_real_image(url, path, size):
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            img = Image.open(BytesIO(resp.content)).convert("RGB")
            img = img.resize(size, Image.Resampling.LANCZOS)
            img.save(path, "PNG")
            return True
    except Exception:
        pass
    return False
