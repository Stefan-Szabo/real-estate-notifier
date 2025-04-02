import json
import os
import sys

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def process_rejection(ids, pending_file, rejected_file):
    pending = load_json(pending_file)
    rejected = load_json(rejected_file)

    new_pending = []
    for item in pending:
        if str(item["id"]) in ids:
            rejected.append(item)
        else:
            new_pending.append(item)

    save_json(pending_file, new_pending)
    save_json(rejected_file, rejected)

event = os.getenv("EVENT_PAYLOAD")
if not event:
    print("⚠️ ENV EVENT_PAYLOAD not set.")
    sys.exit(1)

payload = json.loads(event)
rejected_ids = set(map(str, payload.get("ids", [])))

# Case
process_rejection(rejected_ids, "data/pending.json", "data/rejected.json")

# Apartamente
process_rejection(rejected_ids, "data/apartments_pending.json", "data/apartments_rejected.json")

print(f"❌ Respins {len(rejected_ids)} anunț(uri).")
