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

REDDIT_URL = "https://www.reddit.com/r/todayilearned/top.json"
USED_IDS_PATH = "til_used_ids.json"
QUEUE_PATH = "manual_topics.json"

KEYWORDS = ["accidentally", "by accident", "by mistake", "fluke", "accident led",
            "unintentionally", "randomly discovered", "happy accident"]


def fetch_candidates(limit=50, timeframe="month"):
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
        # TIL titles usually start with "TIL that..." -- strip that prefix
        clean_title = re.sub(r"^TIL\s*(that)?\s*", "", title, flags=re.IGNORECASE).strip()
        if upvotes < 500:
            continue
        if not any(kw in title.lower() for kw in KEYWORDS):
            continue
        candidates.append({"id": post_id, "title": clean_title, "upvotes": upvotes})
    return candidates


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
        queue.append(c["title"])
        used_ids.add(c["id"])
        added += 1
        if added >= 10:  # cap per run so the queue doesn't explode
            break

    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2)
    with open(USED_IDS_PATH, "w", encoding="utf-8") as f:
        json.dump(list(used_ids), f, indent=2)

    print(f"Added {added} new topics from r/todayilearned. Queue now has {len(queue)} items.")


if __name__ == "__main__":
    main()
