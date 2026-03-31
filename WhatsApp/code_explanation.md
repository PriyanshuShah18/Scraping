# WhatsApp Contact Checker: Code Documentation

This document explains the functionality, libraries, and logic behind the `fastest.py` script. This script automates the process of verifying if a list of phone numbers from an Excel file is registered on WhatsApp using WhatsApp Web.

---

## 1. Libraries Used & Why

| Library | Purpose |
| :--- | :--- |
| **`openpyxl`** | The "Excel engine." It allows Python to open `.xlsx` files, read cell values, and save changes back to the file. |
| **`time`** | Used for creating pauses (delays). In web automation, you must wait for pages to load or elements to appear so the script doesn't move faster than the browser. |
| **`sys`** | Provides access to system-specific parameters and functions. Here, it's used to cleanly exit the script (`sys.exit`) if an error occurs. |
| **`re`** (Regular Expressions) | A powerful tool for text pattern matching. It's used here to "clean" phone numbers by removing spaces, dashes, and brackets. |
| **`os`** | Used for interacting with the operating system. It checks if the Excel file exists and manages the local `chrome_profile` folder. |
| **`selenium`** | The core library for browser automation. It launches Chrome, navigates to URLs, and "looks" at the webpage to find information. |
| **`webdriver_manager`** | Automatically downloads the correct version of the Chrome Driver (the bridge between Python and Chrome) so you don't have to manage it manually. |

---

## 2. Core Components (Functions)

### `clean_number(raw)`
*   **Goal**: Converts messy data (like `+1 (555) 000-1111` or `919512.0`) into a standard format (like `15550001111`).
*   **Logic**: 
    1. Converts the input to a string.
    2. Uses `re.sub` to remove non-digit characters (except a leading `+`).
    3. Handles Excel "floats" (e.g., numbers that end in `.0`) ensure they remain integers.

### `find_contact_column(sheet)`
*   **Goal**: If the user doesn't specify which column has phone numbers, this function "guesses" by looking at the first row (headers).
*   **Logic**: Scans headers for keywords like "phone", "contact", or "whatsapp".

### `check_whatsapp_number(driver, number)`
*   **Goal**: The heart of the script. It tells the browser to check a specific number.
*   **Logic**:
    1. Navigates to `https://web.whatsapp.com/send?phone=...`
    2. Searches the page for specific error messages (e.g., "Phone number... is invalid").
    3. If an error is found, it returns `False`.
    4. if the chat window (`id="main"`) loads, it returns `True`.

---

## 3. Line-by-Line Breakdown

### **Setup (Lines 1-12)**
Imports the tools discussed above.

### **Cleaning Process (Lines 15-37)**
Normalizes the data. It ensures that regardless of how the number was typed in Excel, it becomes a clean string of digits that WhatsApp understands.

### **The "Main" Logic (Lines 109-268)**

#### **Configuration (Lines 111-114)**
You define your file name and the column name here.

#### **Loading Excel (Lines 125-150)**
*   `openpyxl.load_workbook` opens the file.
*   The script then looks for your specified column (`P.Contact`).

#### **Preparing the Result Column (Lines 152-174)**
*   It checks if a "Whatsapp Status" column already exists.
*   If not, it finds the first empty column at the end of the sheet and adds the header.

#### **Browser Initialization (Lines 190-205)**
*   **ChromeOptions**: Sets up the browser.
*   `detach=True`: Keeps Chrome open even if the script finishes.
*   `user-data-dir`: Creates a folder named `chrome_profile`. This saves your WhatsApp login so you don't have to scan the QR code every single time.

#### **The Login Wait (Lines 207-215)**
*   `WebDriverWait(driver, 120)`: Gives you 2 minutes to scan the QR code before it gives up.

#### **The Verification Loop (Lines 228-251)**
*   For every number found in the Excel:
    1. It calls `check_whatsapp_number`.
    2. It updates the Excel cell with "Present" or "Not Found".
    3. **Live Save (Lines 242-249)**: It saves the file *after every single check*. This ensures that if the script stops unexpectedly, you don't lose your progress.

#### **Cleanup (Lines 254-259)**
*   Performs a final save and closes the browser.

---

## 4. How to Understand the Workflow

1.  **Input**: The script reads your Excel.
2.  **Browser**: It opens a "controlled" version of Chrome.
3.  **Interaction**: It tries to "chat" with each number. WhatsApp Web will either show a chat box (Number exists) or an error popup (Number doesn't exist).
4.  **Observation**: Selenium "sees" these UI elements and reports back to Python.
5.  **Output**: Python writes the result back to your Excel file instantly.
