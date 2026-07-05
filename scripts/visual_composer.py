import os
import sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

class ProductionVisualEngine:
    def __init__(self):
        # High-retention theme configurations matching NEON STEEL aesthetics
        self.themes = [
            {"bg": (15, 15, 25), "text": (255, 255, 255), "accent": (0, 255, 180), "label": "NEON_STEEL"},
            {"bg": (20, 10, 15), "text": (255, 255, 255), "accent": (255, 70, 85), "label": "CYBER_PULSE"},
            {"bg": (10, 20, 25), "text": (240, 240, 255), "accent": (0, 195, 255), "label": "CELESTIAL"}
        ]

    def create_high_retention_frame(self, width, height, frame_num, phrase, theme):
        """Assembles a high-contrast multi-layered framework with visible visual anchors."""
        # Create a deep-tint baseline canvas
        canvas = Image.new("RGB", (width, height), color=theme["bg"])
        draw = ImageDraw.Draw(canvas)
        
        # 1. Procedural geometric pattern interrupts to eliminate flat black space
        grid_size = 80
        for x in range(0, width, grid_size):
            draw.line([(x, 0), (x, height)], fill=(40, 40, 50), width=1)
        for y in range(0, height, grid_size):
            draw.line([(0, y), (width, y)], fill=(40, 40, 50), width=1)

        # 2. Pulsing cinematic kinetic frame
        pulse = int(np.sin(frame_num * 0.2) * 12)
        draw.rectangle(
            [40 + pulse, 40 + pulse, width - 40 - pulse, height - 40 - pulse],
            outline=theme["accent"], width=8
        )

        # 3. High-impact typography configuration
        try:
            font = ImageFont.truetype("Arial", 75 if width > height else 65)
        except IOError:
            font = ImageFont.load_default()

        # Split text layers cleanly so long sentences wrap perfectly on mobile layouts
        words = phrase.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            if len(" ".join(current_line)) > 12:
                lines.append(" ".join(current_line[:-1]))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))

        # Render heavy multi-line drop shadows for extreme visibility
        y_offset = height // 2 - (len(lines) * 50)
        for line in lines:
            # High-contrast background text card tracking
            draw.text((width // 2 + 6, y_offset + 6), line, fill=(0, 0, 0), font=font, anchor="mm")
            # Alternating flash text highlight matrix to force eye retention
            flash_color = theme["text"] if (frame_num // 8) % 2 == 0 else theme["accent"]
            draw.text((width // 2, y_offset), line, fill=flash_color, font=font, anchor="mm")
            y_offset += 110

        return cv2.cvtColor(np.array(canvas), cv2.COLOR_RGB2BGR)

    def compile_production_video(self, company_name, video_type):
        width, height = (1080, 1920) if video_type.lower() == "short" else (1920, 1080)
        os.makedirs("output", exist_ok=True)
        output_filename = f"output/{company_name.lower()}_{video_type.lower()}.mp4"

        fps = 30
        duration_seconds = 15 if video_type.lower() == "short" else 30
        total_frames = fps * duration_seconds

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))

        # Corporate automation script narrative timeline sequence
        narrative_timeline = [
            f"THE INSANE REALITY OF {company_name.upper()}",
            "CORPORATE SECRETS EXPOSED",
            "THE SYSTEM IS RIGGED",
            "HOW THEY CONTROL THE MARKET",
            "NEON STEEL TECH UNLOCKED"
        ]

        print(f"🎬 Rendering true {duration_seconds}s high-retention structural layout for {output_filename}...")

        for frame_num in range(total_frames):
            # Advance phrases systematically across the video timeline
            phrase_index = (frame_num // (fps * 3)) % len(narrative_timeline)
            active_phrase = narrative_timeline[phrase_index]
            active_theme = self.themes[phrase_index % len(self.themes)]

            frame_img = self.create_high_retention_frame(width, height, frame_num, active_phrase, active_theme)
            video_writer.write(frame_img)

        video_writer.release()
        print(f"✅ Real-time multi-layer visual asset ready: {output_filename}")
        return output_filename

def execute_visual_pipeline(company_name):
    engine = ProductionVisualEngine()
    engine.compile_production_video(company_name, "short")
    engine.compile_production_video(company_name, "long")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "Airbnb"
    execute_visual_pipeline(target)
