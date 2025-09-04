import os
import subprocess
import tempfile
import json
import re

def run_fish_recognition(image_bytes, filename="fish.jpg"):
    """
    Run recognize_fish.py on the given image and return a list of species dicts.
    Example return:
    [
        {"name": "Bass", "accuracy": 0.95},
        {"name": "Trout", "accuracy": 0.87}
    ]
    """
    try:
        # Save image temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name

        # Get API keys
        api_key = os.getenv("FISHIAL_API_KEY")
        secret_key = os.getenv("FISHIAL_SECRET_KEY")
        if not api_key or not secret_key:
            print("[ERROR] Missing FISHIAL_API_KEY or FISHIAL_SECRET_KEY in environment")
            return []

        # Run original recognize_fish.py
        cmd = f"python3 recognize_fish.py -k {api_key} -s {secret_key} {tmp_path}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=90)

        # Cleanup
        os.unlink(tmp_path)

        if result.returncode != 0:
            print("[ERROR] recognize_fish.py failed:", result.stderr)
            return []

        # Extract JSON block from stdout
        match = re.search(r'({.*"results".*})', result.stdout, re.DOTALL)
        if not match:
            print("[WARN] No JSON results found in recognize_fish.py output")
            return []

        recognition_json = json.loads(match.group(1))
        fish_species = []
        for fish in recognition_json.get("results", []):
            for s in fish.get("species", []):
                fish_species.append({
                    "name": s.get("name", "Unknown"),
                    "accuracy": float(s.get("accuracy", 0))
                })

        return fish_species

    except subprocess.TimeoutExpired:
        print("[ERROR] Fish recognition timed out")
        return []
    except Exception as e:
        print(f"[ERROR] Fish recognition failed: {e}")
        return []


# recognize_fish_runner.py

import sys

# ... keep the rest of the file as I gave you above ...

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python recognize_fish_runner.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    results = run_fish_recognition(image_bytes, image_path)
    print("Fish species results:", results)
