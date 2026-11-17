"""This draws the two similarity measure side by side"""

import os 
import matplotlib
matplotlib.use("Agg") # draw straight into a file; no window needed 
import matplotlib.pyplot as plt
import common

# Read the scores and split the pages into two groups 

kept_simhash = []
kept_difflib = []
dropped_simhash = []
dropped_difflib = []

for row in common.read_rows(os.path.join(common.DATA_FOLDER, "all_scores.csv")):
    if float(row["score"]) >= 0.9:
        kept_simhash.append(float(row["simhash_similarity"]))
        kept_difflib.append(float(row["difflib_similarity"]))
    else:
        dropped_simhash.append(float(row["simhash_similarity"]))
        dropped_difflib.append(float(row["difflib_similarity"]))
        
def average(numbers):
    """The average of a list of numbers, or 0 if the list is empty"""
    if len(numbers) == 0:
        return 0
    return sum(numbers) / len(numbers)

simhash_averages = [average(kept_simhash), average(dropped_simhash)]
difflib_averages = [average(kept_difflib), average(dropped_difflib)]
group_names = ["Kept pages (score 0.9 or more)\nnumber of pages: " + str(len(kept_simhash)), "Dropped pages\nnumber of pages: " + str(len(dropped_simhash))]

# Draw the side-by-side bars 

SIMHASH_COLOUR = "#2a78d6" # blue 
DIFFLIB_COLOUR = "#eb6834" # orange
BAR_WIDTH = 0.34

figure, axes = plt.subplots(figsize = (7, 4))

simhash_positions = []
difflib_positioins = []
for index in range(len(group_names)):
    simhash_positions.append(index - BAR_WIDTH / 2)
    difflib_positioins.append(index + BAR_WIDTH / 2)
    
axes.bar(simhash_positions, simhash_averages, BAR_WIDTH - 0.02,
        color=SIMHASH_COLOUR, label="Simhash simililarity (paper's method)")
axes.bar(difflib_positioins, difflib_averages, BAR_WIDTH - 0.02, 
        color=DIFFLIB_COLOUR, label="difflib similarity (comparison)")

# Write the value on top of each bar
for index in range (len(group_names)):
    axes.text(simhash_positions[index], simhash_averages[index] + 0.02,
            str(round(simhash_averages[index], 2)), ha="center")
    axes.text(difflib_positioins[index], difflib_averages[index] + 0.02,
            str(round(difflib_averages[index], 2)), ha="center")

# The chance level for a 64-digit simhash
axes.axhline(0.5, color="#6b6b68", linestyle=":")
axes.text(1.5, 0.52, "chance level for simhash", ha="right", color="#6b6b68", fontsize=8)

axes.set_xticks(range(len(group_names)))
axes.set_xticklabels(group_names)
axes.set_ylim(0, 1.2)
axes.set_ylabel("Average similarity (0 to 1)")
axes.set_title("Simhash against difflib: old and new version of each page")
axes.legend(fontsize=8, frameon=False)
axes.spines["top"].set_visible(False)
axes.spines["right"].set_visible(False)
figure.tight_layout()

# Saving the picture 
output_path = os.path.join(common.REPORTS_FOLDER, "similarity.png")
figure.savefig(output_path, dpi=150)
print("Saved " + output_path)