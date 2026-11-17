"""This script checks which candidate pages are still tody (Section 3.1.4 of the paper).
An orphan must still be reachable. If a candidate no longer loads, the owner deleted it properly, so it is not an orphan and we drop it"""


import os
import time 
import requests
import common

# Loading the candidates

candidates = common.read_rows(os.path.join(common.DATA_FOLDER, "sampled_candidates.csv"))
alive_rows = []

# This asks the server about each page 

for row in candidates:
    page_url = row["url"]
    try:
        # this asks the status only not redirects: the paper keeps only pages that answer "200 OK" directly
        response = requests.head(
            page_url,
            headers={"User-Agent": common.USER_AGENT},
            timeout=30,
            allow_redirects=False,
        )
        if response.status_code == 200:
            # 200 means "OK, the page is here", so it may be an orphan
            alive_rows.append(row)
            print(" still online: " + page_url)
        else:
            # Any other code means, it gets dropped
            print(" gone (status " + str(response.status_code) + "): " + page_url)
    except requests.RequestException as error:
        # The website could not be reached at all (it could be down, refused or too slow)
        # The page is going to be skipped instead of letting the whole script crash
        print (" could not reach: " + page_url)
        if common.LOCAL_TEST:
            print(" Is the test server running? Start it with: python3 -m http.server 8000 -d site")
            
    # Wait a moment before the next request, to be polite to the website 
    time.sleep(common.POLITE_DELAY_SECONDS)
    
    
# This saves the pages that are still online 

alive_path = os.path.join(common.DATA_FOLDER, "alive.csv")
common.write_rows(alive_path, alive_rows, ["url", "last_seen"])
common.log_funnel_step("still online (HTTP 200)", len(alive_rows))