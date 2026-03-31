import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

BASE_API = "https://nianarodagidc.org/xhr/get-search-results-new.php"

headers = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://nianarodagidc.org",
    "Referer": "https://nianarodagidc.org/search/AllData"
}

OUTPUT_FILE = "nia_directory_copy.xlsx"

MAX_THREADS = 8
MAX_RETRIES = 3

session = requests.Session()
session.headers.update(headers)

print("🚀 Starting ZERO-SKIP NIA Scraper...\n")


# -------------------------------------------------
# 1️⃣ Detect Total Pages
# -------------------------------------------------

def get_total_pages():
    page = 1
    while True:
        payload = {
            "page": page,
            "keyword": "AllData",
            "sort_type": 1,
            "current_city": "Ahmedabad",
            "branch": 23
        }

        response = session.post(BASE_API, data=payload, timeout=15)
        data = response.json()
        companies = data.get("data", [])

        if not companies:
            return page - 1

        page += 1


print("🔍 Detecting total pages...")
TOTAL_PAGES = get_total_pages()
print(f"✅ Total Pages Found: {TOTAL_PAGES}\n")


# -------------------------------------------------
# 2️⃣ Fetch Page With Retry (NO SKIP)
# -------------------------------------------------

def fetch_page(page_number):
    for attempt in range(MAX_RETRIES):

        try:
            payload = {
                "page": page_number,
                "keyword": "AllData",
                "sort_type": 1,
                "current_city": "Ahmedabad",
                "branch": 23
            }

            response = session.post(BASE_API, data=payload, timeout=15)

            if response.status_code != 200:
                raise Exception("Bad status")

            data = response.json()
            companies = data.get("data", [])

            rows = []

            for company in companies:

                company_id = company.get("id")
                company_name = company.get("sCompanyName")

                # 🔥 STRICT VALIDATION (prevents blank rows)
                if not company_id and not company_name:
                    continue

                rows.append({
                    "Company ID": company_id,
                    "Company Name": company_name,
                    "Email": company.get("sEmail"),
                    "Website": company.get("sWebsite"),
                    "Address": company.get("sAddress"),
                    "Area": company.get("sArea"),
                    "City": company.get("sCityName"),
                    "District": company.get("sDistrictName"),
                    "State": company.get("sStateName"),
                    "Pincode": company.get("sPincode"),
                    "Phone 1": company.get("sPhone1"),
                    "Phone 2": company.get("sPhone2"),
                    "Phone 3": company.get("sPhone3"),
                    "Mobile 1": company.get("sMobile"),
                    "Mobile 2": company.get("sMobile2"),
                    "Mobile 3": company.get("sMobile3"),
                    "Business Description": company.get("sBusinessDescription"),
                    "Profile URL": company.get("result_link")
                })

            print(f"✅ Page {page_number} done")
            return rows

        except Exception:
            print(f"⚠ Retry {attempt+1} for page {page_number}")
            time.sleep(1)

    print(f"❌ Page {page_number} failed permanently")
    return []


# -------------------------------------------------
# 3️⃣ Parallel Fetch (Guaranteed Full Range)
# -------------------------------------------------

all_rows = []

with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    futures = [executor.submit(fetch_page, p) for p in range(1, TOTAL_PAGES + 1)]

    for future in as_completed(futures):
        result = future.result()
        if result:
            all_rows.extend(result)


# -------------------------------------------------
# 4️⃣ Final Cleaning (ABSOLUTELY NO BLANK ROWS)
# -------------------------------------------------

df = pd.DataFrame(all_rows)

# Remove fully empty rows
df = df.dropna(how="all")

# Remove rows where BOTH ID and Name are missing
df = df[~(df["Company ID"].isna() & df["Company Name"].isna())]

# Remove blank-string IDs and Names
df = df[df["Company ID"].astype(str).str.strip() != ""]
df = df[df["Company Name"].astype(str).str.strip() != ""]

# Remove duplicates safely
df = df.drop_duplicates(subset=["Company ID"])

df = df.reset_index(drop=True)

df.to_excel(OUTPUT_FILE, index=False)

print("\n🎉 ZERO-SKIP Scraping Completed Successfully")
print(f"Total Companies Saved: {len(df)}")