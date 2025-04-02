import requests
import json
import os
import re

# Fișiere pentru case
PENDING_HOUSES = "data/pending.json"
SEEN_HOUSES = "data/seen.json"
APPROVED_HOUSES = "data/approved.json"
REJECTED_HOUSES = "data/rejected.json"
LAST_BATCH_HOUSES = "data/last_batch.json"

# Fișiere pentru apartamente
PENDING_APTS = "data/apartments_pending.json"
SEEN_APTS = "data/apartments_seen.json"
APPROVED_APTS = "data/apartments_approved.json"
REJECTED_APTS = "data/apartments_rejected.json"
LAST_BATCH_APTS = "data/apartments_last_batch.json"

def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_build_id():
    url = "https://www.storia.ro/ro/rezultate/vanzare/casa/cluj/apahida"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    match = re.search(r'"buildId":"(.*?)"', res.text)
    if match:
        return match.group(1)
    raise ValueError("❌ Nu am putut extrage buildId din pagina Storia.")

def fetch_items(build_id, type="house"):
    if type == "house":
        search_path = "vanzare/casa/cluj/apahida"
        filters = (
            "distanceRadius=15"
            "&limit=72"
            "&ownerTypeSingleSelect=ALL"
            "&priceMax=180000"
            "&areaMin=100" 
            "&terrainAreaMin=350"
            "&buildYearMin=2010" 
            "&roomsNumber=%5BTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D"
        )
    elif type == "apartment":
        search_path = "vanzare/apartament/cluj/apahida"
        filters = (
            "distanceRadius=10" 
            "&limit=72" 
            "&ownerTypeSingleSelect=ALL"
            "&priceMax=140000" 
            "&areaMin=60"
            "&roomsNumber=%5BTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D"
        )
        

    base_url = f"https://www.storia.ro/_next/data/{build_id}/ro/rezultate/{search_path}.json?{filters}&by=PRICE&direction=ASC&viewType=listing"
    
    items = []
    for page in range(1, 5):
        url = base_url + f"&page={page}" if page > 1 else base_url
        print(f"📦 Fetching {type} page {page}...")
        try:
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            res.raise_for_status()
            data = res.json()
            page_items = data["pageProps"]["data"]["searchAds"]["items"]
            if not page_items:
                print(f"📭 Pagina {page} ({type}) nu are anunțuri.")
                break
            items.extend(page_items)
        except Exception as e:
            print(f"❌ Eroare la pagina {page} ({type}): {e}")
            break

    print(f"✅ Total anunțuri ({type}) preluate: {len(items)}")
    return items

def process_ads(items, seen, approved, rejected, pending):
    seen_ids = {ad["id"] for ad in seen}
    approved_ids = {ad["id"] for ad in approved}
    rejected_ids = {ad["id"] for ad in rejected}
    pending_ids = {ad["id"] for ad in pending}

    exclude_ids = seen_ids | approved_ids | rejected_ids | pending_ids
    new_ads = [ad for ad in items if ad["id"] not in exclude_ids]

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
    
    return added_ads

def main():
    build_id = get_build_id()

    # --- CASE ---
    houses = fetch_items(build_id, type="house")
    seen = load_json(SEEN_HOUSES)
    approved = load_json(APPROVED_HOUSES)
    rejected = load_json(REJECTED_HOUSES)
    pending = load_json(PENDING_HOUSES)
    new_houses = process_ads(houses, seen, approved, rejected, pending)

    save_json(SEEN_HOUSES, seen)
    save_json(PENDING_HOUSES, pending)
    save_json(LAST_BATCH_HOUSES, new_houses if new_houses else [])

    # --- APARTAMENTE ---
    apartments = fetch_items(build_id, type="apartment")
    seen_a = load_json(SEEN_APTS)
    approved_a = load_json(APPROVED_APTS)
    rejected_a = load_json(REJECTED_APTS)
    pending_a = load_json(PENDING_APTS)
    new_apts = process_ads(apartments, seen_a, approved_a, rejected_a, pending_a)

    save_json(SEEN_APTS, seen_a)
    save_json(PENDING_APTS, pending_a)
    save_json(LAST_BATCH_APTS, new_apts if new_apts else [])

    print(f"✅ Case noi: {len(new_houses)} | Apartamente noi: {len(new_apts)}")

if __name__ == "__main__":
    main()
