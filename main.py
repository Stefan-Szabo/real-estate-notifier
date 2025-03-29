import requests
import json
import os
import time
from notifier.telegram import send_telegram_message

PENDING_FILE = "data/pending.json"
SEEN_FILE = "data/seen.json"
APPROVED_FILE = "data/approved.json"
REJECTED_FILE = "data/rejected.json"

def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def fetch_ads():
    base_url = (
        "https://www.storia.ro/_next/data/8heVoJy2VXtJGYiZhoeFY"
        "/ro/rezultate/vanzare/casa/cluj/apahida.json"
        "?distanceRadius=15&limit=72&ownerTypeSingleSelect=ALL"
        "&priceMax=175000&areaMin=100&terrainAreaMin=350&buildYearMin=2010"
        "&roomsNumber=%5BTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D"
        "&buildingType=%5BDETACHED%5D&by=PRICE&direction=ASC"
        "&viewType=listing&searchingCriteria=vanzare"
        "&searchingCriteria=casa&searchingCriteria=cluj&searchingCriteria=apahida"
    )

    all_items = []
    for page in range(1, 5):  # paginile 1 până la 4
        url = base_url + f"&page={page}" if page > 1 else base_url
        print(f"📦 Fetching page {page}...")
        try:
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            res.raise_for_status()
            data = res.json()
            items = data["pageProps"]["data"]["searchAds"]["items"]
            if not items:
                print(f"📭 Pagina {page} nu are anunțuri.")
                break
            all_items.extend(items)
        except Exception as e:
            print(f"❌ Eroare la pagina {page}: {e}")
            break

    print(f"✅ Total anunțuri preluate: {len(all_items)}")
    return all_items


def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

def main():
    seen = load_json(SEEN_FILE)
    approved = load_json(APPROVED_FILE)
    rejected = load_json(REJECTED_FILE)
    pending = load_json(PENDING_FILE)

    seen_ids = {ad["id"] for ad in seen}
    approved_ids = {ad["id"] for ad in approved}
    rejected_ids = {ad["id"] for ad in rejected}
    pending_ids = {ad["id"] for ad in pending}

    exclude_ids = seen_ids | approved_ids | rejected_ids | pending_ids

    all_ads = fetch_ads()
    new_ads = [ad for ad in all_ads if ad["id"] not in exclude_ids]

    if not new_ads:
        print("Niciun anunț nou.")
        return

    added_ads = []

    for ad in new_ads:
        item = {
            "id": ad["id"],
            "slug": ad["slug"],
            "title": ad["title"],
            "price": ad.get("totalPrice", {}).get("value", "N/A"),
            "location": ad.get("location", {}).get("address", {}).get("city", {}).get("name", "N/A"),
            "link": f"https://www.storia.ro/ro/oferta/{ad['slug']}",
            "rooms": ad.get("roomsNumber", "N/A"),
            "area": ad.get("areaInSquareMeters", "N/A"),
            "terrain": ad.get("terrainAreaInSquareMeters", "N/A")
        }
        pending.append(item)
        seen.append({"id": ad["id"]})
        added_ads.append(item)

    save_json(PENDING_FILE, pending)
    save_json(SEEN_FILE, seen)

    # Trimite anunțurile pe Telegram grupate câte 15
    # Debug: arată exact ce va fi trimis, grupat corect
    for group in chunk_list(added_ads, 15):
        print("📤 Urmează să trimită pe Telegram următorul grup de anunțuri:\n")
        for ad in group:
            camere = ad.get("rooms", "N/A")
            suprafata = ad.get("area", "N/A")
            teren = ad.get("terrain", "N/A")
            price = ad.get("price", "N/A")
            link = ad["link"]
            print(f"🏠 camere {camere} - {price} EUR, casa {suprafata}, teren {teren}\n{link}\n")


    # Trimite anunțurile pe Telegram grupate câte 15
    for group in chunk_list(added_ads, 15):
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
        time.sleep(0.5)  # opțional anti-spam

    # Trimite link-ul către interfață
    send_telegram_message("🔎 Vezi toate anunțurile în așteptare:\nhttps://stefan-szabo.github.io/real-estate-notifier/")

    print(f"{len(added_ads)} anunțuri noi adăugate în pending.")

if __name__ == "__main__":
    main()
