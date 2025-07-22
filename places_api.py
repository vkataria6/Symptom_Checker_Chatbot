#!/usr/bin/env python3
import time
import requests
import json

GOOGLE_API_KEY = "AIzaSyA6At1qOFc4OuUptseLyA1gb6_4VvoxCTU"

def fetch_nearby_medical_centers(lat, lng, radius, pagetoken=None):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": GOOGLE_API_KEY,
        "location": f"{lat},{lng}",
        "radius": radius,
        "keyword": "medical center|hospital|clinic|urgent care"
    }
    if pagetoken:
        params["pagetoken"] = pagetoken

    # Debug: show the full request URL
    req = requests.Request("GET", url, params=params).prepare()
    print("DEBUG: URL →", req.url)

    resp = requests.Session().send(req)
    data = resp.json()
    print(f"→ status={data.get('status')}, results={len(data.get('results', []))}")
    if data.get("status") not in ("OK", "ZERO_RESULTS"):
        raise RuntimeError(f"Places API error: {data.get('status')} / {data.get('error_message')}")
    return data

def build_intents(places_json):
    intents = []
    for place in places_json.get("results", []):
        intents.append({
            "tag": place["name"],
            "location": [
                place["geometry"]["location"]["lat"],
                place["geometry"]["location"]["lng"]
            ],
            "Address": place.get("vicinity", place.get("formatted_address", ""))
        })
    return intents

def collect_all(lat, lng, radius):
    all_intents = []
    data = fetch_nearby_medical_centers(lat, lng, radius)
    all_intents.extend(build_intents(data))

    # Page through up to 3 pages
    while "next_page_token" in data:
        time.sleep(2)  # Must wait before using next_page_token
        data = fetch_nearby_medical_centers(lat, lng, radius, pagetoken=data["next_page_token"])
        all_intents.extend(build_intents(data))

    return all_intents

if __name__ == "__main__":
    # 1) Quick sanity check in Manhattan (25 km radius)
    print("=== Testing NYC fetch ===")
    nyc_places = collect_all(40.740, -73.975, 25000)
    print(f"NYC: collected {len(nyc_places)} places\n")

    # 2) Tile the tri-state area
    grid_centers = [
        (40.740, -73.975),  # Manhattan
        (40.650, -74.230),  # Staten Island / Jersey City
        (40.850, -73.900),  # The Bronx / Westchester edge
        (40.500, -74.440),  # Southern NJ
        (40.000, -75.150),  # Philadelphia
    ]
    print("=== Sweeping Tri-State grid ===")
    all_intents = []
    for lat, lng in grid_centers:
        block = collect_all(lat, lng, 20000)
        print(f"  → center {lat},{lng} → {len(block)} places")
        all_intents.extend(block)

    # Deduplicate by name+address
    unique = { (i["tag"], i["Address"]) : i for i in all_intents }
    final_list = list(unique.values())

    out_file = "tri_state_medical_centers.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"intents": final_list}, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(final_list)} unique entries to {out_file}")
