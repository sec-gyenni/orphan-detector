"""This script is going to create a pretend/fake Internet Archive for our local test site


"""

import os
import sys
import subprocess
from bs4 import BeautifulSoup
import common

# Settings for the pretend internet archive 

SITE_FOLDER = "site"

# When each snapshot was taken. Written the way the Internet Archive writes dates: YYYYMMDDmmss (year, month day, hours, minutes, seconds)

OLD_SNAPSHOT_DATE = "20190101000000"
NEW_SNAPSHOT_DATE = "20260101000000"

# Helper functions

def build_site(version):
    """this runs the make_test_site.py to build the "before" or "after" site """
    subprocess.run([sys.executable, "make_test_site.py", version], check = True)
    
def crawl_home_page():
    """This is going to act like the archive crawler: it is going to start at the home page and return every address it links to (plus the home page itself)"""

    home_page_path = os.path.join (SITE_FOLDER, "index.html")
    home_html = common.read_text_file (home_page_path)
    soup = BeautifulSoup(home_html, "html.parser")

    found_addresses =  ["index.html"]
    for link in soup.find_all("a"):
        address = link.get("href")
        found_addresses.append(address)
    return found_addresses

def full_url(address):
    """Turn a short address like "page1.html" into a full web address."""
    return common.LOCAL_SITE_URL + "/" + address

# The 2019 snapshot 

build_site("before")

old_snapshot = crawl_home_page()

# Save an archived copy of page the crawler saw in 2019

saved_copies = 0
for address in old_snapshot:
    page_file = os.path.join(SITE_FOLDER, address)
    if os.path.exists(page_file):
        page_html = common.read_text_file(page_file)
        common.write_text_file(common.archived_page_path(full_url(address)), page_html)
        saved_copies = saved_copies + 1

# This is for today's snapshot 

build_site ("after")
new_snapshot = crawl_home_page()

# Write the history file 

history_rows= []
for address in old_snapshot:
    history_rows.append({"timestamp": OLD_SNAPSHOT_DATE, "url": full_url(address)})
for address in new_snapshot:
    history_rows.append({"timestamp": NEW_SNAPSHOT_DATE, "url": full_url(address)})
    
# This is going to name the file after the website 

site_name = common.get_domain(common.LOCAL_SITE_URL).replace(":", "_")
history_path = os.path.join(common.HISTORY_FOLDER, site_name + ".csv")
common.write_rows(history_path, history_rows, ["timestamp", "url"])


# This prints the summary

print("2019 snapshot: the crawler saw " + str(len(old_snapshot)) + " addresses.")
print("Today's snapshot: the crawler saw " + str(len(new_snapshot)) + " addresses")
print("Wrote " + str(len(history_rows)) + " history rows to " + history_path)
print("Saved " + str(saved_copies) + " archived copies of pages")