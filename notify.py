import json
import os
import time
import requests

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

LAST_BATCH_HOUSES = "data/last_batch.json"
LAST_BATCH_APTS = "data/apartments_last_batch.json"

def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    res = requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "disable_web_page_preview": True
    })
    if not res.ok:
        print("❌ Eroare la trimiterea notificării:", res.text)
    else:
        print("📨 Trimis:\n", msg)

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

def notify_for_ads(ads, tip="🏠"):
    for group in chunk_list(ads, 15):
        lines = []
        for ad in group:
            camere = ad.get("rooms", "N/A")
            suprafata = ad.get("area", "N/A")
            teren = ad.get("terrain", "N/A")
            price = ad.get("price", "N/A")
            link = ad["link"]
            msg = f"{tip} camere {camere} - {price} EUR, suprafată {suprafata}, teren {teren}\n{link}"
            lines.append(msg)
        send_telegram_message("\n\n".join(lines))
        time.sleep(0.5)

def main():
    new_houses = load_json(LAST_BATCH_HOUSES)
    new_apts = load_json(LAST_BATCH_APTS)

    if not new_houses and not new_apts:
        print("Nimic nou de notificat.")
        return

    if new_houses:
        print(f"📤 Case noi: {len(new_houses)}")
        notify_for_ads(new_houses, "🏠")

    if new_apts:
        print(f"🏢 Apartamente noi: {len(new_apts)}")
        notify_for_ads(new_apts, "🏢")

    send_telegram_message("🔎 Vezi toate anunțurile în așteptare:\nhttps://stefan-szabo.github.io/real-estate-notifier/")

if __name__ == "__main__":
    main()
