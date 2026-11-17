"""
Security check: do orphaned pages have weaker security settings than maintained pages? This is our version of Table 4 paper (Section 5.2.3)
"""
import os 
import time
import requests
import matplotlib
matplotlib.use("Agg") # draw straight into a file: no window needed 
import matplotlib.pyplot as plt
import common

SECURITY_HEADERS = [
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Strict-Transport-Security",
    "Referrer-Policy",
]

# The names of every check, in order they appear  in our results
CHECK_NAMES = []
for header in SECURITY_HEADERS:
    CHECK_NAMES.append("no " + header)
CHECK_NAMES.append("cookie without Secure flag")
CHECK_NAMES.append("cookie without HttpOnly flag")

# Check one page

def check_page(page_url):
    """Fetch a page and return a dictionary of True/False results, where True means "this protection is MISSING" Returns None if the page could not be fetched"""
    try:
        response = requests.get(
            page_url,
            headers={"User-Agent": common.USER_AGENT},
            timeout=30,
            allow_redirects=False,
        )
    except requests.RequestException as error:
        print(" could not reach: " + page_url)
        return None
    
    results = {}
    
    # Is each security header missing ?
    # requests ignores capital letters when looking up header names
    
    for header in SECURITY_HEADERS:
        results ["no " + header] = header not in response.headers
        
    # Cookie flags. We only judge pages that actually set a cookie
    cookie_text = response.headers.get("Set-Cookie", "").lower()
    if cookie_text == "":
        results["cookie without Secure flag"] = None
        results["cookie without HttpOnly flag"] = None
    else:
        results["cookie without Secure flag"] = "secure" not in cookie_text
        results["cookie without HttpOnly flag"] = "httponly" not in cookie_text
        
    return results

orphan_urls = []
for row in common.read_rows(os.path.join(common.DATA_FOLDER, "labelled.csv")):
    if row["label"].startswith("likely orphaned"):
        orphan_urls.append(row["url"])

# The control group: the home page of every website that has an orphan 
control_urls = []
for page_url in orphan_urls:
    scheme = page_url.split("://")[0]
    home_page = scheme + "://" + common.get_domain(page_url) + "/"
    if home_page not in control_urls:
        control_urls.append(home_page)
        
groups = {"orphaned": orphan_urls, "control": control_urls}

# Check every page in both  groups
page_rows = []
for group_name in groups:
    print("Checking the " + group_name + " group:")
    for page_url in groups [group_name]:
        results = check_page(page_url)
        time.sleep(common.POLITE_DELAY_SECONDS)
        if results is None:
            continue
        row = {"group": group_name, "url": page_url}
        for check in CHECK_NAMES:
            row[check] = results[check]
        page_rows.append(row)
        print(" checked: " + page_url)
        
common.write_rows(os.path.join(common.REPORTS_FOLDER, "security_headers.csv"), page_rows, ["group", "url"] + CHECK_NAMES)

# Work out the percentages

summary_rows = []

# Only checks that could be judge in BOTH groups go on the chart 

chart_checks = []
percentages = {"orphaned": [], "control": []}

print()
print("Percentage of pages MISSING each protection: ")
for check in CHECK_NAMES:
    summary = {"check": check}
    for group_name in groups:
        missing = 0
        judged = 0
        for row in page_rows:
            if row["group"] == group_name and row[check] is not None:
                judged = judged + 1
                if row[check] == True:
                    missing = missing + 1
        if judged > 0:
            summary[group_name + " (%)"] = round(100 * missing / judged)
        else: 
            summary[group_name + " (%)"] = "n/a"
        summary[group_name + " pages judged"] = judged
    summary_rows.append(summary)
    
    if summary["orphaned (%)"] == "n/a" or summary["control (%)"] == "n/a":
        print(" " + check + ": no cookies to judge")
    else:
        chart_checks.append(check)
        percentages["orphaned"].append(summary["orphaned (%)"])
        percentages["control"].append(summary["control (%)"])
        print(" " + check + ": orphaned " + str(summary["orphaned (%)"]) + "%, control " + str(summary["control (%)"]) + "%")
        
common.write_rows(os.path.join(common.REPORTS_FOLDER, "security_summary.csv"), summary_rows, ["check", "orphaned (%)", "orphaned pages judged", "control (%)", "control pages judged"])

# Draw  the side-by-side chart 

ORPHAN_COLOUR = "#eb6834" # orange
CONTROL_COLOUR = "2a78d6" # blue
BAR_WIDTH = 0.38

figure, axes = plt.subplots(figsize = (10, 5))

# WOrk out where each pair of bars goes

orphan_positions = []
control_positions = []
for index in range(len(chart_checks)):
    orphan_positions.append(index - BAR_WIDTH / 2)
    control_positions.append(index + BAR_WIDTH / 2)
    
axes.bar(orphan_positions, percentages["orphaned"], BAR_WIDTH, color=ORPHAN_COLOUR, label="Orphaned pages")
axes.bar(control_positions, percentages["control"], BAR_WIDTH, color=ORPHAN_COLOUR, label="Control(maintained home pages)")

axes.set_xticks(range(len(chart_checks)))
axes.set_xticklabels(chart_checks, rotation=30, ha="right")
axes.set_ylabel("Pages missing the protection (%)")
axes.set_ylim(0, 105)
axes.set_title("Missing security protections: orphaned against maintained pages")
axes.legend()
axes.spines["top"].set_visible(False)
axes.spines["right"].set_visible(False)
figure.tight_layout()

output_path = os.path.join(common.REPORTS_FOLDER, "security_headers.png")
figure.savefig(output_path, dpi=150)
print()
print("Saved " + output_path)