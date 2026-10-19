"""
ads_biface_database_scraper.py

Summary:
    This script scrapes biface artifact records from https://archaeologydataservice.ac.uk/archives/view/bifaces (Lower Palaeolithic technology, raw material and population ecology (bifaces)
Gilbert Marshall, David Dupplaw, Derek Roe, Clive Gamble, 2002. https://doi.org/10.5284/1000354).
    For each record ID, it downloads the artifact's metadata and associated images (front, side, rear views),
    saving the data to a CSV file and images to a local directory. The script includes logging, error handling,
    and periodic saving of progress to ensure robustness during long scraping sessions.

Author: Juan Francisco Palomeque-Gonzalez
Year: 2025
"""
import os
import requests
import time
import logging
from bs4 import BeautifulSoup
import pandas as pd

# Setup directories and logging
os.makedirs("images", exist_ok=True)
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/processing_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding='utf-8'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

# Configuration
IDs = [i for i in range(29, 3589) if i not in (48, 551, 552, 3453)]
START_FROM_ID = 29
MAX_RETRIES = 5
THROTTLE_SECONDS = 1.5
SAVE_EVERY = 10  # Save to CSV every N records
OUTPUT_FILE = "biface_records_online.csv"
FAILED_IDS_FILE = "logs/failed_ids.txt"

def extract_fields_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    detail_rows = soup.select("div#archive table.sctab tr")
    record = {}
    
    for row in detail_rows:
        cells = row.find_all('td')
        if len(cells) == 2:
            key = cells[0].get_text(strip=True).replace(":", "")
            value = cells[1].get_text(strip=True)
            record[key] = value
        
    return record

def download_image(id_, view_suffix):
    filename = f"{id_}{view_suffix}.jpg"
    local_path = os.path.join("images", filename)

    if os.path.exists(local_path):
        logging.info(f"Skipped image (already exists): {filename}")
        return

    img_url = f"https://archaeologydataservice.ac.uk/catalogue/adsdata/arch-349-1/dissemination/jpg/{filename}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(img_url, timeout=10)
            if response.status_code == 200:
                with open(local_path, "wb") as f:
                    f.write(response.content)
                logging.info(f"Downloaded image: {filename}")
                print('Sleeping for throttle...')
                time.sleep(THROTTLE_SECONDS)
                return
            else:
                logging.warning(f"Image {filename} not found (HTTP {response.status_code}), {img_url}")
                return
        except Exception as e:
            logging.error(f"Attempt {attempt} failed for image {filename}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(1)
            else:
                logging.error(f"Image {filename} failed after {MAX_RETRIES} attempts")

def process_ids(ids, start_from=0):
    base_url = "https://archaeologydataservice.ac.uk/archives/view/bifaces/bf_full_record.cfm?bf_id={}"
    records = []
    failed_ids = []

    ids = [i for i in ids if i >= start_from]
    total = len(ids)

    for count, id_ in enumerate(ids, start=1):
        logging.info(f"\nProcessing ID {id_} ({count} of {total})")

        success = False
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.get(base_url.format(id_), timeout=15)
                if response.status_code == 200:
                    record = extract_fields_from_html(response.text)
                    record["Record ID"] = id_
                    records.append(record)

                    for suffix in ['f', 's', 'r']:
                        download_image(id_, suffix)

                    success = True
                    print('Sleeping for throttle...')
                    time.sleep(THROTTLE_SECONDS)
                    break  # Success, exit retry loop
                else:
                    logging.warning(f"Failed to fetch ID {id_}: HTTP {response.status_code}, {base_url.format(id_)}")
                    break
            except Exception as e:
                logging.error(f"Attempt {attempt} failed for ID {id_}: {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(1)

        if not success:
            logging.error(f"ID {id_} failed after {MAX_RETRIES} attempts")
            failed_ids.append(id_)

        if count % SAVE_EVERY == 0:
            pd.DataFrame(records).to_csv(OUTPUT_FILE, index=False)
            with open(FAILED_IDS_FILE, "a") as f:
                for fid in failed_ids:
                    f.write(str(fid) + "\n")
            failed_ids.clear()
            logging.info(f"Saved progress after {count} records")

        time.sleep(THROTTLE_SECONDS) 

    # Final save
    pd.DataFrame(records).to_csv(OUTPUT_FILE, index=False)
    with open(FAILED_IDS_FILE, "a") as f:
        for fid in failed_ids:
            f.write(str(fid) + "\n")

    logging.info("Finished processing all IDs.")
    return pd.DataFrame(records)

# Example usage:
# df = process_ids(IDs, start_from=START_FROM_ID)
if __name__ == "__main__":
    df = process_ids(IDs, start_from=START_FROM_ID)
    logging.info(f"Total records processed: {len(df)}")
    logging.info(f"Data saved to {OUTPUT_FILE}")
    logging.info(f"Failed IDs logged in {FAILED_IDS_FILE}")
    print(f"Total records processed: {len(df)}")
    print(f"Data saved to {OUTPUT_FILE}")
    print(f"Failed IDs logged in {FAILED_IDS_FILE}")
    df.head()  # Display the first few records for verification
    df.info()  # Display DataFrame info for verification
    df.describe()  # Display summary statistics for numerical fields
    df.to_csv(OUTPUT_FILE, index=False)  # Ensure final save
    logging.info("Script execution completed successfully.")