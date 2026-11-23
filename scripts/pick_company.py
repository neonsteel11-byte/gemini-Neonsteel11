import random, json, os, sys, requests
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

MANIFEST_PATH = "video_manifest.json"
ALLTIME_USED_PATH = "topics_used_alltime.json"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

TOPICS = [
    "INVENTION:Teflon:Roy Plunkett",
    "INVENTION:Saccharin:Constantin Fahlberg",
    "INVENTION:Pacemaker:Wilson Greatbatch",
    "INVENTION:Stainless Steel:Harry Brearley",
    "INVENTION:Vulcanized Rubber:Charles Goodyear",
    "INVENTION:X-Rays:Wilhelm Roentgen",
    "INVENTION:Safety Glass:Edouard Benedictus",
    "INVENTION:Scotchgard:Patsy Sherman",
    "INVENTION:Mauve Dye:William Henry Perkin",
    "INVENTION:Aspartame:James Schlatter",
    "INVENTION:Smoke Detector:Walter Jaeger",
    "INVENTION:Tea Bags:Thomas Sullivan",
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
    "MONEY:The War of the Stray Dog Between Greece and Bulgaria",
    "MONEY:The Aroostook War Between Maine and New Brunswick",
    "MONEY:The Honey War Between Iowa and Missouri",
    "MONEY:The Whisky War Over Hans Island",
    "MONEY:The Rum Rebellion in Australia",
    "MONEY:The Chesapeake Bay Oyster Wars",
    "MONEY:The Dogger Bank Incident Between Russia and Britain",
    "MONEY:The Great Emu War",
    "MONEY:The Cod Wars Between Iceland and Britain",
    "MONEY:The War of the Bucket",
    "MONEY:The Pig War Between the US and Britain",
    "MONEY:The Football War Between El Salvador and Honduras",
    "MONEY:The Anglo-Zanzibar War, the Shortest War in History",
    "MONEY:The Pastry War Between France and Mexico",
    "MONEY:The War of Jenkins' Ear",
    "MONEY:The Kettle War Between the Dutch and Holy Roman Empire",
    "MONEY:The Toledo War Between Ohio and Michigan",
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


def _is_concrete_story(title):
    """Reject abstract/systemic topics (e.g. trade routes, banking systems) and
    only accept concrete, single, visual, story-driven events. Defaults to
    rejecting if Groq is unavailable, to stay conservative."""
    if not GROQ_API_KEY:
        return False
    prompt = f"""Is the following a CONCRETE, SINGLE, VISUAL, story-driven historical event
(like "The Great Emu War" or "The Pig War" -- something with a clear beginning, middle,
and end that can be shown visually in a short video)?
Or is it an ABSTRACT, systemic, or conceptual topic (like ancient trade routes, monetary
policy, or a broad historical trend)?

Topic: "{title}"

Answer with ONLY one word: CONCRETE or ABSTRACT."""
    try:
        resp = requests.post(GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.2},
            timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            if "choices" in data and data["choices"]:
                answer = data["choices"][0]["message"]["content"].strip().upper()
                return "CONCRETE" in answer
    except Exception:
        pass
    return False


def _pop_hot_topic():
    """Take the hottest freshly-discovered real trending story that passes the
    concrete-story validity check, if any are queued. Discards invalid ones."""
    if not os.path.exists(MANUAL_QUEUE_PATH):
        return None
    try:
        with open(MANUAL_QUEUE_PATH, "r", encoding="utf-8") as f:
            queue = json.load(f)
        while queue:
            title = queue.pop(0)
            if _is_concrete_story(title):
                with open(MANUAL_QUEUE_PATH, "w", encoding="utf-8") as f:
                    json.dump(queue, f, indent=2)
                return f"MONEY:{title}"
            print(f"      [SKIP] Discarding non-story queued topic: {title}")
        with open(MANUAL_QUEUE_PATH, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=2)
        return None
    except Exception:
        return None


def _norm(s):
    return (s or "").strip().lower()


def _load_alltime_used(video_type="short"):
    """Every topic already used: the tracker file PLUS every video in the manifest
    of the same type, so repeats are blocked even if the tracker file is missing."""
    used = set()
    if os.path.exists(ALLTIME_USED_PATH):
        try:
            with open(ALLTIME_USED_PATH, "r", encoding="utf-8") as f:
                used |= {_norm(x) for x in json.load(f)}
        except Exception:
            pass
    for entry in _load_manifest():
        if entry.get("video_type", video_type) == video_type and entry.get("company"):
            used.add(_norm(entry["company"]))
    return used


def _save_alltime_used(used):
    with open(ALLTIME_USED_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(used), f, indent=2)


def _brainstorm_new_topic(video_type, used_names):
    """Ask Groq for a brand-new topic that hasn't been used. Returns None on failure."""
    if not GROQ_API_KEY:
        return None
    if video_type == "long":
        ask = ("a bizarre, little-known true historical WAR or conflict (in the style of The Great Emu War, "
               "The Cod Wars, The Pig War) that makes a compelling story-driven video. Return ONLY the event name.")
    else:
        ask = ("a famous everyday object that was invented completely by accident, with a real, well-documented "
               "inventor. Return ONLY: Object Name | Inventor Full Name")
    prompt = (f"Suggest ONE topic for a YouTube video about {ask}\n"
              f"Do not suggest any of these already-used topics: {', '.join(sorted(used_names)) or 'none yet'}.\n"
              "No quotes, no explanation.")
    try:
        resp = requests.post(GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 1.0},
            timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("choices"):
                text = data["choices"][0]["message"]["content"].strip().strip('"').split("\n")[0].strip()
                if video_type == "long":
                    return f"MONEY:{text}" if text else None
                if "|" in text:
                    obj, inv = [x.strip() for x in text.split("|", 1)]
                    if obj and inv:
                        return f"INVENTION:{obj}:{inv}"
    except Exception as e:
        print(f"[WARNING] Groq brainstorm failed: {e}", file=sys.stderr)
    return None


def pick_company(video_type="short"):
    alltime_used = _load_alltime_used(video_type)
    manifest = _load_manifest()
    recent = {_norm(e.get("company", "")) for e in manifest[-15:]}

    if video_type == "long":
        hot = _pop_hot_topic()
        if hot and _norm(_short_name(hot)) not in alltime_used:
            alltime_used.add(_norm(_short_name(hot)))
            _save_alltime_used(alltime_used)
            return hot

    pool = LONGFORM_TOPICS if video_type == "long" else TOPICS
    available = [t for t in pool if _norm(_short_name(t)) not in alltime_used]

    if not available:
        for _ in range(3):
            new_topic = _brainstorm_new_topic(video_type, alltime_used)
            if new_topic and _norm(_short_name(new_topic)) not in alltime_used:
                alltime_used.add(_norm(_short_name(new_topic)))
                _save_alltime_used(alltime_used)
                return new_topic
        # Groq unavailable: least-recent repeat rather than a hard failure.
        available = [t for t in pool if _norm(_short_name(t)) not in recent] or pool

    chosen = random.choice(available)
    alltime_used.add(_norm(_short_name(chosen)))
    _save_alltime_used(alltime_used)
    return chosen


if __name__ == "__main__":
    video_type = sys.argv[1] if len(sys.argv) > 1 else "short"
    print(pick_company(video_type))
