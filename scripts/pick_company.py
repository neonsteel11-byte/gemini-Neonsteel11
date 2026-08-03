"""
Picks a random high-engagement topic: accidental inventions, bizarre origins, 
or weird historical facts about everyday things.
"""
import random
import json
import os

MANIFEST_PATH = "video_manifest.json"

# HIGH-ENGAGEMENT TOPICS: Mix of accidents, weird original purposes, and hidden history
TOPICS = [
    # Accidental Inventions
    "INVENTION:Penicillin:Alexander Fleming",
    "INVENTION:Microwave Oven:Percy Spencer",
    "INVENTION:Post-it Notes:Spencer Silver",
    "INVENTION:Velcro:George de Mestral",
    "INVENTION:Saccharin:Constantin Fahlberg",
    "INVENTION:Teflon:Roy Plunkett",
    "INVENTION:X-Rays:Wilhelm Rontgen",
    "INVENTION:Vulcanized Rubber:Charles Goodyear",
    "INVENTION:Silly Putty:James Wright",
    "INVENTION:Play-Doh:Noah McVicker",
    "INVENTION:Slinky:Richard James",
    "INVENTION:Super Glue:Harry Coover",
    "INVENTION:Ice Pops:Frank Epperson",
    "INVENTION:Potato Chips:George Crum",
    "INVENTION:Chocolate Chip Cookies:Ruth Wakefield",
    "INVENTION:Safety Glass:Edouard Benedictus",
    "INVENTION:Corn Flakes:John Harvey Kellogg",
    
    # Weird Original Purposes (Bizarre History)
    "HOWITWORKS:Bubble Wrap",
    "HOWITWORKS:Treadmill",
    "HOWITWORKS:Listerine",
    "HOWITWORKS:Chainsaw",
    "HOWITWORKS:High Heels",
    "HOWITWORKS:Play-Doh",
    "HOWITWORKS:Coca-Cola",
    "HOWITWORKS:Viagra",
    "HOWITWORKS:Slinky",
    "HOWITWORKS:Heroin",
    
    # Bizarre Historical Facts / Money Stories
    "MONEY:The Great Emu War",
    "MONEY:Tulip Mania",
    "MONEY:The Louisiana Purchase",
    "MONEY:Alaska Purchase",
    "WIDE:The Origin of the 40-Hour Work Week",
    "WIDE:Why We Shake Hands",
    "WIDE:The History of the Fork",
    "WIDE:Why Stop Signs Are Red",
    "WIDE:The Invention of the Weekend",
]

def _load_manifest():
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def pick_company():
    manifest = _load_manifest()
    
    # Get topics we've used in the last 15 videos to ensure variety
    recent = [entry.get("company", "") for entry in manifest[-15:]]
    
    # Filter out recently used topics
    available = [topic for topic in TOPICS if topic not in recent]
    
    if not available:
        available = TOPICS  # Reset if all used recently
    
    selected = random.choice(available)
    return selected

if __name__ == "__main__":
    print(pick_company())
