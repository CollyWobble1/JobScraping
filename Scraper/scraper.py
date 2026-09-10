"""
Scraper logic for TimesJobs.com.

Single combined pass (scrape_all):

  For each search-results page:
    For each job card on that page:
      - If we've already fully scraped this URL, skip it (fast, no page load).
      - Otherwise, visit the job's own detail page immediately, extract
        skills + scan the description for keywords, and save the complete
        row (card fields + skills + keywords) in one go.

Everything is written to config.FINAL_CSV one row at a time (see append_row),
and any URL already present in that CSV is skipped on startup. This means:

  - A crash, closed laptop, or Ctrl+C loses at most the single job in
    progress, never the whole run.
  - Rerunning the script after an interruption automatically resumes instead
    of starting over or duplicating rows.

STALL DETECTION:

  If a full search-results page produces zero NEW completed jobs — whether
  because it had no cards at all, or because every card on it was a
  duplicate we'd already scraped — that counts toward
  config.NO_NEW_JOBS_PAGE_LIMIT. After several such pages in a row, the run
  stops automatically. This is what catches a broken pagination parameter
  (the site silently re-serving the same page over and over) rather than
  looping through hundreds of pages finding nothing new.

SELECTOR NOTES (why the CSS selectors below look the way they do):

  - Search cards are `div.srp-card`. Confirmed directly from TimesJobs HTML.
  - Skills on the DETAIL page use a distinctive Tailwind class combination
    (`span.border.mr-1.rounded-full.px-3.py-1.text-xs.mb-2.inline-block`)
    rather than a wrapping container class, because the obvious wrapping div
    (`div.mt-2`) turned out to be too generic and matched unrelated elements
    on the page. Selecting the spans directly by their full class signature
    was more reliable.
  - Job descriptions are read from `div.rtd-content` first, but fall back to
    the whole page's visible body text if that container isn't found or is
    empty. This fallback exists because keyword matching only needs *some*
    text to scan — it degrades gracefully instead of failing outright if
    TimesJobs changes this specific container's markup.
  - The search-results PAGINATION parameter (currently `sequence=` /
    `startPage=` in the URL) has NOT been confirmed against the live site
    and is a likely source of bugs — see README "Known fragile points".

If TimesJobs changes its page layout, the most likely breakage point is one
of these selectors. Symptom: skills or keywords come back empty for many
jobs in a row (the CONSECUTIVE_SKILL_FAILURE_LIMIT safeguard stops the run
automatically rather than burning hours on bad data). Fix by re-inspecting a
live job page (right-click -> Inspect) and updating the relevant selector in
this file.
"""

import csv
import os
import re
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import config


# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------

def log(msg: str) -> None:
    """Print a timestamped message and append it to the log file."""
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    with open(config.LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_existing_urls(csv_path: str, url_field: str = "URL") -> set:
    """Return the set of URLs already present in a CSV, for resume/dedup."""
    if not os.path.exists(csv_path):
        return set()
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row[url_field] for row in reader if row.get(url_field)}


def append_row(csv_path: str, fieldnames: list, row: dict) -> None:
    """Append a single row to a CSV, writing the header first if the file is new."""
    file_exists = os.path.exists(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def find_matched_keywords(text: str, keyword_list: list) -> str:
    """
    Return a comma-separated string of keywords found in `text`, matched as
    whole words only (so "Go" won't match inside "Google", "Unity" won't
    match inside "opportunity", etc.).
    """
    text_lower = text.lower()
    matched = []
    for kw in keyword_list:
        pattern = r'\b' + re.escape(kw.lower()) + r'\b'
        if re.search(pattern, text_lower):
            matched.append(kw)
    return ", ".join(matched)


def new_driver() -> webdriver.Chrome:
    """Launch a visible Chrome window with sane defaults for this scraper."""
    options = Options()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)


def extract_card_fields(card) -> dict:
    """Pull the basic fields off a single search-result card element."""
    item = {}

    try:
        item["URL"] = card.find_element(By.CSS_SELECTOR, 'a[target="_blank"]').get_attribute("href")
    except Exception:
        item["URL"] = ""

    try:
        item["Job_Title"] = card.find_element(By.TAG_NAME, "h2").text.strip()
    except Exception:
        item["Job_Title"] = ""

    try:
        item["Company_Name"] = card.find_element(
            By.CSS_SELECTOR, "div.text-xs.text-gray-400 span"
        ).text.strip()
    except Exception:
        item["Company_Name"] = ""

    try:
        item["Location"] = card.find_element(
            By.XPATH, './/span[.//i[contains(@class,"locations-icon")]]'
        ).text.strip()
    except Exception:
        item["Location"] = ""

    try:
        item["Experience"] = card.find_element(
            By.XPATH, './/span[.//i[contains(@class,"years-icon")]]'
        ).text.strip()
    except Exception:
        item["Experience"] = ""

    try:
        item["Salary"] = card.find_element(
            By.XPATH, './/span[.//i[contains(@class,"salary-icon")]]/following-sibling::span'
        ).text.strip()
    except Exception:
        item["Salary"] = ""

    return item


def extract_detail_fields(driver) -> dict:
    """
    Assumes driver is already on a job's detail page. Returns skills and
    matched keywords extracted from the currently loaded page.
    """
    try:
        skill_elements = driver.find_elements(
            By.CSS_SELECTOR,
            "span.border.mr-1.rounded-full.px-3.py-1.text-xs.mb-2.inline-block"
        )
        skills = ", ".join(el.text.strip() for el in skill_elements if el.text.strip())
    except Exception:
        skills = ""

    try:
        desc_elements = driver.find_elements(By.CSS_SELECTOR, "div.rtd-content")
        description_text = " ".join(el.text for el in desc_elements)
        if not description_text.strip():
            raise ValueError("empty description container")
    except Exception:
        description_text = driver.find_element(By.TAG_NAME, "body").text

    keywords = find_matched_keywords(description_text, config.KEYWORDS_TO_FLAG)

    return {"Skills_Required": skills, "Matched_Keywords": keywords}


def scrape_detail_in_new_tab(driver, job_url: str) -> dict:
    """
    Open a job's detail page in a new tab, scrape it, close the tab, and
    switch back to the original tab. This is used (rather than driver.get()
    in the same tab + driver.back()) specifically because TimesJobs'
    pagination is JavaScript-driven with no URL change — navigating away in
    the same tab and going "back" would just reload the original search URL
    from scratch and silently reset pagination to page 1. Opening a new tab
    leaves the results-list tab's state completely untouched.
    """
    original_window = driver.current_window_handle

    driver.execute_script("window.open(arguments[0], '_blank');", job_url)
    new_window = [w for w in driver.window_handles if w != original_window][-1]
    driver.switch_to.window(new_window)

    time.sleep(config.BETWEEN_DETAIL_DELAY)
    detail_fields = extract_detail_fields(driver)

    driver.close()
    driver.switch_to.window(original_window)

    return detail_fields


def get_first_card_signature(driver) -> str:
    """
    Return a small fingerprint of the currently-displayed first job card
    (its detail-page URL). Used to detect whether clicking "next" actually
    changed the results, since TimesJobs paginates via JavaScript and the
    page URL itself never changes.
    """
    try:
        first_card = driver.find_element(By.CSS_SELECTOR, "div.srp-card")
        return first_card.find_element(By.CSS_SELECTOR, 'a[target="_blank"]').get_attribute("href")
    except Exception:
        return ""


def click_next_page(driver) -> bool:
    """
    Click the "next page" button and wait for the results to actually
    change. Returns True if the click happened and content changed, False
    if there's no next button, it's disabled, or the click didn't do
    anything (e.g. we're on the last page).
    """
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "button.pagination-next")
    except Exception:
        return False  # no next button at all — likely the last page

    if not next_button.is_enabled():
        return False  # button present but disabled — last page

    before_signature = get_first_card_signature(driver)

    try:
        next_button.click()
    except Exception:
        return False  # click failed for some reason (covered by overlay, etc.)

    # Wait for the first card's URL to differ from before, meaning new
    # results actually loaded in. Poll instead of a single fixed sleep,
    # since we don't know exactly how long the JS update will take.
    max_wait = config.PAGE_LOAD_WAIT_SECONDS
    poll_interval = 0.5
    waited = 0.0
    while waited < max_wait:
        time.sleep(poll_interval)
        waited += poll_interval
        after_signature = get_first_card_signature(driver)
        if after_signature and after_signature != before_signature:
            return True  # content genuinely changed

    return False  # timed out without the content changing — treat as stalled


# ---------------------------------------------------------------------------
# Main combined scrape
# ---------------------------------------------------------------------------

def scrape_all(keyword: str = None, max_pages: int = None) -> None:
    """
    Crawl TimesJobs search results for `keyword`, paginating by clicking the
    "Next" button (TimesJobs loads new results via JavaScript rather than
    distinct page URLs). For every job card found that isn't already fully
    saved, immediately visit its detail page, extract skills + keywords, and
    save the complete row to config.FINAL_CSV.

    Stops early if several consecutive pages in a row yield zero new
    completed jobs, or clicking "next" stops changing the results
    (config.NO_NEW_JOBS_PAGE_LIMIT) — or if many detail pages in a row come
    back with no skills found (config.CONSECUTIVE_SKILL_FAILURE_LIMIT).
    """
    keyword = keyword or config.SEARCH_KEYWORD
    max_pages = max_pages or config.MAX_PAGES

    driver = new_driver()
    already_done = load_existing_urls(config.FINAL_CSV)
    log(f"Resuming with {len(already_done)} jobs already fully saved" if already_done
        else "Starting fresh scrape")

    consecutive_no_new_pages = 0
    consecutive_skill_failures = 0

    try:
        search_url = (
            "https://www.timesjobs.com/job-search"
            f"?searchType=personalizedSearch&from=submit&txtKeywords={keyword.replace(' ', '+')}"
        )
        driver.get(search_url)

        try:
            WebDriverWait(driver, config.PAGE_LOAD_WAIT_SECONDS).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.srp-card"))
            )
        except Exception:
            log("No cards found on the initial search page — check the search URL or your connection.")
            return

        for page_num in range(1, max_pages + 1):
            cards = driver.find_elements(By.CSS_SELECTOR, "div.srp-card")

            # Read off basic fields for every card on this page BEFORE
            # navigating away to any detail pages (card elements go stale
            # the moment we call driver.get() again).
            card_items = [extract_card_fields(card) for card in cards]

            new_on_this_page = 0

            for item in card_items:
                job_url = item.get("URL")

                if not job_url or job_url in already_done:
                    continue  # duplicate / already scraped / no link found — skip, no page load

                detail_fields = scrape_detail_in_new_tab(driver, job_url)
                item.update(detail_fields)

                append_row(config.FINAL_CSV, config.FINAL_FIELDS, item)
                already_done.add(job_url)
                new_on_this_page += 1

                if detail_fields["Skills_Required"]:
                    consecutive_skill_failures = 0
                else:
                    consecutive_skill_failures += 1

                status = "OK" if detail_fields["Skills_Required"] else "EMPTY"
                log(f"  [{len(already_done)}] {item['Job_Title'][:50]} -> "
                    f"skills: {status}, keywords: {detail_fields['Matched_Keywords'] or 'none'}")

                if consecutive_skill_failures >= config.CONSECUTIVE_SKILL_FAILURE_LIMIT:
                    log(f"{config.CONSECUTIVE_SKILL_FAILURE_LIMIT} consecutive empty skill results — "
                        "likely blocked or page layout changed. Stopping.")
                    return  # bail out of the whole function, not just this page

            log(f"Page {page_num}: found {len(cards)} cards, {new_on_this_page} newly scraped, "
                f"total saved: {len(already_done)}")

            if new_on_this_page == 0:
                consecutive_no_new_pages += 1
                log(f"  (no new jobs on this page — {consecutive_no_new_pages}/"
                    f"{config.NO_NEW_JOBS_PAGE_LIMIT} stalled pages in a row)")
                if consecutive_no_new_pages >= config.NO_NEW_JOBS_PAGE_LIMIT:
                    log("Hit stall limit — pagination may be stuck, or we've reached the end "
                        "of real results. Stopping.")
                    break
            else:
                consecutive_no_new_pages = 0

            if page_num < max_pages:
                clicked = click_next_page(driver)
                if not clicked:
                    log("Could not advance to the next page (no button, disabled, or content "
                        "didn't change) — assuming end of results. Stopping.")
                    break

            time.sleep(config.BETWEEN_PAGE_DELAY)

    finally:
        driver.quit()

    log(f"Scrape finished. Total jobs saved: {len(already_done)}")
