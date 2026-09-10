import random, json, os, sys, requests
from config import GROQ_API_KEY, GROQ_MODEL

MANIFEST_PATH = "video_manifest.json"
ALLTIME_USED_PATH = "topics_used_alltime.json"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

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
    "INVENTION:Potato Chips:George Crum",
    "INVENTION:Corn Flakes:John Harvey Kellogg",
    "INVENTION:Chocolate Chip Cookies:Ruth Wakefield",
    "INVENTION:Popsicle:Frank Epperson",
    "INVENTION:Coca-Cola:John Pemberton",
    "HOWITWORKS:Bubble Wrap",
    "HOWITWORKS:Treadmill",
    "HOWITWORKS:Listerine",
    "HOWITWORKS:Chainsaw",
    "HOWITWORKS:Toothpaste",
    "HOWITWORKS:Zipper",
    "HOWITWORKS:Velcro",
    "INVENTION:Penicillin:Alexander Fleming",
    "LISTICLE:Everyday Objects With Insane Origin Stories",
    "LISTICLE:Scientists Who Changed Everything By Accident",
    "LISTICLE:Inventions That Were Total Mistakes",
    "LISTICLE:Household Items You Never Knew Had a Wild History",
]

# Long-form gets its OWN dedicated pool of unique, narrative-driven historical
# events (Emu War-style) -- kept separate from Shorts, which stays focused on
# famous, everyday accidental inventions only.
LONGFORM_TOPICS = [
    "MONEY:The Great Emu War",
    "MONEY:Tulip Mania",
    "MONEY:The Cod Wars Between Iceland and Britain",
    "MONEY:The War of the Bucket",
    "MONEY:The Great Molasses Flood of Boston",
    "MONEY:The Pig War Between the US and Britain",
    "MONEY:The Toilet Paper Panic of 1973",
    "MONEY:The Great Stork Derby",
]


def _load_manifest():
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _short_name(topic):
    """Extract the comparable short name from a topic string, e.g.
    "INVENTION:Zipper Lighter:George Blaisdell" -> "Zipper Lighter",
    matching the plain names actually stored in the manifest."""
    parts = topic.split(":")
    return parts[1] if len(parts) > 1 else parts[0]


MANUAL_QUEUE_PATH = "manual_topics.json"


def _pop_hot_topic():
    """Take the hottest freshly-discovered real trending story, if any are queued."""
    if not os.path.exists(MANUAL_QUEUE_PATH):
        return None
    try:
        with open(MANUAL_QUEUE_PATH, "r", encoding="utf-8") as f:
            queue = json.load(f)
        if not queue:
            return None
        title = queue.pop(0)
        with open(MANUAL_QUEUE_PATH, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=2)
        return f"MONEY:{title}"
    except Exception:
        return None


def _load_alltime_used():
    if os.path.exists(ALLTIME_USED_PATH):
        with open(ALLTIME_USED_PATH, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def _save_alltime_used(used):
    with open(ALLTIME_USED_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(used), f, indent=2)


def _brainstorm_new_topic(video_type, used_names):
    """Ask Groq for a brand-new topic, in the channel's existing style, that
    hasn't been used before. Returns None if Groq is unavailable or fails."""
    if not GROQ_API_KEY:
        return None
    if video_type == "long":
        style = "a bizarre, little-known true historical event (in the style of The Great Emu War, Tulip Mania, The Cod Wars) that would make a compelling story-driven video"
        prefix = "MONEY"
    else:
        style = "a famous everyday object that was invented completely by accident"
        prefix = "INVENTION"
    prompt = f"""Suggest ONE topic for a YouTube video about {style}.
Do not suggest any of these already-used topics: {', '.join(sorted(used_names)) or 'none yet'}.
Return ONLY the topic name, nothing else, no quotes, no explanation."""
    try:
        resp = requests.post(GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 1.0},
            timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if "choices" in data and data["choices"]:
                title = data["choices"][0]["message"]["content"].strip().strip('"')
                if title:
                    if prefix == "INVENTION":
                        return f"INVENTION:{title}:Unknown"
                    return f"{prefix}:{title}"
    except Exception as e:
        print(f"[WARNING] Groq brainstorm failed: {e}", file=sys.stderr)
    return None


def pick_company(video_type="short"):
    alltime_used = _load_alltime_used()
    manifest = _load_manifest()
    recent = [entry.get("company", "") for entry in manifest[-15:]]

    if video_type == "long":
        hot = _pop_hot_topic()
        if hot and _short_name(hot) not in alltime_used:
            alltime_used.add(_short_name(hot))
            _save_alltime_used(alltime_used)
            return hot

    pool = LONGFORM_TOPICS if video_type == "long" else TOPICS
    available = [t for t in pool if _short_name(t) not in alltime_used]

    if not available:
        new_topic = _brainstorm_new_topic(video_type, alltime_used)
        if new_topic:
            alltime_used.add(_short_name(new_topic))
            _save_alltime_used(alltime_used)
            return new_topic
        # Groq brainstorm unavailable/failed -- fall back to least-recently-used
        # repeat rather than a hard failure.
        available = [t for t in pool if _short_name(t) not in recent] or pool

    chosen = random.choice(available)
    alltime_used.add(_short_name(chosen))
    _save_alltime_used(alltime_used)
    return chosen


if __name__ == "__main__":
    video_type = sys.argv[1] if len(sys.argv) > 1 else "short"
    print(pick_company(video_type))
