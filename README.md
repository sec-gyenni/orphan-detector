# Orphaned Page Detector 

A reproduction of the method in:

Pletinckx, S., Borgolte, K and Fiebig, T. (2021) 'Out of sight, out of mind: detecting orphaned web pages at internet-scale', CSS '21, pp. 21-35. doi:10.1145/3460120.3485367

An **orphaned page** is a page that is still online but no longer linked from anywhere on its website. Nobody maintains it, so it can become a security risk. This project finds such pages by comparing old copies of a website (from the Internet Archive) with the website today.

## What you need

- Python 3.10 or newer 
- An internet connection (for installing libraries and for the real run)
- About 10MB of disk space for the test run 

The code uses three libraries: `requests`, `beautifulsoup4` and `matplotlib`.

## Setting up

### Ubuntu

```bash
sudo apt update
sudo apt install python3 python-venv python3-pip
cd orphan detector 
python3 -m venv orphan-env
source orphan-env/bin/activate
pip install -r requirements.txt
```

### macOS (including Apple Silicon)

Install Homebrew first if you do not have it (see https://brew.sh), then:

```bash
brew install python
cd orphan-detector
python3 -m venv orphan-env
source orphan-env/bin/activate
pip install -r requirements.txt
```
After this , your terminal prompt starts with `(orphan-env)`. Run `source orphan-env/bin/activate` again each time you open a new terminal

### Running on the test website (recommended first)

The test website is built on your own computer, so the correct answers are known in advance: pages 21 to 28 are the planted orphans, and six other pages are "decoys" designed to trick the detector.

1. Open `common.py` and check that `LOCAL_TEST = True`.
2. Run:

```bash
bash run_all.sh
```

This takes about 10 seconds. It builds the test site, starts a small local web server, runs every step and stops the server again.

**Expected result:** recall 100%, precision 100%, and every decoy handled as expected. Results are saved in the `reports` folder:

| File | What it shows |
|---|---|
| `accuracy.csv` | Precision, recall and what happened to each decoy |
| `funnel.png` | How many pages remain after each filtering step |
| `similarity.png` | Simhash compared with Python's difflib |
| `security_headers.png` | Missing security headers, orphans against maintained pages |

To view the test site in a browser while the server is running, go to http://localhost:8000

## Running on real websites

Please read the ethics section below before doing this.

1. In `common.py` :
   - set `LOCAL_TEST = False`
   - put your own email address in `CONTACT_EMAIL`
   - check the websites listed in `REAL_DOMAINS`
2. Run it in the background, because it is slow on purpose:

```bash
nohup bash run_real.sh > real_run.log 2>&1 &
tail -f real_run.log
```

Press `Ctrl + C` to stop watching the log (the run carries on)
Results are saved in `reports_real`.

**Our real run (November 2026)** on lua.org, openssh.com and gnuplot.info:
11,257 archived addresses were reduced to 257 sampled pages, 30 still online, and 13 labelled "likely orphaned", all on lua.org. On inspection, these were old manuals and source listings that lua.org keeps on purpose, so they are false orphans. This is discussed in the report.

### Ethics and safety

- Only public information is used: the Internet Archive and normal web requests, like a browser makes.
- Every request includes a contact email, so website owners can askk to be left out
- There is a 10-second pause between requests, and at most 40 pages are checked per website.
- No attacks are run. The security check only reads the headers that a website sends to every visitor.

## The files, in the order they run 

| File | What it does |
|---|---|
| `common.py` | Shared settings (including the `LOCAL_TEST` switch) and helper functions |
| `make_test_site.py` | Builds the "before" site and "after" versions of the test website |
| `make_local_archive.py` | Crawls the "before" site to make a pretend archive history |
| `download_history.py` | Real run only: downloads archive history from the Internet Archive |
| `find_candidates.py` | Finds pages seen in the past but not recently; drops non-page files |
| `remove_dynamic_urls.py` | Dynamic URL Detection (DUDe, the paper's Algorithm 1) |
| `limit_candidates.py` | Picks at most 40 random pages per website |
| `check_alive.py` | Keeps only pages that still answer with HTTP 200 |
| `remove_duplicates.py` | Removes fake error pages (same size) and non-HTML pages |
| `score_pages.py` | Simhash similarity and orphan score; keeps scores of 0.9 or more |
| `label_pages.py` | Labels pages likely orphaned, not orphaned or uncertain |
| `check_headers.py` | Passive check of security headers and cookie flags |
| `measure_accuracy.py` | Test site only: precision, recall and decoy results |
| `draw_funnel.py` | Funnel chart (log scale for large numbers) |
| `draw_similarity.py` | Simhash against difflib chart |
| `run_all.sh` | Runs the whole test pipeline |
| `run_real.sh` | Runs the whole real pipeline |

## Troubleshooting 

| Problem | Fix |
|---|---|
| `python: common not found` | Activate the environment: `source orphan-env/bin/activate` |
| `externally-managed-environemt` | You are outside the environment; activate it first |
| `Address already in use` | An old server is still running: `pkill -f "http.server 8000"` |
| Archive errors 503 or 504 | The Internet Archive is busy; the code waits and retries |