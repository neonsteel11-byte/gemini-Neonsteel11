"""
Picks today's content. 6-slot cycle: 2x invention-history (proven winner),
2x money-stories (new test format), 1x single-company POV, 1x comparison.
"""
import json
import os
import sys

COMPANIES_PATH = "companies.json"
INVENTIONS_PATH = "inventions.json"
MONEY_PATH = "money_stories.json"
MANUAL_QUEUE_PATH = "manual_topics.json"
STATE_PATH = "company_state.json"


def _try_manual_queue():
    if not os.path.exists(MANUAL_QUEUE_PATH):
        return None
    with open(MANUAL_QUEUE_PATH, "r", encoding="utf-8") as f:
        queue = json.load(f)
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

    with open(COMPANIES_PATH, "r", encoding="utf-8") as f:
        companies = json.load(f)
    inventions = json.load(open(INVENTIONS_PATH, encoding="utf-8")) if os.path.exists(INVENTIONS_PATH) else []
    money_stories = json.load(open(MONEY_PATH, encoding="utf-8")) if os.path.exists(MONEY_PATH) else []

    last_index = -1
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            last_index = json.load(f).get("last_index", -1)

    next_index = last_index + 1
    slot = next_index % 6
    cycle_pos = next_index // 6

    if slot in (0, 1) and inventions:
        i_idx = (cycle_pos * 2 + slot) % len(inventions)
        item = inventions[i_idx]
        output = f"INVENTION:{item['invention']}:{item['inventor']}"
    elif slot in (2, 3) and money_stories:
        m_idx = (cycle_pos * 2 + (slot - 2)) % len(money_stories)
        output = f"MONEY:{money_stories[m_idx]}"
    elif slot == 4:
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
