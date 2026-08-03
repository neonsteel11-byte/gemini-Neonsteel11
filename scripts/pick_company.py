import random
import json
import os

MANIFEST_PATH = "video_manifest.json"

# HIGH-ENGAGEMENT INVENTIONS (proven viral topics)
INVENTIONS = [
    "INVENTION:Potato Chips:George Crum",  # Food + revenge story
    "INVENTION:Penicillin:Alexander Fleming",  # Life-saving accident
    "INVENTION:Microwave Oven:Percy Spencer",  # Radar + chocolate bar
    "INVENTION:Post-it Notes:Spencer Silver",  # Failed glue
    "INVENTION:Velcro:George de Mestral",  # Burrs on dog
    "INVENTION:Silly Putty:James Wright",  # WWII rubber substitute
    "INVENTION:Play-Doh:Noah McVicker",  # Wallpaper cleaner → toy
    "INVENTION:Safety Glass:Edouard Benedictus",  # Dropped flask
    "INVENTION:Corn Flakes:John Harvey Kellogg",  # Stale wheat accident
    "INVENTION:Ice Pops:Frank Epperson",  # Kid forgot soda outside
    "INVENTION:Super Glue:Harry Coover",  # Failed gun sight
    "INVENTION:Slinky:Richard James",  # Knocked over spring
    "INVENTION:Teflon:Roy Plunkett",  # Leaking gas canister
    "INVENTION:X-Rays:Wilhelm Rontgen",  # Glowing screen mystery
    "INVENTION:Dynamite:Alfred Nobel",  # Nitroglycerin stabilization
]

def _load_manifest():
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def pick_company():
    manifest = _load_manifest()
    recent = [entry.get("company", "") for entry in manifest[-15:]]
    available = [inv for inv in INVENTIONS if inv not in recent]
    if not available:
        available = INVENTIONS
    return random.choice(available)

if __name__ == "__main__":
    print(pick_company())
