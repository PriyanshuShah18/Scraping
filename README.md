# Scraping & Automation Suite

This repository contains a suite of Python-based scraping and automation tools. The suite comprises two main components: an industrial directory data extraction engine equipped with OCR capabilities, and an automated WhatsApp contact verification system.

---

## 1. Industrial Directory extraction (`/VIA`)
A multi-threaded data extraction tool targeting the Vatva Industries Association (VIA) and Naroda Industries Association (NIA) directories. This module goes beyond standard HTML scraping by employing Computer Vision and Optical Character Recognition (OCR) to extract valuable contact details hidden within company advertisement images.

**Core Scripts:**
*   **`nia.py` / `vatva.py`**: High-speed, concurrent scraping of company profiles (Names, Phones, Emails, Addresses, Products, Memberships) through paginated APIs. Includes robust data cleaning and deduplication, outputting results directly to Excel.
*   **`image.py`**: A multi-threaded image downloader that efficiently extracts ad/premium association images using `BeautifulSoup`.
*   **`image_extractor.py`**: A locally-run image processing pipeline leveraging `easyocr` and `OpenCV` (CV2). It enhances images, extracts text, clusters bounding boxes based on positioning, and classifies text lines (e.g., Email, Phone, Address, Certification). Organizes the extracted insight into a structured, confidence-scored Excel sheet.

---

## 2. WhatsApp Contact Verifier (`/WhatsApp`)
An automated Selenium-based tool that verifies whether a bulk list of phone numbers (stored in an Excel sheet) is registered on WhatsApp.

**Core Scripts:**
*   **`fastest.py`**: Reads raw phone numbers, sanitizes them via Regular Expressions, and programmatically controls a Chrome browser using `selenium`. It checks each number's validity against WhatsApp Web's UI responses and updates the source Excel file with a "Whatsapp Status" ("Present" or "Not Found") in real-time. It retains the Chrome Session (`chrome_profile`) locally to avoid repetitive QR code logins.
*   **`code_explanation.md`**: Comprehensive, line-by-line documentation explaining the WhatsApp verification logic.

---

## Technologies Used
*   **Web Automation & Scraping**: `requests`, `BeautifulSoup4`, `selenium`, `webdriver_manager`
*   **Data Manipulation**: `pandas`, `openpyxl`
*   **Computer Vision & OCR**: `easyocr`, `cv2` (OpenCV), `imutils`, `numpy`
*   **Performance Optimization**: `concurrent.futures` (`ThreadPoolExecutor`)

---

## Getting Started

1. **Clone the Repository**
   ```bash
   git clone https://github.com/PriyanshuShah18/Scraping.git
   cd Scraping
   ```

2. **Install Required Packages**
   Ensure you have Python installed, then run:
   ```bash
   pip install requests pandas beautifulsoup4 selenium webdriver-manager easyocr opencv-python imutils numpy openpyxl
   ```

3. **Running the Scripts**
   Navigate to the respective folder and run the script of your choice.
   *Example:*
   ```bash
   cd WhatsApp
   python fastest.py
   ```

> **Note:** For security and repository size efficiency, all generated output directories (like `vatva_ads_images/`), Excel sheets (`*.xlsx`, `*.csv`), and browser cache configurations (`chrome_profile/`) are deliberately ignored from version control (`.gitignore`).
