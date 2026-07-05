import os
import sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

class ProductionVisualEngine:
    def __init__(self):
        # High-impact retention color combinations
        self.themes = [
            {"bg": (10, 10, 15), "text": (255, 255, 255), "accent": (0, 235, 150), "label": "FINANCE_DARK"},
            {"bg": (15, 5, 10), "text": (255, 255, 255), "accent": (255, 60, 90), "label": "CRIMSON_PULSE"},
            {"bg": (5, 15, 20), "text": (240, 240, 255), "accent": (0, 180, 255), "label": "CELESTIAL_METRIC"}
        ]

    def draw_gradient_background(self, draw, width, height, theme):
        """Generates a high-contrast dynamic gradient backdrop to replace flat black panels."""
        base_color = theme["bg"]
        for y in range(height):
            # Smoothly blend from dark to deep accent tone
            ratio = y / height
            r = int(base_color[0] * (1 - ratio) + theme["accent"][0] * 0.1 * ratio)
            g = int(base_color[1] * (1 - ratio) + theme["accent"][1] * 0.1 * ratio)
            b = int(base_color[2] * (1 - ratio) + theme["accent"][2] * 0.1 * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

    def create_scene_frame(self, width, height, frame_num, phrase, theme):
        """Assembles a multi-layered cinematic asset frame with rapid pattern interrupts."""
        canvas = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(canvas)
        
        # 1. Background Generation
        self.draw_gradient_background(draw, width, height, theme)

        # 2. Add Active Framing Borders
        border_pulse = int(np.sin(frame_num * 0.15) * 8)
        draw.rectangle(
            [40 + border_pulse, 40 + border_pulse, width - 40 - border_pulse, height - 40 - border_pulse],
            outline=theme["accent"], width=8
        )

        # 3. Dynamic Pattern Interrupt: Alternating background contrast flash to retain eyes
        if (frame_num // 15) % 2 == 0:
            draw.rectangle([50, 50, width - 50, height - 50], outline=(255, 255, 255), width=2)

        # 4. Heavy-Scale Text Layout Compilation
        # Fallback to standard system true-type fonts if available, otherwise load scalable array
        try:
            font = ImageFont.truetype("Arial", 80 if width > height else 70)
        except IOError:
            font = ImageFont.load_default()

        # Split long text arrays cleanly so they wrap inside mobile screens
        words = phrase.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            if len(" ".join(current_line)) > 15:
                lines.append(" ".join(current_line[:-1]))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))

        # Render rows with heavy drop-shadowing for clarity and contrast
        y_offset = height // 2 - (len(lines) * 45)
        for line in lines:
            # Draw shadow tracking
            draw.text((width // 2 + 5, y_offset + 5), line, fill=(0, 0, 0), font=font, anchor="mm")
            # Draw primary high-impact accent fill
            draw.text((width // 2, y_offset), line, fill=theme["text"] if (frame_num // 10) % 2 == 0 else theme["accent"], font=font, anchor="mm")
            y_offset += 95

        return cv2.cvtColor(np.array(canvas), cv2.COLOR_RGB2BGR)

    def compile_narrative_video(self, company_name, video_type):
        theme = self.themes[0]
        width, height = (1080, 1920) if video_type.lower() == "short" else (1920, 1080)
        os.makedirs("output", exist_ok=True)
        output_filename = f"output/{company_name.lower()}_{video_type.lower()}.mp4"

        fps = 30
        duration_seconds = 30 if video_type.lower() == "short" else 60
        total_frames = fps * duration_seconds

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))

        # Dynamic narrative timeline structure to stop user scrolling
        script_timeline = [
            "THE INSANE REALITY OF " + company_name.upper(),
            "HOW THEY FOOLED EVERYONE",
            "THE SECRET MONETIZATION TRICK",
            "THE REVENUE STREAM EXPOSED",
            "WHY IT IS COLLAPSING RIGHT NOW",
            "SUBSCRIBE TO THE SYSTEM FOR MORE"
        ]

        print(f"🎬 [VISION Core]: Rendering true {duration_seconds}s high-retention cinematic array for {output_filename}...")

        for frame_num in range(total_frames):
            # Rotate phrases dynamically over time across the length of the video
            phrase_index = (frame_num // (fps * 5)) % len(script_timeline)
            active_phrase = script_timeline[phrase_index]

            # Rotate style themes matching the phrase shifts
            active_theme = self.themes[phrase_index % len(self.themes)]

            frame_img = self.create_scene_frame(width, height, frame_num, active_phrase, active_theme)
            video_writer.write(frame_img)

        video_writer.release()
        print(f"✅ Real-time asset render complete: {output_filename}")
        return output_filename

def execute_visual_pipeline(company_name):
    engine = ProductionVisualEngine()
    engine.compile_narrative_video(company_name, "short")
    engine.compile_narrative_video(company_name, "long")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "Airbnb"
    execute_visual_pipeline(target)
