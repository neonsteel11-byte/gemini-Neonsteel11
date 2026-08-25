"""
Shows what topic is queued up next WITHOUT consuming it -- lets you preview
tomorrow's video topic ahead of time. Run anytime: python scripts/peek_next_topic.py
"""
import json
import os

QUEUE_PATH = "manual_topics.json"


def main():
    if not os.path.exists(QUEUE_PATH):
        print("No hot-topic queue found yet -- next video will use the fallback list.")
        return
    with open(QUEUE_PATH, "r", encoding="utf-8") as f:
        queue = json.load(f)
    if not queue:
        print("Hot-topic queue is empty right now -- next video will use the fallback list.")
        return
    print(f"Next hot topic queued: {queue[0]}")
    print(f"({len(queue)} hot topics currently waiting in the queue)")


if __name__ == "__main__":
    main()
