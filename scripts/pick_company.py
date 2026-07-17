"""
Picks today's content. Weighted based on REAL performance data: invention-
history format got 220 views vs 0-5 for other formats, so it now gets 2/3
of rotation slots instead of an even 1/3 split.
"""
import json
import os
import sys

COMPANIES_PATH = "companies.json"
INVENTIONS_PATH = "inventions.json"
STATE_PATH = "company_state.json"


def main():
    with open(COMPANIES_PATH, "r", encoding="utf-8") as f:
        companies = json.load(f)
    inventions = []
    if os.path.exists(INVENTIONS_PATH):
        with open(INVENTIONS_PATH, "r", encoding="utf-8") as f:
            inventions = json.load(f)

    if not companies:
        print("FATAL: companies.json is empty.", file=sys.stderr)
        sys.exit(1)

    last_index = -1
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            state = json.load(f)
            last_index = state.get("last_index", -1)

    next_index = last_index + 1
    mod3 = next_index % 3

    if mod3 == 0 and inventions:
        # 1/3: single-company POV (kept for variety/comparison baseline)
        c_idx = (next_index // 3) % len(companies)
        output = companies[c_idx]
    elif inventions:
        # 2/3: invention-history -- proven winner (220 views vs 0-5 elsewhere)
        i_idx = (next_index // 3 * 2 + (mod3 - 1)) % len(inventions)
        item = inventions[i_idx]
        output = f"INVENTION:{item['invention']}:{item['inventor']}"
    else:
        c_idx = (next_index // 3) % len(companies)
        output = companies[c_idx]

    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump({"last_index": next_index}, f)

    print(output)


if __name__ == "__main__":
    main()
