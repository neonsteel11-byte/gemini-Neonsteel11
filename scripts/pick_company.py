import random, json, os

MANIFEST_PATH = "video_manifest.json"

TOPICS = [
    "INVENTION:Penicillin:Alexander Fleming",
    "INVENTION:Microwave Oven:Percy Spencer",
    "INVENTION:Post-it Notes:Spencer Silver",
    "INVENTION:Velcro:George de Mestral",
    "INVENTION:Silly Putty:James Wright",
    "INVENTION:Play-Doh:Noah McVicker",
    "INVENTION:Slinky:Richard James",
    "INVENTION:Super Glue:Harry Coover",
    "INVENTION:Potato Chips:George Crum",
    "INVENTION:Corn Flakes:John Harvey Kellogg",
    "HOWITWORKS:Bubble Wrap",
    "HOWITWORKS:Treadmill",
    "HOWITWORKS:Listerine",
    "HOWITWORKS:Chainsaw",
    "MONEY:The Great Emu War",
    "MONEY:Tulip Mania",
]

def _load_manifest():
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def pick_company():
    manifest = _load_manifest()
    recent = [entry.get("company", "") for entry in manifest[-10:]]
    available = [t for t in TOPICS if t not in recent]
    if not available:
        available = TOPICS
    return random.choice(available)

if __name__ == "__main__":
    print(pick_company())
