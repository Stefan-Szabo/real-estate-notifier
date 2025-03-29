import json
import os
import sys

PENDING_FILE = "data/pending.json"
REJECTED_FILE = "data/rejected.json"

def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    event = os.getenv("EVENT_PAYLOAD")
    if not event:
        print("⚠️ ENV EVENT_PAYLOAD not set.")
        sys.exit(1)

    payload = json.loads(event)
    rejected_ids = set(payload.get("ids", []))

    pending = load_json(PENDING_FILE)
    rejected = load_json(REJECTED_FILE)

    new_pending = []
    for item in pending:
        if str(item["id"]) in rejected_ids:
            rejected.append(item)
        else:
            new_pending.append(item)

    save_json(PENDING_FILE, new_pending)
    save_json(REJECTED_FILE, rejected)
    print(f"❌ Respins {len(rejected_ids)} anunț(uri).")

if __name__ == "__main__":
    main()
