"""This script finds orphan pages. These are pages the archive saw in the past, 
but has not seen recently. These pages have lost their links"""

import os
import sys
import glob # this finds files that match a pattern, such as *.csv
import common

# This is going to start a fresh funnel for this run 

# This is going to be the first step, so it will clear any counts left from an earlier run

common.start_new_funnel()

# This finds the most recent date each page was seen 

# Get a list of every history file (one per website)
history_files = glob.glob(os.path.join(common.HISTORY_FOLDER, "*.csv"))

# Stop with a helpful message if there is no history to read 
if len(history_files) == 0:
    print("No history files found. Run make_local_archive.py first")
    sys.exit(1)
    
# For each page, remember the  LATEST date the archive saw it.
last_seen = {}
for history_file in history_files:
    for row in common.read_rows(history_file):
        page_url = row["url"]
        timestamp = row ["timestamp"]
        if page_url not in last_seen:
            # If it is the first time we are seeing this page: store its data
            last_seen[page_url] = timestamp
        elif timestamp > last_seen[page_url]:
            # We have met it before, but this date is newer: keep the newer one.
            last_seen[page_url] = timestamp
# Record how many different pages the archive knows about.

common.log_funnel_step("pages in archive history", len(last_seen))

# This keeps the last seen BEFORE the cut-off date 

# A page the archive has not seen since before the cut-off has lost its links

candidate_urls = []
for page_url in last_seen:
    if last_seen[page_url] < common.CUTOFF_DATE:
        candidate_urls.append(page_url)
        
common.log_funnel_step("seen in the past, not recently", len(candidate_urls))

# This removes anything that is not a web page

def is_web_page(page_url):
    """Return True if the address looks like a web page, and false if it ends in a picture, video, font, etc"""
    
    # Drop anything after a "?" and make it lowercase 
    address = page_url.split("?")[0].lower()
    # Check the ending against the paper's list of non-page file types
    if address.endswith(common.NON_PAGE_EXTENSIONS):
        return False
    return True

# This keeps the web pages; report anything we throw away
page_candidates = []
for page_url in candidate_urls:
    if is_web_page(page_url):
        page_candidates.append(page_url)
    else:
        print(" not a web page, removed: " + page_url)

common.log_funnel_step("after removing non-page files", len(page_candidates))

# This saves the candidates

# Sorts alphabetically so that the file is tidy and the same on every run

page_candidates.sort()

# This builds one row per candidate: its address and the last date it was seen.
rows_to_save = []
for page_url in page_candidates:
    rows_to_save.append({"url": page_url, "last_seen": last_seen[page_url]})
    
# Save the rows for the next step of the pipeline 
candidates_path = os.path.join(common.DATA_FOLDER, "candidates.csv")
common.write_rows(candidates_path, rows_to_save, ["url", "last_seen"])
print("Saved " + str(len(rows_to_save)) + " candidates to " + candidates_path)