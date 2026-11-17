"""
This file is a shared setting file and helper functions file which will be used by every script in this project.
Other scripts will load this file.

"""

import os
import csv 
import hashlib
from urllib.parse import urlparse
from bs4 import BeautifulSoup

#Setting 
# True for testing it locally
# False for running it against a rel website and real internet Archive

LOCAL_TEST = False

# Where the local tests website is served from.

LOCAL_SITE_URL = "http://localhost:8000"

# This will be for real websites we study in the real run
# Choosing small, lon-lived, non-commercial sites
REAL_DOMAINS = ["lua.org", "openssh.com", "gnuplot.info"]

# Credentials that will be sent with every web request we send so a site can see who is running the test and asks us to step in they need us to 

CONTACT_EMAIL = "testuser@exeter.ac.uk"
USER_AGENT = f"OpharhedPageStudy/1.0 (student coursework; contact: {CONTACT_EMAIL})"

# The year this was treated
CURRENT_YEAR = 2026

# Pages last seen in the archive BEFORE this data count as "past" pages
# Pages last seen in the archive AFTER this date count as "current" pages
# The data is written as YYYYMMDD, just as the format the Internet Archive uses 

CUTOFF_DATE = "20250101"

# Seconds to wait between requests. Short for our own local site.
# Longer for real websites to avoid overloading them.
if LOCAL_TEST:
    POLITE_DELAY_SECONDS = 0.2
else:
    POLITE_DELAY_SECONDS = 10
        

# The test run and the real run keep their results in separate folders, so one never overwrites the other.
if LOCAL_TEST:
    DATA_FOLDER = "data"
    REPORTS_FOLDER = "reports"
else:
    DATA_FOLDER = "data_real"
    REPORTS_FOLDER = "reports_real"
    
# Folders where the data is stored 

HISTORY_FOLDER = os.path.join(DATA_FOLDER, "history") # archive history lists
PAGES_FOLDER = os.path.join(DATA_FOLDER, "pages")   # pages as they look today
ARCHIVE_FOLDER = os.path.join(DATA_FOLDER, "archived") # pages as the archive saw them




# This is going to create each folder if it does not exist yet.
for folder in [DATA_FOLDER, HISTORY_FOLDER, PAGES_FOLDER, ARCHIVE_FOLDER, REPORTS_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# File endings that are not web pages
# This is the list from Appendix B of the paper

NON_PAGE_EXTENSIONS = (
    # Pictures
    ".bmp", ".dib", ".gif", ".heic", ".heif", ".ico", ".j2k", ".jfi", ".jfif",
    ".jif", ".jp2", ".jpe", ".jpeg", ".jpf", ".jpg", ".jpm", ".jpx", ".mj2",
    ".png", ".psd", ".svg", ".svgz", ".tif", ".tiff", ".webp",
    # Design files
    ".ai", ".eps", ".ind", ".indd", ".indt",
    # Video
    ".3g2", ".3gp", ".3gp2", ".3gpp", ".3gpp2", ".avi", ".f4a", ".f4b", ".f4v",
    ".flv", ".m4v", ".mov", ".mp4", ".mpe", ".mpeg", ".mpg", ".mpv", ".ogv",
    ".qt", ".swf", ".webm", ".wmv",
    #Audio
    ".m4a", ".m4b", ".m4p",".m4r",".mp2",".mp3",".oga",".ogg",".ogx",".wma",
    # Fonts
    ".eot",".ttf",".woff",
    # Code, styles and documents
    ".js", ".css",".pdf"
)

# Helpers for web addresses and saved pages 

def get_domain(url):
    """This returns the website part of an address"""
    return urlparse(url).netloc

def short_id(url):
    """This is going to turn a web address into a short, unique code to use as a file name"""
    fingerprint = hashlib.sha1(url.encode("utf-8")).hexdigest()
    return fingerprint[:16]

def live_page_path(url):
    """Where a page is saved, as it looks like today or currently"""
    return os.path.join(PAGES_FOLDER, short_id(url) + ".html")

def archived_page_path(url):
    """Where pages that are archive saw it in the past are saved"""
    return os.path.join(ARCHIVE_FOLDER, short_id(url) + ".html")

def read_text_file(path):
    """This is going to read a text files and return its contents. If the files does not exist, return an empty string"""
    if not os.path.exists(path):
        return ""
    with open (path, encoding="utf-8", errors="replace") as text_file:
        return text_file.read()
    
def write_text_file(path, text):
    """This is going to save some text into a file"""
    with open(path, "w", encoding="utf-8") as text_file:
        text_file.write(text)
        
# Helper function for CSV files

def read_rows(csv_path):
    """This is going to read a CSV file and return a list of rows"""
    
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader (csv_file)
        for row in reader:
            rows.append(row)
        return rows
    
def write_rows (csv_path, rows, column_names):
    """Save a list of rows (dictionaries) into a CSV file"""
    with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=column_names)
        writer.writeheader()
        writer.writerows(rows)
        
# The funnel log (This is our version of the paper's Table 1)

FUNNEL_PATH = os.path.join(DATA_FOLDER, "funnel.csv")

def start_new_funnel():
    """This is going to write the funnel log so a fresh starts with a clean record."""
    if os.path.exists(FUNNEL_PATH):
        os.remove(FUNNEL_PATH)
        
def log_funnel_step(step_name, page_count):
    """This records how many pages are left after a step, and prints it"""
    file_is_new = not os.path.exists(FUNNEL_PATH)
    with open(FUNNEL_PATH, "a", newline="", encoding="utf-8") as funnel_file:
        writer = csv.writer(funnel_file)
        if file_is_new:
            writer.writerow(["step", "count"])
        writer.writerow([step_name, page_count])
    print(step_name + ": " + str(page_count) + " pages")    
    
def get_visible_text(html):
    """Remove all HTML tags, scripts and styles, and return only the words a visitor would actually see on the page"""
    
    soup = BeautifulSoup(html, "html.parser")
    # Scripts and styles are code, not words for people, so they will be deleted
    for tag in soup.find_all(["script", "style"]):
        tag.decompose()
    return soup.get_text(" ", strip=True)