""" This script measures how well our detector did on the test site, where we know the answers"""

import os
import common

TRUE_ORPHANS = ["page21.html", "page22.html", "page23.html", "page24.html", "page25.html", "page26.html", "page27.html", "page28.html"]

# Each decoy, and the step that SHOULD remove it

DECOYS = {
    "old-logo.png": "removing non-page files",
    "january-new-product-range-announcement.html": "Dynamic URL Detection",
    "page29.html": "liveness check",
    "page30.html": "size-based filtering",
    "page31.html": "size-based filtering",
    "page32.html": "orphan score",
    
}

# The output file of each step, in the pipeline order, and the step's name
STEPS = [
    ("candidates.csv", "removing non-page files"),
    ("static_candidates.csv", "Dynamic URL Detection"),
    ("alive.csv", "liveness check"),
    ("unique.csv", "size-based filtering"),
    ("scored.csv", "orphan score"),
]

def page_name(url):
    """The last part of an address, e.g. ".../news/x.html" gives "x.html" """
    return url.split("/")[-1]

def page_names_in(csv_name):
    """Return the page names listed in one of the pipeline's CSV files"""
    names = []
    for row in common.read_rows(os.path.join(common.DATA_FOLDER, csv_name)):
        names.append(page_name(row["url"]))
    return names

# The pages our detector flagged as likely orphaned
flagged = []
for row in common.read_rows(os.path.join(common.DATA_FOLDER, "labelled.csv")):
    if row ["label"].startswith("likely orphaned"):
        flagged.append(page_name(row["url"]))

found_correctly = []
missed = []
false_alarms = []

for name in TRUE_ORPHANS:
    if name in flagged:
        found_correctly.append(name)
    else:
        missed.append(name)
        
for name in flagged:
    if name not in TRUE_ORPHANS:
        false_alarms.append(name)
        
# Recall: of the real orphans, what share did we find?

recall = len(found_correctly) / len(TRUE_ORPHANS)

#Precision: of the pages we flagged, what share were right ?

if len(flagged) > 0:
    precision = len(found_correctly) / len(flagged)
else:
    precision = 0

print("True orphans planted : " + str(len(TRUE_ORPHANS)))
print("Pages flagged        : " + str(len(flagged)))
print("Found correctly      : " + str(len(found_correctly)))
print("Missed               : " + str(missed))
print("False alarms         : " + str(false_alarms))
print("Recall               : " + str(round(recall * 100)) + "%")
print("Precision            : " + str(round(precision * 100)) + "%")
print()

print("Where each decoy was caught:")
decoy_rows = []
for decoy in DECOYS:
    expected_step = DECOYS[decoy]
    
    # Walk through the steps in order. The decoy was removed by the first step whose output file contains it.
    
    caught_by = "NOT CAUGHT"
    for csv_name, step_name in STEPS:
        if decoy not in page_names_in(csv_name):
            caught_by = step_name
            break
    
    if caught_by == expected_step:
        result = "as expected"
    else:
        result = "UNEXPECTED"
        
    print(" " + decoy + " -> " + caught_by + " (" + result + ")")
    decoy_rows.append({"decoy": decoy, "expected_step": expected_step, "caught_by": caught_by, "result": result})
    
    
# The other 5 news articles go same way as the January one.

common.write_rows(os.path.join(common.REPORTS_FOLDER, "accuracy.csv"), decoy_rows, ["decoy", "expected_step", "caught_by", "result"])