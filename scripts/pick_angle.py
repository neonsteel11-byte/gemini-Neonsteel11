"""
Picks the next story angle for today's video, rotating through angles.json
so the POV format doesn't repeat the same angle every run.
"""
import json
import os
import sys

ANGLES_PATH = "angles.json"
STATE_PATH = "angle_state.json"


def main():
    if not os.path.exists(ANGLES_PATH):
        print("FATAL: angles.json not found.", file=sys.stderr)
        sys.exit(1)

    with open(ANGLES_PATH, "r", encoding="utf-8") as f:
        angles = json.load(f)

    last_index = -1
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            state = json.load(f)
            last_index = state.get("last_index", -1)

    next_index = (last_index + 1) % len(angles)
    angle = angles[next_index]

    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump({"last_index": next_index}, f)

    print(angle)


if __name__ == "__main__":
    main()
