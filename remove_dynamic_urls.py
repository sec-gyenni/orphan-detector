"""Dynamic URL Detection (DUDe), from section 3.1.3 and algorithm 1 from the paper.
This script find groups of long, automatically made addresses that share the same start (a "prefix"), such as old new articles, and removes them"""

import os
import common

# The paper's settings for DUDe (Section 3.1.3)

# A prefix  must be shared by at least this share of site's addresses (5%)

POPULARITY_CUTOFF = 0.05

# A prefix must have at least this many characters after the domain name.
# This is going to stop us removing a whole website with a tiny prefix like "/"

SHORT_LINK_THRESHOLD = 15

# An address  counts as "long" if it has more than this many characters after the domain name.

LONG_LINK_THRESHOLD = 20

# DUDe only runs if a site has more than this many long addresses
LONG_LINK_CUTOFF = 0

# The paper adds 8 for the length of "https://" in its length checks
SCHEME_LENGTH = 8

# Helper functions

def is_long_link(url, domain):
    """True if the address is long enough to look automatically made"""
    return len(url) > LONG_LINK_THRESHOLD + len(domain) + SCHEME_LENGTH

def most_common_characters(long_links):
    """This builds a new address from the most common character at each position"""
    
    # Find the length of the longest address 
    longest_length = 0
    for link in long_links:
        if len(link) > longest_length:
            longest_length = len(link)
    
    built_link = ""
    for position in range(longest_length):
        # Count how often each character appears at this position
        counts = {}
        for link in long_links:
            if position < len(link):
                character = link[position]
                if character in counts:
                    counts[character] = counts[character] + 1
                else:
                    counts[character] = 1
                    
        # Pick the most common one. If there is a tie, the first one met wins
        best_character = ""
        best_count = 0
        for character in counts:
            if counts[character] > best_count:
                best_character = character
                best_count = counts[character]
        built_link = built_link + best_character
            
    return built_link

def addresses_starting_with (prefix, addresses):
    """Return the addresses that begin with the prefix"""
    matches = []
    for address in addresses:
        if address.startswith(prefix):
            matches.append(address)
    return matches

def remove_dynamic_urls(addresses, domain):
    """Run DUDe on one website's addresses. Returns two lists: the addresses we keep, and the one we remove"""
    kept = list (addresses)
    removed = []
    total_addresses = len(addresses)
    shortest_allowed_prefix = len(domain) + SCHEME_LENGTH + SHORT_LINK_THRESHOLD
    
    while True:
        # find the long addresses. Stop if there are not enough 
        long_links = []
        for address in kept:
            if is_long_link(address, domain):
                long_links.append(address)
        if len(long_links) <= LONG_LINK_CUTOFF:
            break
            
        # build a "typical" long address and cut it to the average length
        total_length = 0
        for address in kept:
            total_length = total_length + len(address)
        average_length = round(total_length / len(kept))
        prefix = most_common_characters (long_links)[:average_length]
            
        # shorten the prefix one character at a time until enough address start with it, or until it becomes too short
        matches = addresses_starting_with (prefix, kept)
        while len(matches) == 0 or len(matches) < POPULARITY_CUTOFF * total_addresses:
            if len(prefix) < shortest_allowed_prefix:
                break
            prefix = prefix[:-1]
            matches = addresses_starting_with(prefix, kept)
                
        # a prefix that is too short is not trusted, so we stop
        # The paper tries again while ignoring these addresses.
            
        if len(prefix) < shortest_allowed_prefix:
            break
            
        # remove every address that starts with the prefix, then repeat
        print(" dynamic prefix found " + prefix + " (" + str(len(matches)) + " addresses)")
        for address in matches:
            kept.remove(address)
            removed.append(address)
                
    return kept, removed

# This will check against the paper's own example 

print (" Checking DUDe with the paper's example (Listing 1):")
paper_example = [
    "https://example.com/articles/1997/January/article1.html",
    "https://example.com/articles/1997/February/article1.html",
    "https://example.com/articles/2002/May/article1.html",
    "https://example.com/articles/2002/May/article2.html",
    "https://example.com/contact.html",
    "https://example.com/login.html",
]
example_kept, example_removed = remove_dynamic_urls(paper_example, "example.com")
print(" kept: " + str(example_kept))
print(" (the paper's Listing 2 keeps only contact.html and login.html)")
print()

# This is going to Run DUDe on our candidates, one site at a time

candidates = common.read_rows(os.path.join(common.DATA_FOLDER, "candidates.csv"))

# Group the candidate addresses by website, because DUDe works per website

addresses_by_domain = {}
for row in candidates:
    domain = common.get_domain(row["url"])
    if domain not in  addresses_by_domain:
        addresses_by_domain[domain] = []
    addresses_by_domain[domain].append(row["url"])
    
# Ru DUDe on each website and collect the addresses we keep 
kept_addresses = []
for domain in addresses_by_domain:
    print("Running DUDe on " + domain + ":")
    kept, removed = remove_dynamic_urls(addresses_by_domain[domain], domain)
    for address in kept:
        kept_addresses.append(address)
        
# This is going to save what is left

rows_to_save = []
for row in candidates:
    if row["url"] in kept_addresses:
        rows_to_save.append(row)
        
output_path = os.path.join(common.DATA_FOLDER, "static_candidates.csv")
common.write_rows(output_path, rows_to_save, ["url", "last_seen"])
common.log_funnel_step("after Dynamic URL Detection", len(rows_to_save))