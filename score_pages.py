"""Gives each candidate an "orphan score" (Section 4.3 and 4.4 of the paper)"""

import os
import time
import difflib
import requests
import common

# There are settings from the paper 

NGRAM_SIZE = 8   # the length of each piece of text
FINGERPRINT_BITS = 64 # the number of binary digits in a fingerprint
SIMILARITY_WEIGHT = 0.9 #w_s in the paper
AGE_WEIGHT = 0.1 # w_a in the paper
SCORE_CUTOFF = 0.9 # keep pages scoring at least this much 

# Two fixed  numbers that define the FNV-1a hash (64-bit version)
FNV_OFFSET = 14695981039346656037
FNV_PRIME = 1099511628211

# this is the simhash fingerprint 

def fnv1a_hash(text):
    """Turn a piece of text into a 64-bit number using FNV-1a. The same text always give the same number"""
    hash_value = FNV_OFFSET
    for byte in text.encode ("utf-8"):
        hash_value = hash_value ^ byte
        hash_value = (hash_value * FNV_PRIME) % (2 ** 64)
    return hash_value

# The simhash 
def simhash(text):
    """Make a 64-digit fingerprint (a string of 0s and 1s) for some text. Similar text get similar fingerprints"""
    # One  running total ("vote") for each of the 64 digits
    
    votes = [0] * FINGERPRINT_BITS
    
    # Cut the text into overlpapping 8 -character pieces
    
    for start in range (len(text) - NGRAM_SIZE + 1):
        piece = text [start:start + NGRAM_SIZE]
        
        # Write the piece's hash as 64 binary digits 
        bits = format (fnv1a_hash(piece), "064b")
        
        # Each digit votes a "1" adds one, a "0" takes one away
        for position in range (FINGERPRINT_BITS):
            if  bits [position] == "1":
                votes[position] = votes[position] + 1
            else:
                votes[position] = votes[position] - 1
                
    # A positive total becomes "1", otherwise "0"
    fingerprint = ""
    for total in votes:
        if total > 0:
            fingerprint = fingerprint + "1"
        else:
            fingerprint = fingerprint + "0"
    return fingerprint

def simhash_similarity(text_a, text_b):
    """Compare two texts from 0 (completely different) to 1 (the same). We count how many of the 64 digits differ (the "Hamming distance")""" 
    fingerprint_a = simhash(text_a)
    fingerprint_b = simhash(text_b)
    differences = 0
    for position in range (FINGERPRINT_BITS):
        if fingerprint_a[position] != fingerprint_b[position]:
            differences = differences + 1
    return 1 - (differences / FINGERPRINT_BITS)

# the difflib_similarity

def difflib_similarity(text_a, text_b):
    """A second, similarity measure from Python's difflib, for comparison"""
    return difflib.SequenceMatcher(None, text_a, text_b).ratio()   

def get_archived_html(page_url, timestamp):
    """Return the page as the Internet Archive saw it. Local test: read our saved copy. Real run: ask the Wayback Machine"""
    
    if common.LOCAL_TEST:
        return common.read_text_file(common.archived_page_path(page_url))
    
    #"id_" asks the Wayback Machine for original page, without its toolbar.
    wayback_url = "https://web.archive.org/web/" + timestamp + "id_/" + page_url
    try:
        response = requests.get(wayback_url, headers={"User-Agent": common.USER_AGENT}, timeout=60)
        return response.text
    except requests.RequestException as error:
        print(" could not fetch archived copy: " + page_url)
        return ""
    
def year_of (timestamp):
    """Take the year form a timestamp"""
    return int(timestamp[:4])

# This is going to score every page

pages = common.read_rows(os.path.join(common.DATA_FOLDER, "unique.csv"))

# Find the oldest page, so every age can be scaled to between 0 and 1. The paper uses 23 years, the oldest age in its own data

oldest_age = 1
for row in pages:
    age = common.CURRENT_YEAR - year_of(row["last_seen"])
    if age > oldest_age:
        oldest_age = age
        
secored_rows = []
kept_rows = []
for row in pages:
    pages_url = row["url"]
    
    # The visible words of the page today, and as the archive saw it.
    today_text = common.get_visible_text(common.read_text_file(common.live_page_path(pages_url)))
    archived_text = common.get_visible_text(get_archived_html(pages_url, row["last_seen"]))
    
    # how similar the two version are.
    similarity = simhash_similarity(today_text, archived_text)
    
    # how old the page is, scaled to between 0 and 1
    age = common.CURRENT_YEAR - year_of(row["last_seen"])
    age_scaled = age / oldest_age
    
    # the paper's orphan score 
    score = (SIMILARITY_WEIGHT * similarity) + (AGE_WEIGHT * age_scaled)
    
    # Build a fresh row holding just the columns we want to save
    result = {
        "url": pages_url,
        "last_seen": row["last_seen"],
        "age": age,
        "simhash_similarity": round(similarity, 3),
        "difflib_similarity": round(difflib_similarity(today_text, archived_text), 3),
        "score": round(score, 3),
    }
    secored_rows.append(result)
    
    if score >= SCORE_CUTOFF:
        kept_rows.append(result)
        print(" kept (score " + str(result["score"]) + "): " + pages_url)
    else: 
        print(" dropped (score " + str(result["score"]) + "): " + pages_url)
        
# Saving the results 

columns = ["url", "last_seen", "age", "simhash_similarity", "difflib_similarity", "score"]

# Every page with its scores (used for the similarity chart)
common.write_rows(os.path.join(common.DATA_FOLDER, "all_scores.csv"), secored_rows, columns)
common.write_rows(os.path.join(common.DATA_FOLDER, "scored.csv"), kept_rows, columns)
common.log_funnel_step("orphan score 0.9 or more", len(kept_rows))