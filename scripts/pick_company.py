"""
Picks today's content: rotates through THREE formats to A/B test which
performs best -- single-company POV, vs-comparison, and invention-history.
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

    if mod3 == 0:
        # Single-company POV format
        c_idx = (next_index // 3) % len(companies)
        output = companies[c_idx]
    elif mod3 == 1:
        # Vs-comparison format
        c_idx = (next_index // 3) % len(companies)
        pair_idx = (c_idx + 1) % len(companies)
        output = f"{companies[c_idx]}|{companies[pair_idx]}"
    else:
        # Invention-history format
        if inventions:
            i_idx = (next_index // 3) % len(inventions)
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
