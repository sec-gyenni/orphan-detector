#!/bin/bash

# This script runs the pipeline on REAL websites. Before running:
# In common.py set LOCAL_TEST = False
# Check the websites listed in REAL_DOMAINS

set -e

echo "=== Download archive history==="
python download_history.py

echo "===Find and filter candidates==="
python find_candidates.py
python remove_dynamic_urls.py
python limit_candidates.py

echo "===Check the candidates on the live websites ==="
python check_alive.py
python remove_duplicates.py
python score_pages.py
python label_pages.py

echo "===Security headers and chart ==="
python check_headers.py
python draw_funnel.py

echo "===Done. See the reports_real folder for the results==="