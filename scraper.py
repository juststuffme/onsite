import requests
import json
import re
import time
from datetime import datetime

BASE_URL = "https://www.theonsitemanager.com.au/api/v1"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}


def _num(x):
    """Parse a coordinate to float, guarding blanks and 0/placeholder values."""
    try:
        v = float(x)
        return v if abs(v) > 0.01 else None
    except (TypeError, ValueError):
        return None


def _typed_street(d):
    """A street address from the typed fields, only when it's a real street
    (a leading number + name) rather than a bare unit fragment ("Unit 10")."""
    num = str(d.get("streetNumber") or "").strip()
    st = str(d.get("street") or "").strip()
    typed = f"{num} {st}".strip()
    return typed if re.match(r"^\d+[A-Za-z]?\s+\S", typed) else ""


def geocode_addresses(listings):
    """Resolve a real street address from each listing's map pin. The public ad
    hides the street when addressDisplay=no, so the pin (cordLat/cordLong, which
    the ad's OpenFreeMap map renders) is the reliable source. Reverse-geocode via
    OSM Nominatim and keep the result only when it lands in the listing's own
    suburb/postcode, so a stray pin never yields a wrong street. ~1 req/sec."""
    todo = [l for l in listings
            if l.get("lat") and l.get("lng") and not re.match(r"^\s*\d", str(l.get("address") or ""))]
    print(f"Resolving street addresses from the map pin for {len(todo)} listings (~1/sec)...")
    done = 0
    for i, l in enumerate(todo, 1):
        try:
            url = ("https://nominatim.openstreetmap.org/reverse?format=jsonv2"
                   f"&lat={l['lat']}&lon={l['lng']}&zoom=18&addressdetails=1")
            r = requests.get(url, headers={"User-Agent": "Ras360iQ-Onsite/1.0 (internal research tool)"}, timeout=20)
            a = (r.json() or {}).get("address", {})
            road = a.get("road") or a.get("pedestrian") or a.get("footway")
            pc = str(a.get("postcode") or "")
            sub = (a.get("suburb") or a.get("town") or a.get("city") or a.get("village") or "").lower()
            want_sub = str(l.get("suburb") or "").lower()
            want_pc = str(l.get("postcode") or "")
            if road and ((want_pc and pc == want_pc) or (want_sub and sub and (want_sub in sub or sub in want_sub))):
                hn = a.get("house_number")
                l["address"] = ((f"{hn} " if hn else "") + road).strip()
                done += 1
        except Exception:
            pass
        time.sleep(1.1)
        if i % 50 == 0:
            print(f"  {i}/{len(todo)} checked ({done} resolved)")
    print(f"  geocoded {done}/{len(todo)} listings to a street address")
    return done

def fetch_all_ids():
    all_ids = []
    page = 1
    while True:
        url = f"{BASE_URL}/listings.php?class=management%20rights&page={page}&limit=20&proximity=0.15"
        resp = requests.get(url, headers=HEADERS, timeout=30)
        data = resp.json()
        if not data.get("success") or not data.get("data"):
            break
        ids = [item["pageId"] for item in data["data"]]
        all_ids.extend(ids)
        print(f"  Page {page}: {len(ids)} listings (total: {len(all_ids)})")
        pagination = data.get("pagination", {})
        if page >= pagination.get("pages", 1):
            break
        page += 1
        time.sleep(0.3)
    return all_ids

def fetch_listing_detail(listing_id):
    url = f"{BASE_URL}/listing.php?id={listing_id}"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    data = resp.json()
    raw = data.get("data") or data
    if not raw or not raw.get("pageId"):
        return None
    d = raw
    business_price = (d.get("price") or 0) - (d.get("mr_unitValue") or 0)
    takings = d.get("takings") or 0
    multiplier = round(business_price / takings, 2) if takings > 0 and business_price > 0 else None
    return {
        "id": d.get("pageId"),
        "url": f"https://www.theonsitemanager.com.au/listing/{d.get('pageId')}",
        "title": d.get("title"),
        "category": d.get("category"),
        "status": d.get("status"),
        "price": d.get("price"),
        "priceView": d.get("priceView"),
        "netIncome": d.get("takings"),
        "netIncomeBasis": d.get("takingsBasis"),
        "unitValue": d.get("mr_unitValue"),
        "multiplier": multiplier,
        "bedrooms": d.get("bedrooms"),
        "bathrooms": d.get("bathrooms"),
        "carSpaces": d.get("carSpaces"),
        "officeOnTitle": bool(d.get("mr_officeOnTitle")),
        "pets": d.get("pets") or "No",
        "caretakingRemuneration": d.get("mr_remuneration"),
        "agreementTerm": d.get("mr_agreementTerm"),
        "agreementRemaining": d.get("mr_agreementRemaining"),
        "agreementAge": d.get("mr_age"),
        "officeHours": d.get("mr_officeHours"),
        "lettingPool": d.get("mr_unitsLettingPool"),
        "ownerOccupiers": d.get("mr_unitsOwnerOccupied"),
        "lockUps": d.get("mr_unitsLockUp"),
        "outsideAgents": d.get("mr_unitsLetOutside"),
        "unitsInComplex": d.get("mr_unitsTotal"),
        "suburb": d.get("suburb"),
        "state": d.get("state"),
        "postcode": d.get("postcode"),
        "address": _typed_street(d),            # real street from the pin filled in a later pass
        "lat": _num(d.get("cordLat")),          # map-pin latitude  (from the ad's map)
        "lng": _num(d.get("cordLong")),         # map-pin longitude
        "agentName": (d.get("listingAgentName") or d.get("salesName") or "").strip(),
        "agentPhone": d.get("listingAgentPhone") or d.get("agentPhone"),
        "agentEmail": d.get("agentEmail"),
        "agencyName": d.get("businessName") or d.get("agencyName"),
        "agencyWebsite": d.get("agencyWebsite") or d.get("website"),
        "dateListed": d.get("entryDate"),
        "lastUpdated": d.get("timestamp")
    }

def main():
    print(f"Starting scrape at {datetime.now().isoformat()}")
    print("Fetching all listing IDs...")
    ids = fetch_all_ids()
    print(f"Found {len(ids)} listings. Fetching details...")
    listings = []
    errors = []
    for i, lid in enumerate(ids):
        try:
            detail = fetch_listing_detail(lid)
            if detail:
                listings.append(detail)
            if (i + 1) % 50 == 0:
                print(f"  Progress: {i+1}/{len(ids)}")
            time.sleep(0.15)
        except Exception as e:
            print(f"  Error on {lid}: {e}")
            errors.append(lid)
    geocode_addresses(listings)
    output = {
        "scraped_at": datetime.now().isoformat(),
        "total": len(listings),
        "listings": listings
    }
    with open("listings.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Done! Saved {len(listings)} listings ({len(errors)} errors)")

if __name__ == "__main__":
    main()
