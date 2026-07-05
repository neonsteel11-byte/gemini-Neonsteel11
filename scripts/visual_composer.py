import os
import sys
import numpy as np
import cv2
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

class FutureProofVisualEngine:
    def __init__(self):
        self.day_of_year = datetime.now().timetuple().tm_yday
        self.evolution_cycle = self.day_of_year % 4

    def determine_current_aesthetic_tier(self):
        # RGB Formats
        if self.evolution_cycle == 0:
            return {"bg_tint": (15, 15, 25), "accent_color": (0, 255, 180), "style_name": "Neon Steel Kinetic"}
        elif self.evolution_cycle == 1:
            return {"bg_tint": (20, 10, 15), "accent_color": (255, 70, 85), "style_name": "Cyber Obsidian Pulse"}
        elif self.evolution_cycle == 2:
            return {"bg_tint": (10, 20, 25), "accent_color": (0, 195, 255), "style_name": "Deep Celestial Aura"}
        else:
            return {"bg_tint": (15, 20, 15), "accent_color": (212, 175, 55), "style_name": "Liquid Gold Minimalist"}

    def compile_high_retention_frames(self, company_name, video_type):
        style = self.determine_current_aesthetic_tier()
        print(f"🎬 [Visual Composer]: Activating Visual Architecture Tier: {style['style_name']}")

        width, height = (1080, 1920) if video_type.lower() == "short" else (1920, 1080)
        os.makedirs("output", exist_ok=True)
        output_filename = f"output/{company_name.lower()}_{video_type.lower()}.mp4"

        # 🎞️ Set up a real video writer (30 FPS, 5-second duration = 150 frames total)
        fps = 30
        total_frames = 150
        
        # Use MP4V for native cross-platform runner compatibility
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))

        text_content = f"THE REAL REALITY OF {company_name.upper()}"
        font = ImageFont.load_default()

        print(f"🔄 Encoding {total_frames} absolute video frames for {video_type} container...")

        for frame_num in range(total_frames):
            # Create a clean PIL canvas
            canvas = Image.new("RGB", (width, height), color=style["bg_tint"])
            draw = ImageDraw.Draw(canvas)

            # Make the accent border pulsate slightly based on the frame index
            pulse_offset = int(np.sin(frame_num * 0.1) * 10)
            draw.rectangle(
                [int(width*0.05) + pulse_offset, int(height*0.05) + pulse_offset, 
                 int(width*0.95) - pulse_offset, int(height*0.95) - pulse_offset], 
                outline=style["accent_color"], width=6
            )

            # Draw corporate text target
            draw.text((int(width/2), int(height/2)), text_content, fill=(255, 255, 255), anchor="mm")

            # Convert frame from RGB (PIL standard) to BGR (OpenCV standard)
            frame_np = np.array(canvas)
            frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)

            # Write the raw frame array directly into the video output pipeline
            video_writer.write(frame_bgr)

        video_writer.release()
        print(f"✅ Visual Composer successfully synthesized production video asset: {output_filename}")
        return output_filename

def execute_visual_pipeline(company_name):
    engine = FutureProofVisualEngine()
    short_path = engine.compile_high_retention_frames(company_name, "short")
    long_path = engine.compile_high_retention_frames(company_name, "long")
    return short_path, long_path

if __name__ == "__main__":
    if len(sys.argv) > 1:
        execute_visual_pipeline(sys.argv[1])
    else:
        execute_visual_pipeline("Airbnb")
