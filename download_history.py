"""This script downloads the real archive history of each website in common.REAL_DOMAINS from the internet archive's "CDX"  service (Section 3.1.1)"""


import os 
import time 
import requests
import common

# Settings 

CDX_ADDRESS = "https://web.archive.org/cdx/search/cdx"

PAST_FROM_YEAR = "2010"
PAST_TO_YEAR = "2024"
RECENT_FROM_YEAR = "2025"

# The most rows we accept for one question, to keep our load on the archive small.

MAX_ROWS = 20000

# If the archive is busy, wait this long before trying again (the paper waited a minute)

RETRY_WAIT_SECONDS = 60
MAX_ATTEMPTS = 3

# Helper functions

def ask_archive(domain, from_year, to_year):
    """Ask the CDX service for every page of website seen between two years. This returns the raw answer as text, or "" if the archive could not be reached"""
    
    settings = {
        "url": domain,
        "matchType": "domain",       # include subdomains such as www
        "fl": "timestamp,original", # only the date and the address
        "filter": "statuscode:200",  # only pages that worked when archived
        "collapse": "urlkey",        # one row per address
        "from": from_year,
        "limit": MAX_ROWS,
    }
    if to_year != "":
        settings["to"] = to_year
        
    for attempt in range(MAX_ATTEMPTS):
        try:
            response = requests.get(CDX_ADDRESS, params=settings, 
                                    headers={"User-Agent": common.USER_AGENT}, timeout=180)
            if response.status_code == 200: 
                return response.text 
            print(" archive answered status " + str(response.status_code) + ", waiting to retry")
        except requests.RequestException as error:
            print (" could not reach the archive, waiting to retry")
        time.sleep(RETRY_WAIT_SECONDS)
    return ""

def tidy_address(address):
    """Write every address the same way, so the same page always matches: use https, and remove the default port numbers :80 and :443"""
    address = address.replace("http://", "https://", 1)
    address = address.replace(":80/", "/", 1)
    address = address.replace(":443/", "/", 1)
    address = address.split("?")[0]
    return address
    
def answer_to_rows(answer_text):
    """Turn the archive's answer (one "timestamp address" per line) into rows"""
    rows = []
    for line in answer_text.splitlines():
        parts = line.split(" ")
        if len(parts) == 2:
            rows.append({"timestamp": parts[0], "url": tidy_address(parts[1])})
    return rows        

# Download the history of every website 

if common.LOCAL_TEST:
    print("LOCAL_TEST is True, so there is nothing to download")
    print("Set LOCAL_TEST = False in common.py for the real run")
else:
    for domain in common.REAL_DOMAINS:
        print("Downloading the history of " + domain + ":")
        
        past_rows = answer_to_rows(ask_archive(domain, PAST_FROM_YEAR, PAST_TO_YEAR))
        time.sleep(common.POLITE_DELAY_SECONDS)
        recent_rows = answer_to_rows(ask_archive(domain, RECENT_FROM_YEAR, ""))
        time.sleep(common.POLITE_DELAY_SECONDS)
        
        print(" past pages: " + str(len(past_rows)))
        print(" recent pages: " + str(len(recent_rows)))
        
        # If we hit the limit, the lists may be incomplete, and pages could be wrongly treated as orphans. Warn so a smaller website can be chosen
        
        if len(past_rows) >= MAX_ROWS or len(recent_rows) >= MAX_ROWS:
            print(" WARNING: the limit was reached, so this list may be incomplete")
            print(" Consider replacing " + domain + " with a smaller website")
            
        history_path = os.path.join(common.HISTORY_FOLDER, domain + ".csv")
        common.write_rows(history_path, past_rows + recent_rows, ["timestamp", "url"])