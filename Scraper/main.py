"""
Entry point for the TimesJobs scraper.

Usage:
    python main.py

By default this runs a small trial (see TRIAL_MAX_PAGES below) so you can
sanity-check the output before committing to a long/overnight run. Once
you've checked timesjobs_final.csv looks correct, switch RUN_MODE to "full"
and rerun.

To stop a run early at any time: Ctrl+C in the terminal. Progress already
written to timesjobs_final.csv is safe — nothing is lost, and rerunning will
resume from where it left off (see README.md for details).
"""

import config
import scraper

# Change to "full" once a trial run looks correct.
RUN_MODE = "trial"   # "trial" or "full"

TRIAL_MAX_PAGES = 2   # >1 so the trial can also sanity-check that pagination
                      # is actually moving to a different set of jobs, not
                      # just repeating page 1.


def main():
    if RUN_MODE == "trial":
        scraper.log("=== Running in TRIAL mode ===")
        scraper.scrape_all(keyword=config.SEARCH_KEYWORD, max_pages=TRIAL_MAX_PAGES)
    elif RUN_MODE == "full":
        scraper.log("=== Running in FULL mode ===")
        scraper.scrape_all(keyword=config.SEARCH_KEYWORD, max_pages=config.MAX_PAGES)
    else:
        raise ValueError(f"Unknown RUN_MODE: {RUN_MODE!r} (expected 'trial' or 'full')")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        scraper.log("Stopped manually by user (Ctrl+C). Progress up to this point is saved in the CSV.")
