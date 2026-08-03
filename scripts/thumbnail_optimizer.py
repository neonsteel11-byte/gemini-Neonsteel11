"""
Generates HIGH-CTR thumbnails optimized for educational content.
Professional design that balances curiosity + credibility.
"""
from PIL import Image, ImageDraw, ImageFont
import os

def generate_professional_thumbnail(invention: str, inventor: str, output_path: str, size: tuple = (1280, 720)):
    """
    Professional thumbnail formula for educational channels:
    1. Shocked/curious cartoon face (emotional hook)
    2. The invention visible (curiosity)
    3. Bold contrasting colors (red/yellow/blue)
    4. 3-4 words MAX of punchy text
    5. Clean, readable font
    """
    from scripts.image_gen import _generate_pollinations, CONSISTENT_CARTOON_STYLE
    
    # Generate base image with shocked face + invention
    prompt = (
        f"extreme close-up cartoon face with MOUTH WIDE OPEN in shock and amazement, "
        f"eyes popping out, exaggerated surprised expression, "
        f"holding or looking at {invention}, "
        f"flat vector cartoon illustration, bold black outlines, "
        f"bright RED and YELLOW background for maximum contrast and CTR, "
        f"professional YouTube thumbnail style, no text, no logos"
    )
    
    _generate_pollinations(prompt, output_path, size, seed=999)
    
    # Add professional text overlay
    img = Image.open(output_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    
    # HIGH-CTR text formulas:
    text_options = [
        f"ACCIDENT!\n{invention.upper()[:20]}",
        f"BY MISTAKE\n{invention.upper()[:20]}",
        f"$0 IDEA\n{invention.upper()[:20]}",
        f"WRONG TURN\n{invention.upper()[:20]}",
    ]
    
    import random
    text = random.choice(text_options)
    
    # Font size proportional to thumbnail
    font_size = int(size[1] * 0.18)
    
    # Try to load a bold professional font
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
    ]
    
    font = None
    for path in font_paths:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, font_size)
                break
            except:
                pass
    
    if not font:
        font = ImageFont.load_default()
    
    # Position: Upper left (proven best for CTR on mobile)
    x, y = int(size[0] * 0.03), int(size[1] * 0.05)
    
    # White text with THICK BLACK outline (maximum contrast, readable on all backgrounds)
    stroke_width = max(5, font_size // 10)
    draw.text((x, y), text, font=font, fill="white", 
              stroke_width=stroke_width, stroke_fill="black")
    
    # Add subtle drop shadow for depth
    draw.text((x+3, y+3), text, font=font, fill="black", alpha=128)
    
    # Save as high-quality JPEG
    img.save(output_path, "JPEG", quality=95, optimize=True)
    print(f"      [✓] Generated HIGH-CTR thumbnail: '{text.split()[0]} {invention[:15]}'")

if __name__ == "__main__":
    generate_professional_thumbnail("Potato Chips", "George Crum", "test_thumbnail.jpg")
