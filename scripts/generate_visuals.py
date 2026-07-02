import os
import json
import time
import random
from datetime import datetime

class UpgradingVisualEngine:
    def __init__(self):
        # Initial core visual signatures (Version 1.0)
        self.visual_dna = {
            "version": 1.0,
            "last_upgrade": datetime.now().strftime("%Y-%m-%d"),
            "active_compositing_rules": ["split_screen_diagonal", "framed_focus"],
            "parallax_depth_range": [0.05, 0.20],
            "motion_easing_profiles": ["cubic-bezier(0.4, 0, 0.2, 1)"],
            "glitch_artefact_chance": 0.05
        }
        self.themes = {
            "neon_corporate": {"bg": "#0a0a16", "accent": "#39ff14", "text_primary": "#ffffff"},
            "wall_street_crash": {"bg": "#1c0606", "accent": "#ff3333", "text_primary": "#ffff00"},
            "bubble_burst": {"bg": "#0f011a", "accent": "#00ffff", "text_primary": "#ffffff"}
        }

    def check_for_upgrades(self):
        """Dynamic upgrade logic: Checks current date vs last upgrade date."""
        today = datetime.now()
        last_upgrade_date = datetime.strptime(self.visual_dna["last_upgrade"], "%Y-%m-%d")
        days_since_upgrade = (today - last_upgrade_date).days

        # Evolve every 14 days to simulate human iteration and fool detection
        if days_since_upgrade >= 14:
            print("🔄 AESTHETIC UPGRADE INITIATED: Injecting new visual signature...")
            self.evolve_visual_system()

    def evolve_visual_system(self):
        """Mutates the visual pipeline by introducing more complex techniques."""
        # 1. New Composition Rules
        complex_rules = ["complex_tiling", "layered_storyboard", "integrated_commentary"]
        new_rule = random.choice(complex_rules)
        if new_rule not in self.visual_dna["active_compositing_rules"]:
            self.visual_dna["active_compositing_rules"].append(new_rule)
        
        # 2. Increase Parallax & Depth Variation
        self.visual_dna["parallax_depth_range"][1] += 0.05 # Increase depth
        
        # 3. Add Human Editing Techniques (e.g., subtle digital camera shake)
        if random.random() > 0.5:
            self.visual_dna["motion_easing_profiles"].append("cubic-bezier(0.25, 0.1, 0.25, 1)")

        self.visual_dna["version"] += 0.1
        self.visual_dna["last_upgrade"] = datetime.now().strftime("%Y-%m-%d")
        print(f"✅ VISUAL SYSTEM UPGRADED to v{self.visual_dna['version']:.1f}. Active Techniques: {self.visual_dna['active_compositing_rules']}")

    def generate_human_composition(self, scene_data, company_name):
        """Generates dynamic composition based on CURRENTLY evolved rules."""
        # Check and apply upgrades first
        self.check_for_upgrades()
        
        print(f"🎨 Visual Supervisor: Composition started for {company_name} (Pipeline v{self.visual_dna['version']:.1f}).")
        
        selected_theme = random.choice(list(self.themes.values()))
        active_rule = random.choice(self.visual_dna["active_compositing_rules"])
        
        composition = {
            "visual_signature_v": self.visual_dna["version"],
            "layout_style": active_rule,
            "theme_colors": selected_theme,
            "background_layer": {
                "color": selected_theme["bg"],
                "blur_radius": 15,
                "scale_multiplier": 1.15
            },
            "parallax_mapping": {
                "depth_factor": random.uniform(self.visual_dna["parallax_depth_range"][0], self.visual_dna["parallax_depth_range"][1]),
                "motion_easing": random.choice(self.visual_dna["motion_easing_profiles"])
            },
            "kinetic_typography": {
                "color_highlight": selected_theme["accent"],
                "border_size": "5px"
            }
        }
        
        print(f"⚡ Layout complete: Applied [{active_rule}] structure with dynamic depth and human motion curves.")
        return composition

if __name__ == "__main__":
    # Test execution
    engine = UpgradingVisualEngine()
    
    # 1. Simulate initial run
    engine.generate_human_composition({"text": "He lost billions in a single afternoon."}, "WeWork")
    
    # 2. Simulate a run in the future (cheat the system date)
    from datetime import timedelta
    engine.visual_dna["last_upgrade"] = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")
    
    # 3. Trigger immediate upgrade and check result
    engine.generate_human_composition({"text": "The entire board voted him out."}, "Uber")
