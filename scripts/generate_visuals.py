import os
import json
import random

class HumanVisualEngine:
    def __init__(self):
        self.themes = {
            "neon_corporate": {"bg": "#0a0a16", "accent": "#39ff14", "text_primary": "#ffffff"},
            "wall_street_crash": {"bg": "#1c0606", "accent": "#ff3333", "text_primary": "#ffff00"},
            "bubble_burst": {"bg": "#0f011a", "accent": "#00ffff", "text_primary": "#ffffff"}
        }

    def generate_human_composition(self, scene_data, company_name):
        """
        Calculates complex, multi-layered visual compositions instead of simple full-screen images.
        """
        print(f"🎨 Design Room: Composition started for {company_name} scene.")
        
        # 1. Randomly assign a high-contrast human color palette
        selected_theme = random.choice(list(self.themes.values()))
        
        # 2. Layer Separation for Parallax (Foreground Character vs Background Depth)
        composition = {
            "layout_style": random.choice(["comic_book_panel", "split_screen_diagonal", "framed_focus"]),
            "background_layer": {
                "color": selected_theme["bg"],
                "blur_radius": 15,          # Simulates high-end human camera lens depth of field
                "scale_multiplier": 1.15    # Extra padding allows digital camera panning/zoom
            },
            "foreground_assets": {
                "vector_asset": f"assets/vectors/{company_name.lower()}_boss.png",
                "stroke_thickness": "6px",  # Thick, intentional human-drawn comic outlines
                "drop_shadow": "0px 15px 30px rgba(0,0,0,0.7)"
            },
            "kinetic_typography": {
                "font": "Impact_Custom",
                "color_main": selected_theme["text_primary"],
                "color_highlight": selected_theme["accent"],
                "border_size": "5px",
                "animation_curve": "cubic-bezier(0.25, 1, 0.5, 1)" # Human easing curves, not linear motion
            }
        }
        
        print(f"⚡ Visual Layout complete: Applied [{composition['layout_style']}] framing with depth-of-field separation.")
        return composition

if __name__ == "__main__":
    engine = HumanVisualEngine()
    # Test generation setup
    engine.generate_human_composition({"text": "He lost billions in a single afternoon."}, "WeWork")
