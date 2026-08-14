"""
Builds a branded static infographic image from listicle script data --
one row per entry (portrait + name + fact), suitable for a YouTube
Community post. Reuses generate_image() so entries share the channel's
established cartoon art style.
"""
import os
from PIL import Image, ImageDraw, ImageFont
from scripts.image_gen import generate_image

CANVAS_WIDTH = 1080
ROW_HEIGHT = 220
HEADER_HEIGHT = 200
PORTRAIT_SIZE = 160
BG_COLORS = [(20, 20, 35), (28, 28, 45)]
ACCENT_COLORS = [(255, 140, 0), (0, 200, 140), (60, 140, 255), (200, 80, 220)]


def _load_font(size, bold=False):
    path = "assets/fonts/arialbd.ttf" if bold else "assets/fonts/arial.ttf"
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), trial, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def build_infographic(title, entries, output_path, tmp_dir):
    """
    entries: list of dicts with "entry_name" and "narration" (from a listicle script's scenes).
    Generates a portrait for each entry, then composes a single tall image.
    """
    num_entries = len(entries)
    total_height = HEADER_HEIGHT + (ROW_HEIGHT * num_entries) + 60

    canvas = Image.new("RGB", (CANVAS_WIDTH, total_height), color=(15, 15, 25))
    draw = ImageDraw.Draw(canvas)

    title_font = _load_font(56, bold=True)
    name_font = _load_font(34, bold=True)
    fact_font = _load_font(26)
    number_font = _load_font(48, bold=True)

    title_lines = _wrap_text(draw, title, title_font, CANVAS_WIDTH - 80)
    y = 40
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        w = bbox[2] - bbox[0]
        draw.text(((CANVAS_WIDTH - w) / 2, y), line, font=title_font, fill=(255, 255, 255))
        y += bbox[3] - bbox[1] + 10

    row_y = HEADER_HEIGHT
    for idx, entry in enumerate(entries):
        name = entry.get("entry_name", f"Entry {idx+1}")
        fact = entry.get("narration", "")
        accent = ACCENT_COLORS[idx % len(ACCENT_COLORS)]
        bg = BG_COLORS[idx % 2]

        draw.rectangle([0, row_y, CANVAS_WIDTH, row_y + ROW_HEIGHT], fill=bg)
        draw.rectangle([0, row_y, 8, row_y + ROW_HEIGHT], fill=accent)

        num_x, num_y = 30, row_y + ROW_HEIGHT // 2 - 24
        draw.ellipse([num_x, num_y, num_x + 50, num_y + 50], fill=accent)
        num_text = str(idx + 1)
        bbox = draw.textbbox((0, 0), num_text, font=number_font)
        draw.text((num_x + 25 - (bbox[2]-bbox[0])/2, num_y + 25 - (bbox[3]-bbox[1])/2 - bbox[1]),
                   num_text, font=number_font, fill=(15, 15, 25))

        portrait_path = os.path.join(tmp_dir, f"infographic_portrait_{idx}.png")
        try:
            generate_image(
                f"cartoon portrait of {name}, related to {title}, flat illustration style",
                portrait_path, (PORTRAIT_SIZE, PORTRAIT_SIZE), specific_object=name
            )
            portrait = Image.open(portrait_path).convert("RGB").resize((PORTRAIT_SIZE, PORTRAIT_SIZE))
            px = 100
            py = row_y + (ROW_HEIGHT - PORTRAIT_SIZE) // 2
            canvas.paste(portrait, (px, py))
        except Exception as e:
            print(f"      [!] Infographic portrait failed for {name}: {e}")

        text_x = 100 + PORTRAIT_SIZE + 30
        text_y = row_y + 25
        draw.text((text_x, text_y), name, font=name_font, fill=accent)

        fact_lines = _wrap_text(draw, fact, fact_font, CANVAS_WIDTH - text_x - 30)
        fy = text_y + 50
        for line in fact_lines[:3]:
            draw.text((text_x, fy), line, font=fact_font, fill=(230, 230, 230))
            fy += 32

        row_y += ROW_HEIGHT

    canvas.save(output_path, "PNG")
    print(f"      [OK] Infographic saved: {output_path}")
    return output_path
