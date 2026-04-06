"""
This script serves as the main entry point for the web scrapper. It scrapes the project details from the Verra registry.
"""

# ───────────────────────────────────────────────────── imports ────────────────────────────────────────────────────── #

import argparse
import csv
import time
from pathlib import Path
from typing import Optional

import pandas as pd
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from conf_mgr import conf_mgr

# ────────────────────────────────────────────────── Configuration Constants ─────────────────────────────────────── #

VERRA_BASE_URL = "https://registry.verra.org/app/projectDetail/VCS"
ELEMENT_WAIT_TIMEOUT = 5  # seconds
INTER_PROJECT_DELAY = 5  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

DOCUMENT_HEADERS = [
    "VCS Registration Documents",
    "VCS Pipeline Documents",
    "VCS Issuance Documents",
    "VCS Other Documents",
]

CSV_HEADERS = ["Project ID", "Document Type", "Document Name", "Document URL", "Date Updated"]

# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #
#                                               Web Scrapper Main Script                                               #
# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #


def setup_driver() -> webdriver.Chrome:
    """Set up and return a Chrome WebDriver instance in headless mode."""
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def validate_input_file(file_path: Path) -> bool:
    """Validate that the input Excel file exists and is readable."""
    if not file_path.exists():
        logger.error(f"Input file not found: {file_path}")
        return False
    if not file_path.is_file():
        logger.error(f"Path is not a file: {file_path}")
        return False
    return True


def scrape_summary(driver: webdriver.Chrome, element_id: str) -> Optional[str]:
    """Scrape the summary content from the page."""
    try:
        element = WebDriverWait(driver, ELEMENT_WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.CLASS_NAME, "card-text"))
        )
        return element.get_attribute("innerHTML")
    except Exception as e:
        logger.error(f"Failed to scrape summary for project {element_id}: {e}")
        return None


def save_summary(content: str, project_id: str) -> bool:
    """Save summary content to a text file."""
    try:
        output_path = conf_mgr.path_results_summary / f"{project_id}.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Failed to save summary for project {project_id}: {e}")
        return False


def extract_document_links(driver: webdriver.Chrome, project_id: str) -> list[tuple]:
    """Extract document links from the page."""
    document_links = []

    for header in DOCUMENT_HEADERS:
        try:
            found_document_group = driver.find_elements(
                By.XPATH,
                f"//div[contains(@class,'card') and .//div[contains(@class,'card-header')][contains(text(),'{header}')]]",
            )

            if len(found_document_group) != 1:
                logger.warning(
                    f"Expected 1 document group for header '{header}' in project {project_id}, "
                    f"but found {len(found_document_group)}"
                )
                continue

            group = found_document_group[0]
            pdf_links = group.find_elements(By.CSS_SELECTOR, "table tbody tr td a")
            dates = group.find_elements(By.CSS_SELECTOR, "table tbody tr td:nth-child(2)")

            for link, date in zip(pdf_links, dates):
                pdf_url = link.get_attribute("href")
                pdf_name = link.text
                date_updated = date.text

                document_links.append((project_id, header, pdf_name, pdf_url, date_updated))

        except Exception as e:
            logger.warning(f"Failed to extract documents from group '{header}' for project {project_id}: {e}")
            continue

    return document_links


def main(scrape_summary: bool = True, scrape_document_links: bool = True) -> None:
    """
    Main function to scrape project details from the Verra registry.

    Args:
        scrape_summary (bool): Flag to indicate whether to scrape project summary content. Default is True.
        scrape_document_links (bool): Flag to indicate whether to scrape project document links. Default is True.
    """

    # Validate input file
    input_file = conf_mgr.path_data / "registered.xlsx"
    if not validate_input_file(input_file):
        logger.error("Cannot proceed without valid input file")
        exit(1)

    # Load the Excel file with the project IDs and Names
    try:
        df = pd.read_excel(input_file, sheet_name="Results")
        logger.info(f"Loaded {len(df)} projects from {input_file}")
    except Exception as e:
        logger.error(f"Failed to load Excel file: {e}")
        exit(1)

    failed_ids = []
    failed_projects = []
    all_document_links = []

    # Initialize the WebDriver once for all projects
    driver = None
    try:
        driver = setup_driver()
        logger.info("WebDriver initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize WebDriver: {e}")
        exit(1)

    # Iterate over the ID and Name columns
    total_projects = len(df)
    for count, (project_id, name) in enumerate(zip(df["ID"], df["Name"]), 1):
        logger.info(f"Processing project {count}/{total_projects}: {name} (ID: {project_id})")

        url = f"{VERRA_BASE_URL}/{project_id}"

        try:
            # Navigate to the project page
            driver.get(url)

            # Scrape the summary content
            if scrape_summary:
                content = scrape_summary(driver, project_id)
                if content:
                    save_summary(content, project_id)
                    logger.debug(f"Successfully saved summary for project {project_id}")

            # Scrape the document links
            if scrape_document_links:
                links = extract_document_links(driver, project_id)
                all_document_links.extend(links)
                logger.debug(f"Extracted {len(links)} document links for project {project_id}")

        except Exception as e:
            logger.error(f"Failed to scrape {name} (ID: {project_id}). Error: {e}")
            failed_ids.append(project_id)
            failed_projects.append(name)

        # Wait before scraping the next project (to be respectful to the server)
        if count < total_projects:
            time.sleep(INTER_PROJECT_DELAY)

        logger.debug(f"Finished processing project {count}/{total_projects}")

    # Close the WebDriver after all projects are processed
    try:
        driver.quit()
        logger.info("WebDriver closed successfully")
    except Exception as e:
        logger.warning(f"Error closing WebDriver: {e}")

    # Write all document links to CSV at once
    if scrape_document_links and all_document_links:
        try:
            with open(conf_mgr.path_results_csv, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(CSV_HEADERS)
                writer.writerows(all_document_links)
            logger.info(f"Saved {len(all_document_links)} document links to {conf_mgr.path_results_csv}")
        except Exception as e:
            logger.error(f"Failed to write document links to CSV: {e}")

    # Save failed projects to CSV
    if failed_ids:
        try:
            df_failed = pd.DataFrame(
                {
                    "ID": failed_ids,
                    "Name": failed_projects,
                }
            )
            failed_file = conf_mgr.path_results / "failed_projects.csv"
            df_failed.to_csv(failed_file, index=False)
            logger.warning(f"Saved {len(failed_ids)} failed projects to {failed_file}")
        except Exception as e:
            logger.error(f"Failed to save failed projects list: {e}")

    # Final summary
    successful_projects = total_projects - len(failed_ids)
    logger.info(f"Scraping completed: {successful_projects}/{total_projects} projects processed successfully")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verra VCS Registry Scraper")
    parser.add_argument(
        "-ds",
        "--disable-summary",
        dest="disable_summary",
        action="store_true",
        help="Do not scrape project summary content",
    )
    parser.add_argument(
        "-dd",
        "--disable-document",
        dest="disable_document",
        action="store_true",
        help="Do not scrape project document links",
    )
    args = parser.parse_args()

    if args.disable_summary and args.disable_document:
        logger.error("Both summary and document scraping are disabled. Nothing to do.")
        exit(1)

    # Run the main function
    main(scrape_summary=not args.disable_summary, scrape_document_links=not args.disable_document)
