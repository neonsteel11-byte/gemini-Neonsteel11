"""
Picks the next company for today's videos, rotating through companies.json
so coverage spans big-cap to small-cap without repeats until the full list
has cycled through.
"""
import json
import os
import sys

COMPANIES_PATH = "companies.json"
STATE_PATH = "company_state.json"


def main():
    if not os.path.exists(COMPANIES_PATH):
        print("FATAL: companies.json not found.", file=sys.stderr)
        sys.exit(1)

    with open(COMPANIES_PATH, "r", encoding="utf-8") as f:
        companies = json.load(f)

    if not companies:
        print("FATAL: companies.json is empty.", file=sys.stderr)
        sys.exit(1)

    last_index = -1
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            state = json.load(f)
            last_index = state.get("last_index", -1)

    next_index = (last_index + 1) % len(companies)
    company = companies[next_index]

    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump({"last_index": next_index}, f)

    # Print ONLY the company name -- this is captured by the workflow
    print(company)


if __name__ == "__main__":
    main()
