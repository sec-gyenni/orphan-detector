#!/bin/bash
#This runs the whole orphan-detection pipeline on the local test site, in order

set -e

echo "=== Build the test site and the pretend archive === "
rm -rf data site
python make_local_archive.py

echo "===Start the local web server in the background==="
python -m http.server 8000 -d site > /dev/null 2>&1 &
SERVER_ID=$!

# Make sure the server is stopped when this script ends, even after an error
trap "kill $SERVER_ID" EXIT

#Give the server a second to start up

sleep 1

echo "===Run the pipeline==="
python find_candidates.py
python remove_dynamic_urls.py
python limit_candidates.py
python check_alive.py
python remove_duplicates.py
python score_pages.py
python label_pages.py
python check_headers.py

echo "=== Measure accuracy and draw the chart ==="
python measure_accuracy.py
python draw_funnel.py

echo "===Done. See the reports folder for the results==="