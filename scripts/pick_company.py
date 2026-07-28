"""
8-slot rotation: 2x invention, 2x money-story, 2x wide-topic (general trivia,
NOT company-related), 1x single-company POV, 1x comparison.
"""
import json
import os
import sys

COMPANIES_PATH = "companies.json"
INVENTIONS_PATH = "inventions.json"
MONEY_PATH = "money_stories.json"
WIDE_PATH = "wide_topics.json"
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

    companies = _load(COMPANIES_PATH)
    inventions = _load(INVENTIONS_PATH)
    money_stories = _load(MONEY_PATH)
    wide_topics = _load(WIDE_PATH)

    last_index = -1
    if os.path.exists(STATE_PATH):
        last_index = json.load(open(STATE_PATH, encoding="utf-8")).get("last_index", -1)

    listicles = _load("listicle_topics.json")

    next_index = last_index + 1
    slot = next_index % 9
    cycle_pos = next_index // 9

    if slot in (0, 1) and inventions:
        i_idx = (cycle_pos * 2 + slot) % len(inventions)
        item = inventions[i_idx]
        output = f"INVENTION:{item['invention']}:{item['inventor']}"
    elif slot in (2, 3) and money_stories:
        m_idx = (cycle_pos * 2 + (slot - 2)) % len(money_stories)
        output = f"MONEY:{money_stories[m_idx]}"
    elif slot in (4, 5) and wide_topics:
        w_idx = (cycle_pos * 2 + (slot - 4)) % len(wide_topics)
        output = f"WIDE:{wide_topics[w_idx]}"
    elif slot == 6 and listicles:
        l_idx = cycle_pos % len(listicles)
        output = f"LISTICLE:{listicles[l_idx]}"
    elif slot == 7:
        c_idx = cycle_pos % len(companies)
        output = companies[c_idx]
    else:
        c_idx = cycle_pos % len(companies)
        pair_idx = (c_idx + 1) % len(companies)
        output = f"{companies[c_idx]}|{companies[pair_idx]}"

    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump({"last_index": next_index}, f)

    print(output)


if __name__ == "__main__":
    main()
