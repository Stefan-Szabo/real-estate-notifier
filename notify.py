import json
import os
import time
import requests

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
PENDING_FILE = "data/pending.json"
SEEN_FILE = "data/seen.json"

def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    res = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "disable_web_page_preview": True})
    if not res.ok:
        print("❌ Eroare la trimiterea notificării:", res.text)

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

def main():
    pending = load_json(PENDING_FILE)

    # Obține timestamp-ul ultimei modificări a seen.json
    seen_mtime = os.path.getmtime(SEEN_FILE)
    seen_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(seen_mtime))

    print(f"🕒 Verific anunțuri noi adăugate după: {seen_timestamp}")

    # Filtrăm anunțurile adăugate recent
    new_ads = []
    for ad in pending:
        ad_mtime = os.path.getmtime(PENDING_FILE)
        if ad_mtime >= seen_mtime:
            new_ads.append(ad)

    if not new_ads:
        print("Nimic nou de notificat.")
        return

    print(f"📤 Trimit notificări pentru {len(new_ads)} anunțuri...")

    for group in chunk_list(new_ads, 15):
        lines = []
        for ad in group:
            camere = ad.get("rooms", "N/A")
            suprafata = ad.get("area", "N/A")
            teren = ad.get("terrain", "N/A")
            price = ad.get("price", "N/A")
            link = ad["link"]
            lines.append(f"🏠 camere {camere} - {price} EUR, casa {suprafata}, teren {teren}\n{link}")
        msg = "\n\n".join(lines)
        send_telegram_message(msg)
        time.sleep(0.5)

    send_telegram_message("🔎 Vezi toate anunțurile în așteptare:\nhttps://stefan-szabo.github.io/real-estate-notifier/")

if __name__ == "__main__":
    main()
