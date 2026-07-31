"""
10-slot rotation across the 5 formats that are actually performing:
3x invention-history (top performer), 2x money-story, 2x wide-topic,
2x how-it-works, 1x listicle. No more single-company POV or vs-comparison
-- retired per direct feedback that they were underperforming/boring.
"""
import json
import os
import sys

INVENTIONS_PATH = "inventions.json"
MONEY_PATH = "money_stories.json"
WIDE_PATH = "wide_topics.json"
LISTICLE_PATH = "listicle_topics.json"
HOWITWORKS_PATH = "how_it_works_topics.json"
MANUAL_QUEUE_PATH = "manual_topics.json"
STATE_PATH = "company_state.json"


def _load(path):
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else []


def _try_manual_queue():
    if not os.path.exists(MANUAL_QUEUE_PATH):
        return None
    queue = _load(MANUAL_QUEUE_PATH)
    if not queue:
        return None
    topic = queue.pop(0)
    with open(MANUAL_QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2)
    return topic


def main():
    manual_topic = _try_manual_queue()
    if manual_topic:
        print(manual_topic)
        return

    inventions = _load(INVENTIONS_PATH)
    money_stories = _load(MONEY_PATH)
    wide_topics = _load(WIDE_PATH)
    listicles = _load(LISTICLE_PATH)
    how_it_works = _load(HOWITWORKS_PATH)

    last_index = -1
    if os.path.exists(STATE_PATH):
        last_index = json.load(open(STATE_PATH, encoding="utf-8")).get("last_index", -1)

    next_index = last_index + 1
    slot = next_index % 10
    cycle_pos = next_index // 10

    if slot in (0, 1, 2) and inventions:
        i_idx = (cycle_pos * 3 + slot) % len(inventions)
        item = inventions[i_idx]
        output = f"INVENTION:{item['invention']}:{item['inventor']}"
    elif slot in (3, 4) and money_stories:
        m_idx = (cycle_pos * 2 + (slot - 3)) % len(money_stories)
        output = f"MONEY:{money_stories[m_idx]}"
    elif slot in (5, 6) and wide_topics:
        w_idx = (cycle_pos * 2 + (slot - 5)) % len(wide_topics)
        output = f"WIDE:{wide_topics[w_idx]}"
    elif slot in (7, 8) and how_it_works:
        h_idx = (cycle_pos * 2 + (slot - 7)) % len(how_it_works)
        output = f"HOWITWORKS:{how_it_works[h_idx]}"
    elif listicles:
        l_idx = cycle_pos % len(listicles)
        output = f"LISTICLE:{listicles[l_idx]}"
    else:
        i_idx = cycle_pos % len(inventions)
        item = inventions[i_idx]
        output = f"INVENTION:{item['invention']}:{item['inventor']}"

    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump({"last_index": next_index}, f)

    print(output)


if __name__ == "__main__":
    main()
