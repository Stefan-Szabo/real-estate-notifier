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

def process_approval(ids, pending_file, approved_file):
    pending = load_json(pending_file)
    approved = load_json(approved_file)

    new_pending = []
    for item in pending:
        if str(item["id"]) in ids:
            approved.append(item)
        else:
            new_pending.append(item)

    save_json(pending_file, new_pending)
    save_json(approved_file, approved)

event = os.getenv("EVENT_PAYLOAD")
if not event:
    print("⚠️ ENV EVENT_PAYLOAD not set.")
    sys.exit(1)

payload = json.loads(event)
approved_ids = set(map(str, payload.get("ids", [])))

# Case
process_approval(approved_ids, "data/pending.json", "data/approved.json")

# Apartamente
process_approval(approved_ids, "data/apartments_pending.json", "data/apartments_approved.json")

print(f"✅ Aprobat {len(approved_ids)} anunț(uri).")
