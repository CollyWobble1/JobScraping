# TimesJobs Scraper

Scrapes job listings from [timesjobs.com](https://www.timesjobs.com), pulling
title, company, location, experience, salary, skills, and a keyword scan of
each job description (e.g. does it mention Python, AWS, Unity, etc.).

## How it works

Single combined pass (`scraper.scrape_all`): for every job card found on a
search-results page, it immediately visits that job's own detail page,
pulls the skills list, scans the description for keywords, and saves the
complete row — card fields + skills + keywords all together — before moving
to the next card. There's no separate "collect links first, scrape details
later" step; skills and keywords are gathered as part of the same pass, not
deferred to the end.

Writes to CSV **one row at a time**, and **skips anything already saved** on
startup. Practically, this means:

- A crash, a closed laptop, or a manual `Ctrl+C` never loses more than the
  one job in progress.
- You can just rerun `python main.py` after any interruption and it picks up
  where it left off — no flags or extra steps needed.

## Setup

```bash
pip install -r requirements.txt
```

You also need Google Chrome installed. Selenium 4.6+ manages the matching
chromedriver automatically — no separate download needed.

## Usage

```bash
python main.py
```

By default this runs in **trial mode** (`RUN_MODE = "trial"` in `main.py`),
scraping 2 search-results pages (~20 jobs) so you can check the output
before committing to a long run. Using 2 pages instead of 1 also lets you
confirm pagination is actually moving forward to new jobs, not silently
re-serving the same page (see "Known fragile points" below — this has
happened before).

**To do a full/overnight run:**

1. Check `timesjobs_final.csv` from the trial run looks correct (right
   fields, skills populated, keywords look sane — not matching on every
   single job, e.g. "Unity" or "Go" showing up everywhere would mean the
   keyword matcher regressed to substring matching). Also confirm the jobs
   from page 2 are genuinely different jobs from page 1, not duplicates.
2. Open `main.py` and change `RUN_MODE = "trial"` to `RUN_MODE = "full"`.
3. Run `python main.py` again.
4. Make sure your machine won't sleep mid-run (see below).

**To stop a run early:** `Ctrl+C` in the terminal. Everything written so far
is safe. Rerun the same command later to resume.

**To start completely fresh** (ignore all previously saved progress): delete
`timesjobs_final.csv` before running.

## Output files

| File | Contents |
|---|---|
| `timesjobs_final.csv` | title, company, URL, location, experience, salary, `Skills_Required`, `Matched_Keywords` — one complete row per job |
| `scrape_log.txt` | Timestamped log of every page/job processed — check this first if something looks off |

## Configuration

All tunable settings live in `config.py`, not scattered through the scraper
code:

- `SEARCH_KEYWORD` / `MAX_PAGES` — what to search for and how far to page
- `KEYWORDS_TO_FLAG` — the list scanned for in job descriptions (edit freely,
  no effect on scraping logic)
- Timing/retry settings — delays between requests, how many empty pages or
  failed detail-page scrapes to tolerate before stopping automatically

## Running overnight safely

- **Keep the laptop plugged in and set to not sleep** while plugged in
  (System Settings → Battery/Energy on Mac), otherwise the script just
  freezes when the display sleeps.
- The script already includes safeguards that stop it automatically rather
  than running all night on bad data:
  - `NO_NEW_JOBS_PAGE_LIMIT` (default 3) — stops the run if several search
    pages in a row produce **zero newly-scraped jobs**, whether because the
    page had no cards at all, or because every card on it turned out to be
    a duplicate already saved. This second case is what catches a broken
    pagination parameter (the site silently re-serving the same page over
    and over) — a real bug this scraper hit during development, where
    pagination looked like it was working (different card counts per page)
    but was actually just repeating the same ~10 jobs indefinitely.
  - `CONSECUTIVE_SKILL_FAILURE_LIMIT` (default 15) — stops the run if many
    detail pages in a row return no skills (means the site layout changed,
    or we're being blocked).
- Check `scrape_log.txt` in the morning — it tells you exactly how far it
  got and why it stopped, if it stopped early.
- Resource-wise, this is a single Chrome tab navigating pages continuously —
  CPU/network load is light, but Chrome's memory usage can creep up over a
  very long single session. If you're on a lower-RAM machine and this
  becomes an issue, consider adding a periodic driver restart (not currently
  implemented).

## Known fragile points (read this if scraping suddenly breaks)

TimesJobs' page structure isn't guaranteed to stay the same, and the
selectors below were reverse-engineered from the live site at time of
writing — not from any official API or documentation. If Skills or Matched
Keywords start coming back empty for large batches of jobs, this is the
first place to look:

- **Search cards**: `div.srp-card` — the wrapper for each listing on a
  search-results page.
- **Skills** (on the job's own detail page): matched by a specific
  Tailwind CSS class combination on the `<span>` tags themselves
  (`span.border.mr-1.rounded-full.px-3.py-1.text-xs.mb-2.inline-block`),
  not by a wrapping container. An earlier attempt used the wrapping
  `div.mt-2`, but that class is too generic (used all over the page) and
  matched unrelated elements — worth knowing if you're tempted to simplify
  the selector back to the container.
- **Description text**: `div.rtd-content`, with a fallback to the whole
  page's visible text if that specific element isn't found. The fallback
  exists because keyword-matching just needs *some* text to search — it
  doesn't need a perfectly clean extraction the way skills does.
- **Pagination**: TimesJobs loads additional results via **JavaScript**,
  not by changing the URL — clicking "next page" on the live site does not
  change the address bar at all. Pagination is done by clicking
  `button.pagination-next` and waiting for the first result to change.
  If TimesJobs changes this button's class or markup, pagination will stop
  advancing — the `NO_NEW_JOBS_PAGE_LIMIT` safeguard will catch this and
  stop the run rather than looping forever on page 1.
- **Detail pages are opened in a new browser tab**, not the same tab, and
  the tab is closed afterward before returning to the results tab. This is
  deliberate: since pagination has no URL to "go back" to, navigating away
  in the same tab and pressing back would just reload the original search
  URL from scratch and silently reset to page 1. Opening a new tab per job
  leaves the results tab's scroll/pagination state completely undisturbed.

To fix a broken selector: open a live job page in Chrome, right-click the
element in question → **Inspect**, and update the relevant selector in
`scraper.py` (see the `SELECTOR NOTES` docstring at the top of that file).

## Notes on scale

TimesJobs' search pagination will very likely run out of real, unique
results long before reaching very large numbers (tens of thousands+) of
listings for a single search term — `EMPTY_PAGE_LIMIT` is what catches this
and stops the run cleanly rather than looping on empty pages forever.

## Respecting the target site

This scraper includes deliberate delays between requests (`config.py`:
`BETWEEN_PAGE_DELAY`, `BETWEEN_DETAIL_DELAY`) to avoid hammering
timesjobs.com. Please don't remove these to "speed things up" — keep runs
reasonably paced and mindful of the site's terms of service.
