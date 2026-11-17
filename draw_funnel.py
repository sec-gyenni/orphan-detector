"""This script draws the filtering funnel: how many pages are left after each step. This is our version of the Table 1 on the paper """

import os
import matplotlib
matplotlib.use("Agg") # this draws straight into a file and we will not need a window
import matplotlib.pyplot as plt
import common

# This read the funnel log
# If a step was run more than once, keep only its latest count 

step_names = []
step_counts = {}
for row in common.read_rows(os.path.join(common.DATA_FOLDER, "funnel.csv")):
    step = row["step"]
    if step not in step_names:
        step_names.append(step)
    step_counts[step] = int(row["count"])
    
counts = []
for step in step_names:
    counts.append(step_counts[step])
    
# This draws the chat
BAR_COLOUR = "#2A78d6" # every bar will be a blue colour
TEXT_COLOUR = "#52514e" # and dark gray for labels

figure, axes = plt.subplots(figsize=(9, 4.5))
axes.barh(step_names, counts, color=BAR_COLOUR, height=0.6)

# Put the first step at the top, like a funnel
axes.invert_yaxis()

# Real websites have thousands of pages at the top and only a handful at the bottom. A "log" scale (1, 10, 100, 1000, ...) lets every bar be seen,
# as in the paper's own charts. The small test site keeps a normal scale.
use_log_scale = max(counts) > 1000
if use_log_scale:
    axes.set_xscale("log")

# Write the exact number just past the end of each bar.
for position in range(len(counts)):
    if use_log_scale:
        label_x = counts[position] * 1.1
    else:
        label_x = counts[position] + max(counts) * 0.01
    axes.text(label_x, position, str(counts[position]),
            va="center", color=TEXT_COLOUR)


if common.LOCAL_TEST:    
    axes.set_title("Pages remaining after each filtering step (test site)")
else:
    axes.set_title("Pages remaining after each filtering step (real websites)")

# Keep the chart clean
axes.spines["top"].set_visible(False)
axes.spines["right"].set_visible(False)

if use_log_scale:
    axes.set_xlabel("Pages remaining (log scale)")
else:
    axes.set_xlabel("Pages remaining")

figure.tight_layout()

# Saving the pictures
output_path = os.path.join(common.REPORTS_FOLDER, "funnel.png")
figure.savefig(output_path, dpi=150)
print("Saved " + output_path)