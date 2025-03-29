import requests
import json
import os

PENDING_FILE = "data/pending.json"
SEEN_FILE = "data/seen.json"

# Endpoint-ul tău Storia (poți adapta după filtrul tău)
URL = "https://www.storia.ro/_next/data/8heVoJy2VXtJGYiZhoeFY/ro/rezultate/vanzare/casa/cluj/apahida.json?distanceRadius=15&limit=36&ownerTypeSingleSelect=ALL&priceMax=175000&areaMin=100&terrainAreaMin=350&buildYearMin=2010&roomsNumber=%5BTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D&buildingType=%5BDETACHED%5D&by=PRICE&direction=ASC&viewType=listing"

def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def fetch_ads():
    res = requests.get(URL)
    data = res.json()
    return data["pageProps"]["data"]["searchAds"]["items"]

def main():
    seen = load_json(SEEN_FILE)
    seen_ids = {ad["id"] for ad in seen}
    pending = load_json(PENDING_FILE)

    all_ads = fetch_ads()
    new_ads = [ad for ad in all_ads if ad["id"] not in seen_ids]

    if not new_ads:
        print("Niciun anunț nou.")
        return

    for ad in new_ads:
        item = {
            "id": ad["id"],
            "slug": ad["slug"],
            "title": ad["title"],
            "price": ad.get("totalPrice", {}).get("value", "N/A"),
            "location": ad.get("location", {}).get("address", {}).get("city", {}).get("name", "N/A"),
            "link": f"https://www.storia.ro/ro/oferta/{ad['slug']}"
        }
        pending.append(item)
        seen.append({"id": ad["id"]})

    save_json(PENDING_FILE, pending)
    save_json(SEEN_FILE, seen)
    print(f"{len(new_ads)} anunțuri noi adăugate în pending.")

if __name__ == "__main__":
    main()
