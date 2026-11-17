"""This script labels each high-scoring page using clues on the page itself (Section 4.5, Table 2 Appendix A of the paper)"""

import os
import common

# A.2: phrases that mean the page is really an error page
ERROR_PHRASES = ["404 not found", "404 error", "page not found", "no longer exists"]

#A.1: code that sends the visitor on to a different page

REDIRECT_CLUES = ["window.location", "top.location", 'http-equiv="refresh"', "redirect(", "object moved to"]

# A.3: tags that load another page inside this one
FRAME_CLUES = ["<iframe", "<frame", "<frameset"]

# A page with fewer visible words than this is a blank template (Section 4.5.2)
BOILERPLATE_WORD_LIMIT = 5

# How many characters either side of "copyright" to search for a year (Section 4.5.1)

COPYRIGHT_SEARCH_DISTANCE = 50

# 

def find_years(text):
    """Return every four-digit year (1900 to 2099) found in the text"""
    years = []
    for start in range(len(text) - 3):
        piece = text[start:start + 4]
        if piece.isdigit() and (piece.startswith("19") or piece.startswith("20")):
            years.append(int(piece))
    return years

# the copyright_label

def copyright_label(visible_text):
    """Look for a copyright statement and judge how old it is. Return a label, or "" if has no copyright statement """
    lower_text = visible_text.lower()
    
    # Find where the copyright statement is: the word, or the symbol
    position = lower_text.find("copyright")
    if position == -1:
        position = lower_text.find("©")
    if position == -1:
        return "" # no copyright statement on this page
    
    # Look at the text just  before and after it, and search for years
    start = max (0, position - COPYRIGHT_SEARCH_DISTANCE)
    end = position + COPYRIGHT_SEARCH_DISTANCE
    nearby_text = visible_text[start:end]
    years = find_years(nearby_text)
    
    if len(years) == 0:
        return "likely orphaned (copyright without date)"
    
    # if there are several years, the latest one counts
    lastest_year = max(years)
    if lastest_year >= common.CURRENT_YEAR -1:
        return "not orphaned (recent copyright)"
    return "likely orphaned (old copyright)"

# this is labels the pages 

def label_page(html):
    """Decide the label for one page from its HTML"""
    lower_html = html.lower()
    visible_text = common.get_visible_text(html)
    lower_text = visible_text.lower()
    
    # Is it really an error page ?
    for phrase in ERROR_PHRASES:
        if phrase in lower_text:
            return "not orphaned (error page)"
        
    # Does it send the visitor elsewhere, or load another page inside it ?
    for clue in REDIRECT_CLUES:
        if clue in lower_html:
            return "uncertain (redirect)"
    for clue in FRAME_CLUES:
        if clue in lower_html:
            return "uncertain (frame)"
    
    #Is it a blank template with almost no words
    word_count = len(visible_text.split())
    if word_count < BOILERPLATE_WORD_LIMIT:
        return "likely orphaned (boilerplate)"
    
    # Does it have a copyright statement?
    label = copyright_label(visible_text)
    if label != "":
        return label
    
    # No clear clue either way
    return "uncertain (undefined)"

# Label every page
pages = common.read_rows(os.path.join(common.DATA_FOLDER, "scored.csv"))

labelled_rows =[]
for row in pages:
    html = common.read_text_file(common.live_page_path(row["url"]))
    row["label"] = label_page(html)
    labelled_rows.append(row)
    print(" " + row["url"] + " -> " + row["label"])
    
# Save, and print a summary like Table 2

columns = ["url", "last_seen", "age", "simhash_similarity", "difflib_similarity", "score", "label"]
common.write_rows(os.path.join(common.DATA_FOLDER, "labelled.csv"), labelled_rows, columns)

likely_count = 0
uncertain_count = 0
not_orphan_count = 0
for row in labelled_rows:
    if row["label"].startswith("likely orphaned"):
        likely_count = likely_count + 1
    elif row["label"].startswith("uncertain"):
        uncertain_count = uncertain_count + 1
    else: 
        not_orphan_count = not_orphan_count + 1
        
print()
print("Summary (like Table 2 in the paper):")
print(" likely orphaned: " + str(likely_count))
print(" uncertain:       " + str(uncertain_count))
print(" not orphaned:    " + str(not_orphan_count))

common.log_funnel_step("likely orphaned", likely_count)