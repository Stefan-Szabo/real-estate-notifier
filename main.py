import requests
import json
import os

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
    for page in range(1, 5):
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

    print(f"✅ {len(added_ads)} anunțuri noi adăugate în pending. Notificările vor fi trimise de workflow-ul `notify.yml`.")

if __name__ == "__main__":
    main()
