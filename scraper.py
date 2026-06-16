import requests
import json
import time
from datetime import datetime

BASE_URL = "https://www.theonsitemanager.com.au/api/v1"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}

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
