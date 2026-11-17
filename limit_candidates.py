"""This script keeps at most MAX_PER_WEBSITE candidates for each website before we start sending requests to websites """

import os
import random
import common

# Settings
MAX_PER_WEBSITE = 40
RANDOM_SEED = 42  # any fixed number; it makes the "random" sample repeatable

# Group the candidates by website 

candidates = common.read_rows(os.path.join(common.DATA_FOLDER, "static_candidates.csv"))

addresses_by_domain = {}
for row in candidates:
    domain = common.get_domain(row["url"])
    if domain not in addresses_by_domain:
        addresses_by_domain [domain] = []
    addresses_by_domain[domain].append(row["url"])
    
# Take a repeatable random sample from each website 

random.seed(RANDOM_SEED)

chosen_addresses = []
for domain in addresses_by_domain:
    addresses = addresses_by_domain[domain]
    if len(addresses) > MAX_PER_WEBSITE:
        sample = random.sample(addresses, MAX_PER_WEBSITE)
        print(" " + domain + ": checking " + str(MAX_PER_WEBSITE) + " of " + str(len(addresses)) + " candidates")
    else:
        sample = addresses
        print(" " + domain + ": checking all " + str(len(addresses)) + " candidates")
    for address in sample:
        chosen_addresses.append(address)
        
# Saving the sample 

rows_to_save = []
for row in candidates:
    if row["url"] in chosen_addresses:
        rows_to_save.append(row)
        
common.write_rows(os.path.join(common.DATA_FOLDER, "sampled_candidates.csv"), rows_to_save, ["url", "last_seen"])
common.log_funnel_step("sampled for checking (at most " + str(MAX_PER_WEBSITE) + " per site)", len(rows_to_save))