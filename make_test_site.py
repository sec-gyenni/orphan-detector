"""This builds a small website that we control, just so we can test the detector on pages where we already know the right answers"""

import os
import sys
import shutil
import common

# The plan for the test site

SITE_FOLDER = "site"

# Normal pages; These are pages that are always linked and kept up to date

NORMAL_PAGES = list(range(1,21)) # pages 1 to 20

# TRUE ORPHANS; These are unlinked in the "after" version, still online but never updated or accessed from main site

FORGOTTEN_PAGES = [21, 22, 23, 24, 25, 26] # an old copyright year (2019)
BLANK_TEMPLATE_PAGE = 27                   # an empty template page that was never finished
NO_YEAR_PAGE = 28                          # a copyright year with no year

# DECOYS; each one should be removed by a different step of the pipeline
DELETED_PAGE = 29                   # properly deleted. This should be deleted by the check_alive.py script
SOFT_404_PAGES = [30, 31]           # fake "not found pages". This should be deleted by the remove_duplicates.py
HIDDEN_MAINTAINED_PAGE = 32         # unlinked but kept fresh. This should be removed by the score_pages.py script
OLD_IMAGE = "image.old-logo.png"    # this is not a webpage at all. It will be removed by the find_candidates.py script

# News articles with long, automatically made addresses.
# This paper removes these on purpose with Dynamic URL Detection (DUDe)

NEWS_ARTICLES = [
    "news/archive/2019/january-new-product-range-announcement.html",
    "news/archive/2019/february-spring-sale-starts-this-week.html",
    "news/archive/2019/march-opening-hours-change-for-easter.html",
    "news/archive/2019/april-customer-survey-results-published.html",
    "news/archive/2019/may-new-delivery-partner-announced.html",
    "news/archive/2019/june-summer-collection-now-available.html",
]

# This is going to read which version build whether before or after
if len(sys.argv) >1:
    version = sys.argv[1]
else:
    version = "before"

if version != "before" and version != "after":
    print ("Please type either 'before' or 'after' the script name")
    sys.exit(1)

# These are functions that build the html for each kind of page

def make_html(title, body):
    """ This wraps a title and some body content into a complete web page"""
    return f"""<!doctype html>
<html>
<head><title>{title}</title></head>
<body>
{body}
</body>
</html>
"""

def product_page(page_number, copyright_line, extra_text):
    """ This will be the product page. Each page has a different amount of text, so that no two product page are exactly the same size"""
    filler_text = "More detail about this product." * page_number
    body = f"""<h1>Product {page_number}</p>
    <p>{filler_text}</p>
    {extra_text}
    <footer>{copyright_line}</footer>
    """
    return make_html(f"Product {page_number}", body)

def normal_page (page_number):
    """In 2019 it had the old year; today it has been updated"""
    if version == "beefore":
        return product_page(page_number, "Copyright 2026 Orphan Test Site", "")

def forgotten_page(page_number):
    """A true orphan: identical in both versions because nobody touched it."""
    return product_page(page_number, "Copyright 2019 Orphan Test Site", "")

def blank_template_page():
    """A true orphan: a template that was set up but never filled in"""
    body = """<div class="container">
    <div class="row"></div>
    </div>
    <script>"""
    return make_html("New page", body)

def no_year_page():
    """A true orphan: its copyright line has no year at all."""
    return product_page(NO_YEAR_PAGE, "&copy; Orphan test Site", "")

def soft_404_page(page_number):
    """This was a real page in 2019. Today, the server shows a "not found" message but still answers "200 OK. Both soft 404 pages are identical today, so they have exactly same size"""

    if version == "before":
        return product_page(page_number,  "Copyright 2019 Orphan Test Site", "")
    else:
        body = """<h1> Page Not Found<h1>
        <p>Sorry, this page no longer exists.</p>
        <p><a href="index.html">Return to the homepage</a></p>"""
        return make_html("Page Not Found" , body)

def hidden_maintained_page():
    """Inlinked on purpose, but the owner still keeps it up to date"""
    if version == "before":
        return product_page(HIDDEN_MAINTAINED_PAGE, "Copyright 2019 Orphan Test Site", "")
    else:
        body = """<h1>Staff Discount Portal</h1>
        <p>Welcome, team. This private page still lists this season's staff offers.</p>
        <ul>
            <li>Twenty percent off all winter coats untill the end of January.</li>
            <li>Free next-day delivery on every staff order.</li>
            <li>Extra loyalty points on weekend shifts.</li>
        </ul>
        <p>Questions? Contact people team on extensions 4410</p>
        <footer>Copyright 2019 Orphan Test Site</footer>"""
        return make_html("Staff Discount Portal", body)

def news_article(article_number, article_path):
    """An old new article, identical in both versions"""
    filler_text = "Read the full story in our newsletter." * (article_number + 2)
    body = f"""<h1>News from {article_path}</h1>
<p>{filler_text}</p>
<footer>Copyright 2019 Orphan Test Site</footer>"""
    return make_html("Company new", body)

# This decides which pages the home page links to

#Every product page number, from 1 to 32
all_page_numbers = list (range(1,33))

linked_address = []
if version == "before":
    # In 2019, the hope page linked to everything.
    for page_number in all_page_numbers:
        linked_address.append(f"page{page_number}.html")
    for article_path in NEWS_ARTICLES:
        linked_address.append(article_path)
    linked_address.append(OLD_IMAGE)
else:
    # Today the homepage only links to the normal pages
    for page_number in NORMAL_PAGES:
        linked_address.append(f"page{page_number}.html")

link_lines = ""
for address in linked_address:
    link_lines = link_lines + f' <li><a href="{address}" > {address}</a></li>\n'    

home_body = f"""<h1>Orphan Test Site</h1>
<ul>
{link_lines}</ul>"""
home_page_html = make_html("Orphan Test Site", home_body)

if os.path.exists(SITE_FOLDER):
    shutil.rmtree(SITE_FOLDER)
os.makedirs(os.path.join(SITE_FOLDER, "news", "archive", "2019"))

common.write_text_file(os.path.join(SITE_FOLDER, "index.html"), home_page_html)

# The homepage
for page_number in all_page_numbers:
    if page_number in NORMAL_PAGES:
        page_html = normal_page (page_number)
    elif page_number in FORGOTTEN_PAGES:
        page_html = forgotten_page(page_number)
    elif page_number == BLANK_TEMPLATE_PAGE:
        page_html = blank_template_page()
    elif page_number == NO_YEAR_PAGE:
        page_html = no_year_page()
    elif page_number in SOFT_404_PAGES:
        page_html = soft_404_page(page_number)
    elif page_number == HIDDEN_MAINTAINED_PAGE:
        page_html = hidden_maintained_page()
    else:
        page_html = product_page(page_number, "Copyright 2019 Orphan Test Site", "")

    # The deleted page is only written in the "before" version
    if page_number == DELETED_PAGE and version == "after":
        continue

    page_path = os.path.join(SITE_FOLDER, f"page{page_number}.html")
    common.write_text_file(page_path, page_html)

# This is going to print a short summary

print("Built '" + version + "' version of the test")
print("The home page links to " + str(len(linked_address)) + " addresses.")
if version == "after":
    print("Page " + str(DELETED_PAGE) + " has been deleted.")