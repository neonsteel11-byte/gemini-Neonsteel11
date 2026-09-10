"""
Pulls real "accidentally discovered" stories from r/todayilearned's public
JSON API (no auth/key needed for read-only subreddit data) and queues fresh
ones into manual_topics.json for the pipeline to use. Tracks used post IDs
so nothing repeats.
"""
import json
import os
import re
import sys
import requests
from config import GROQ_API_KEY, GROQ_MODEL

REDDIT_URL = "https://www.reddit.com/r/todayilearned/top.json"
USED_IDS_PATH = "til_used_ids.json"
QUEUE_PATH = "manual_topics.json"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

KEYWORDS = ["accidentally", "by accident", "by mistake", "fluke", "accident led",
            "unintentionally", "randomly discovered", "happy accident"]


def fetch_candidates(limit=50, timeframe="week"):
    headers = {"User-Agent": "AccidentalGeniusBot/1.0"}
    params = {"limit": limit, "t": timeframe}
    try:
        resp = requests.get(REDDIT_URL, headers=headers, params=params, timeout=20)
        if resp.status_code != 200:
            print(f"[WARNING] Reddit fetch failed: {resp.status_code}", file=sys.stderr)
            return []
        posts = resp.json()["data"]["children"]
    except Exception as e:
        print(f"[WARNING] Reddit fetch error: {e}", file=sys.stderr)
        return []

    candidates = []
    for post in posts:
        data = post["data"]
        title = data.get("title", "")
        post_id = data.get("id", "")
        upvotes = data.get("ups", 0)
        clean_title = re.sub(r"^TIL\s*(that)?\s*", "", title, flags=re.IGNORECASE).strip()
        if upvotes < 500:
            continue
        if not any(kw in title.lower() for kw in KEYWORDS):
            continue
        candidates.append({"id": post_id, "title": clean_title, "upvotes": upvotes})
    candidates.sort(key=lambda c: c["upvotes"], reverse=True)
    return candidates


def _is_concrete_story(title):
    """Reject abstract/systemic topics (e.g. trade routes, banking systems) and
    only accept concrete, single, visual, story-driven events -- the same style
    as the channel's existing Emu War/Tulip Mania content. Defaults to rejecting
    if Groq is unavailable, to stay conservative."""
    if not GROQ_API_KEY:
        return False
    prompt = f"""Is the following a CONCRETE, SINGLE, VISUAL, story-driven historical event or object
(like "The Great Emu War" or "Tulip Mania" -- something with a clear beginning, middle,
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
    except Exception as e:
        print(f"[WARNING] Groq validation failed for '{title}': {e}", file=sys.stderr)
    return False


def main():
    used_ids = set()
    if os.path.exists(USED_IDS_PATH):
        with open(USED_IDS_PATH, "r", encoding="utf-8") as f:
            used_ids = set(json.load(f))

    queue = []
    if os.path.exists(QUEUE_PATH):
        with open(QUEUE_PATH, "r", encoding="utf-8") as f:
            queue = json.load(f)

    candidates = fetch_candidates()
    added = 0
    for c in candidates:
        if c["id"] in used_ids:
            continue
        used_ids.add(c["id"])
        if not _is_concrete_story(c["title"]):
            print(f"[SKIP] Rejected as abstract/non-visual: {c['title']}")
            continue
        queue.append(c["title"])
        added += 1
        if added >= 10:
            break

    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2)
    with open(USED_IDS_PATH, "w", encoding="utf-8") as f:
        json.dump(list(used_ids), f, indent=2)

    print(f"Added {added} new topics from r/todayilearned. Queue now has {len(queue)} items.")


if __name__ == "__main__":
    main()
