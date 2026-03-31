import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://www.vatvaassociation.org/directory"
SAVE_FOLDER = "vatva_ads_images_copy"
MAX_THREADS = 8

headers = {
    "User-Agent": "Mozilla/5.0"
}

# Create folder
os.makedirs(SAVE_FOLDER, exist_ok=True)

print("🚀 Fetching directory page...")

response = requests.get(BASE_URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

print("🔎 Extracting image URLs...")

image_urls = set()

for img in soup.find_all("img"):
    src = img.get("src")
    if src:
        full_url = urljoin(BASE_URL, src)

        # Filter only ads images (important)
        if "premium" in full_url or "popup" in full_url or "company-logo" in full_url:
            image_urls.add(full_url)

print(f"📸 Total Ad Images Found: {len(image_urls)}")


# -----------------------------------------
# Download Function
# -----------------------------------------
def download_image(url):
    try:
        filename = os.path.join(SAVE_FOLDER, url.split("/")[-1].split("?")[0])

        r = requests.get(url, headers=headers, timeout=10)
        with open(filename, "wb") as f:
            f.write(r.content)

        print(f"✅ Downloaded: {filename}")

    except Exception as e:
        print(f"❌ Failed: {url}")


# -----------------------------------------
# Multithreaded Download
# -----------------------------------------

print("⬇️ Downloading images in parallel...")

with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    executor.map(download_image, image_urls)

print("\n🎉 All Ad Images Downloaded Successfully")