import json
import sys

PENDING_FILE = "data/pending.json"
APPROVED_FILE = "data/approved.json"

ids = sys.argv[1].strip("[]").split(",")
ids = [int(id.strip().replace("'", "").replace('"', "")) for id in ids]

def load(file):
    with open(file, "r") as f:
        return json.load(f)

def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

pending = load(PENDING_FILE)
approved = load(APPROVED_FILE)

approved_now = [ad for ad in pending if ad["id"] in ids]
remaining_pending = [ad for ad in pending if ad["id"] not in ids]

save(APPROVED_FILE, approved + approved_now)
save(PENDING_FILE, remaining_pending)

print(f"Aprobat {len(approved_now)} anunțuri.")
