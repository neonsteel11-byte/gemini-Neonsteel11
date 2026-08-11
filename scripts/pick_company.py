import random, json, os

MANIFEST_PATH = "video_manifest.json"

TOPICS = [
    # Daily-use physical objects (highest priority -- proven best performer: Zipper at 243 views)
    "INVENTION:Zipper:Whitcomb Judson",
    "INVENTION:Velcro:George de Mestral",
    "INVENTION:Post-it Notes:Spencer Silver",
    "INVENTION:Silly Putty:James Wright",
    "INVENTION:Play-Doh:Noah McVicker",
    "INVENTION:Slinky:Richard James",
    "INVENTION:Super Glue:Harry Coover",
    "INVENTION:Bubble Wrap:Alfred Fielding and Marc Chavannes",
    "INVENTION:Microwave Oven:Percy Spencer",
    "INVENTION:Toothbrush:William Addis",
    "INVENTION:Safety Pin:Walter Hunt",
    "INVENTION:Ballpoint Pen:Laszlo Biro",
    "INVENTION:Umbrella:Samuel Fox",
    "INVENTION:Matches:John Walker",
    "INVENTION:Rubber Band:Stephen Perry",
    "INVENTION:Paper Clip:Johan Vaaler",
    "INVENTION:Sunglasses:Sam Foster",
    "INVENTION:Chewing Gum:Thomas Adams",
    "INVENTION:Bandage:Earle Dickson",
    "INVENTION:Zipper Lighter:George Blaisdell",
    "INVENTION:Alarm Clock:Levi Hutchins",
    "INVENTION:Contact Lenses:Kevin Tuohy",
    # Daily-use food/household items
    "INVENTION:Potato Chips:George Crum",
    "INVENTION:Corn Flakes:John Harvey Kellogg",
    "INVENTION:Chocolate Chip Cookies:Ruth Wakefield",
    "INVENTION:Popsicle:Frank Epperson",
    "INVENTION:Coca-Cola:John Pemberton",
    # How things work -- daily objects
    "HOWITWORKS:Bubble Wrap",
    "HOWITWORKS:Treadmill",
    "HOWITWORKS:Listerine",
    "HOWITWORKS:Chainsaw",
    "HOWITWORKS:Toothpaste",
    "HOWITWORKS:Zipper",
    "HOWITWORKS:Velcro",
    # Medical/science (still physical, still relatable)
    "INVENTION:Penicillin:Alexander Fleming",
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
