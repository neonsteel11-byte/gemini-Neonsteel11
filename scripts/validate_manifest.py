#!/usr/bin/env python3
import json, sys, os

def validate(manifest_path):
    if not os.path.exists(manifest_path):
        raise SystemExit("Error: manifest.json not found.")
    with open(manifest_path, "r") as f:
        m = json.load(f)
    
    # Ensure mandatory structure exists
    if "status" not in m or "metadata" not in m:
        raise SystemExit("Error: Manifest missing root keys.")
    if m["status"] == "published":
        raise SystemExit("System: Video already published. Skipping.")
    print("-> Manifest validation passed.")

if __name__ == "__main__":
    validate("output/manifest.json")