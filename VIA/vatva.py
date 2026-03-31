import requests
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_API = "https://www.vatvaassociation.org/xhr/get-clients.php"

headers = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest"
}

OUTPUT_FILE = "vatva_directory_copy.xlsx"

MAX_THREADS = 8          # 6–10 is safe range
PAGE_BATCH_SIZE = 20     # Number of pages fetched per batch

print("🚀 Starting MAXIMUM SPEED scrape...\n")

session = requests.Session()
session.headers.update(headers)


def fetch_page(page_number):
    try:
        payload = {"page": page_number, "keyword": ""}
        response = session.post(BASE_API, data=payload, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()
        companies = data.get("data", [])

        if not companies:
            return []

        rows = []

        for company in companies:
            rows.append({
                "Company Name": company.get("sCompanyName"),
                "Category": company.get("sCategoryStr"),
                "Sub Category": company.get("sSubCategoryStr"),
                "Product": company.get("sProductStr"),
                "Business Category": company.get("sBusinessCategory"),
                "Business Description": company.get("sBusinessDescription"),
                "Address": company.get("sAddress"),
                "Area": company.get("sArea"),
                "City": company.get("sCityName"),
                "District": company.get("sDistrictName"),
                "State": company.get("sStateName"),
                "Pincode": company.get("sPincode"),
                "Phone 1": company.get("sPhone1"),
                "Phone 2": company.get("sPhone2"),
                "Mobile 1": company.get("sMobile"),
                "Mobile 2": company.get("sMobile2"),
                "Email 1": company.get("sEmail"),
                "Email 2": company.get("sEmail2"),
                "Website 1": company.get("sWebsite"),
                "Website 2": company.get("sWebsite2"),
                "Contact Person 1": company.get("sPerson1"),
                "Contact Person 2": company.get("sPerson2"),
                "Raw Materials": company.get("sRawMaterial"),
                "Business Type": company.get("sBusinessType"),
                "Membership No": company.get("sMembeshipNo"),
            })

        print(f"✅ Page {page_number} done")
        return rows

    except Exception:
        return None


all_rows = []
current_page = 1
stop_scraping = False

while not stop_scraping:

    page_range = range(current_page, current_page + PAGE_BATCH_SIZE)

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {executor.submit(fetch_page, p): p for p in page_range}

        empty_pages = 0

        for future in as_completed(futures):
            result = future.result()

            if result is None:
                continue

            if result == []:
                empty_pages += 1
            else:
                all_rows.extend(result)

    # If all pages in this batch were empty → stop
    if empty_pages == PAGE_BATCH_SIZE:
        stop_scraping = True
    else:
        current_page += PAGE_BATCH_SIZE

print("\n💾 Writing to Excel (single write, fastest)...")

df = pd.DataFrame(all_rows)
df.to_excel(OUTPUT_FILE, index=False)

print("\n🎉 MAXIMUM SPEED Scraping Completed Successfully")
print(f"Total Companies Scraped: {len(all_rows)}")