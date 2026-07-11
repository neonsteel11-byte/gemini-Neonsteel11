"""
Picks today's company (or company pair for comparison format), rotating
through companies.json. Alternates: even runs = single company (POV format),
odd runs = two companies (guess-the-difference comparison format) --
this is the actual A/B test between formats.
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

    if next_index % 2 == 1:
        # Odd run -> comparison format: pair this company with the next one
        pair_index = (next_index + 1) % len(companies)
        output = f"{companies[next_index]}|{companies[pair_index]}"
    else:
        # Even run -> single company POV format
        output = companies[next_index]

    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump({"last_index": next_index}, f)

    print(output)


if __name__ == "__main__":
    main()
