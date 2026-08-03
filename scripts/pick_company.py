"""
Picks a random accidental invention/discovery for today's video.
Focuses on real inventors and their real inventions.
"""
import random
import json
import os

MANIFEST_PATH = "video_manifest.json"

# ACCIDENTAL INVENTIONS with real inventors
INVENTIONS = [
    "INVENTION:Penicillin:Alexander Fleming",
    "INVENTION:Microwave Oven:Percy Spencer",
    "INVENTION:Post-it Notes:Spencer Silver",
    "INVENTION:Velcro:George de Mestral",
    "INVENTION:Saccharin:Constantin Fahlberg",
    "INVENTION:Teflon:Roy Plunkett",
    "INVENTION:X-Rays:Wilhelm Rontgen",
    "INVENTION:Vulcanized Rubber:Charles Goodyear",
    "INVENTION:Dynamite:Alfred Nobel",
    "INVENTION:Safety Glass:Edouard Benedictus",
    "INVENTION:Corn Flakes:John Harvey Kellogg",
    "INVENTION:Play-Doh:Noah McVicker",
    "INVENTION:Slinky:Richard James",
    "INVENTION:Silly Putty:James Wright",
    "INVENTION:Super Glue:Harry Coover",
    "INVENTION:Ice Pops:Frank Epperson",
    "INVENTION:Potato Chips:George Crum",
    "INVENTION:Chocolate Chip Cookies:Ruth Wakefield",
    "INVENTION:Champagne:Dom Perignon",
    "INVENTION:Gunpowder:Chinese Alchemists",
]

def _load_manifest():
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def pick_company():
    manifest = _load_manifest()
    
    # Get inventions we've used in the last 10 videos
    recent = [entry.get("company", "") for entry in manifest[-10:]]
    
    # Filter out recently used inventions
    available = [inv for inv in INVENTIONS if inv not in recent]
    
    if not available:
        available = INVENTIONS  # Reset if all used recently
    
    selected = random.choice(available)
    return selected

if __name__ == "__main__":
    # CRITICAL: ONLY print the selected string. 
    # No extra text, so it doesn't break GitHub Actions GITHUB_OUTPUT.
    print(pick_company())
