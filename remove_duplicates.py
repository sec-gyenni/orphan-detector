"""This script removes "soft 404"  and invalid pages (Section 3.2.3 and 3.2.5 of the paper )
A soft 404 is a page that SAYS "page not found" but still answers "200 OK"

"""

import os
import time
import requests
import common

#Two pages on the same website whose sizes are this close (in bytes) are treated as copies of the same error page. The paper uses 5
SIZE_TOLERANCE_BYTES =5

# this downlaods, save and measure each page
alive = common.read_rows(os.path.join(common.DATA_FOLDER, "alive.csv"))
downloaded = []

for row in alive:
    page_url = row["url"]
    try: 
        response = requests.get(
            page_url,
            headers ={"User-Agent": common.USER_AGENT},
            timeout=30,
            allow_redirects=False,
        )
    except requests.RequestException as error:
        print(" could not download: " + page_url)
        continue
    
    #This saves the page as it looks today, so later steps can read it
    common.write_text_file(common.live_page_path(page_url), response.text)
    
    # This records the size in bytes, and what time of file the server says it is
    row["size"] = len(response.content)
    row["content_type"] = response.headers.get("Content-Type", "")
    downloaded.append(row)
    print(" downloaded (" + str(row["size"]) + " bytes): " + page_url)
    
    # Wait a moment before the next request, sent to polite to the website 
    
def has_size_twin(page, all_pages):
    """True if another page on the same website has almost the same size"""
    for other_page in all_pages:
        if other_page["url"] == page["url"]:
            continue # do not compare a page with itself
        same_website = common.get_domain(other_page["url"]) == common.get_domain(page["url"])
        size_difference = abs(other_page["size"] - page["size"])
        if same_website and size_difference <= SIZE_TOLERANCE_BYTES:
            return True
    return False

different_size_pages = []
for page in downloaded:
    if has_size_twin(page, downloaded):
        print(" removed (same size as another page): " + page["url"])
    else:
        different_size_pages.append(page)

common.log_funnel_step("after size-based filtering", len(different_size_pages))

# Removing invalid pages
valid_pages = []
for page in different_size_pages:
    if "text/html" in page["content_type"]:
        valid_pages.append(page)
    else:
        print(" removed (not an HTML page): " + page["url"])
        
common.log_funnel_step("after removing invalid pages", len(valid_pages))

# Saving the pages that are left 

unique_path = os.path.join(common.DATA_FOLDER, "unique.csv")
common.write_rows(unique_path, valid_pages, ["url", "last_seen", "size", "content_type"])