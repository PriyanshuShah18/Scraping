import os
import cv2
import re
import json
import numpy as np
import easyocr
import pandas as pd
import imutils
from datetime import datetime

# ==============================
# CONFIG
# ==============================

IMAGE_FOLDER = "vatva_ads_images_copy"
OUTPUT_EXCEL = "enterprise_output.xlsx"
CORRECTION_FILE = "corrections.json"

# English only (Gujarati removed – not supported)
reader = easyocr.Reader(['en'], gpu=False)

# ==============================
# IMAGE ENHANCEMENT (LIGHTER)
# ==============================

def enhance_image(path):
    img = cv2.imread(path)
    img = imutils.resize(img, width=1200)  # Reduced from 1800 → Faster

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)

    return gray


# ==============================
# A) BOUNDING BOX CLUSTERING
# ==============================

def cluster_by_vertical_position(ocr_results, threshold=120):
    sorted_blocks = sorted(ocr_results, key=lambda x: x[0][0][1])

    clusters = []
    current_cluster = []
    last_y = None

    for bbox, text, conf in sorted_blocks:
        y = bbox[0][1]

        if last_y is None:
            current_cluster.append((bbox, text, conf))
            last_y = y
            continue

        if abs(y - last_y) < threshold:
            current_cluster.append((bbox, text, conf))
        else:
            clusters.append(current_cluster)
            current_cluster = [(bbox, text, conf)]

        last_y = y

    if current_cluster:
        clusters.append(current_cluster)

    return clusters


# ==============================
# B) LINE CLASSIFIER
# ==============================

def classify_line(text):
    t = text.upper()

    if "@" in text:
        return "email"

    if re.search(r'\+?\d[\d\s\-]{9,15}', text):
        return "phone"

    if any(k in t for k in ["GIDC","PHASE","ROAD","ESTATE","AHMEDABAD","GUJARAT","PLOT"]):
        return "address"

    if any(k in t for k in ["ISO","FDA","HALAL","CERTIFIED","CE"]):
        return "certification"

    if any(k in t for k in ["PVT","LTD","INDUSTRIES","ENTERPRISE","ENGINEERS","SYSTEMS","CHEM"]):
        return "company"

    return "product"


# ==============================
# PHONE VALIDATION
# ==============================

def valid_phone(p):
    digits = re.sub(r'\D', '', p)
    if 10 <= len(digits) <= 13:
        if not digits.startswith(("9001","22000","14001","45001")):
            return digits
    return None


# ==============================
# C) STRUCTURED EXTRACTION
# ==============================

def extract_from_cluster(cluster):

    data = {
        "Company Name": "",
        "Phones": "",
        "Emails": "",
        "Website": "",
        "Address": "",
        "Products": "",
        "Certifications": "",
        "Confidence Score": 0
    }

    phones = []
    emails = []
    websites = []
    address = []
    products = []
    certifications = []
    company_candidates = []

    for bbox, text, conf in cluster:

        label = classify_line(text)

        if label == "email":
            emails.append(text)

        elif label == "phone":
            vp = valid_phone(text)
            if vp:
                phones.append(vp)

        elif label == "address":
            address.append(text)

        elif label == "certification":
            certifications.append(text)

        elif label == "company":
            company_candidates.append(text)

        else:
            products.append(text)

    # Better company selection: high confidence + longest
    if company_candidates:
        data["Company Name"] = max(company_candidates, key=len)

    full_text = " ".join(products)

    data["Phones"] = ", ".join(set(phones))
    data["Emails"] = ", ".join(set(emails))
    data["Website"] = ", ".join(set(re.findall(r'(www\.[^\s]+)', full_text)))
    data["Address"] = " | ".join(address[:4])
    data["Certifications"] = " | ".join(certifications)
    data["Products"] = " | ".join(products[:15])

    # Confidence scoring
    score = 0
    if data["Company Name"]: score += 20
    if data["Phones"]: score += 20
    if data["Emails"]: score += 20
    if data["Address"]: score += 20
    if data["Products"]: score += 20

    data["Confidence Score"] = score

    return data


# ==============================
# D) FEEDBACK LOOP
# ==============================

def apply_feedback(data):

    if not os.path.exists(CORRECTION_FILE):
        return data

    with open(CORRECTION_FILE, "r") as f:
        corrections = json.load(f)

    company = data["Company Name"]

    if company in corrections:
        data.update(corrections[company])

    return data



# PROCESS IMAGE (Single OCR Pass)


def process_image(file):

    print(f"Processing: {file}")

    path = os.path.join(IMAGE_FOLDER, file)
    enhanced = enhance_image(path)

    # SINGLE OCR PASS (much faster)
    ocr_results = reader.readtext(enhanced)

    clusters = cluster_by_vertical_position(ocr_results)

    results = []

    for cluster in clusters:
        structured = extract_from_cluster(cluster)
        structured = apply_feedback(structured)

        if structured["Confidence Score"] >= 40:
            structured["Image File"] = file
            structured["Processed At"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            results.append(structured)

    return results


# ==============================
# SEQUENTIAL EXECUTION (FASTER FOR CPU)
# ==============================

all_results = []

files = [f for f in os.listdir(IMAGE_FOLDER)
         if f.lower().endswith((".jpg",".png",".jpeg"))]

for file in files:
    result = process_image(file)
    all_results.extend(result)

df = pd.DataFrame(all_results)
df.to_excel(OUTPUT_EXCEL, index=False)

print("\nEnterprise Extraction Completed Successfully.")