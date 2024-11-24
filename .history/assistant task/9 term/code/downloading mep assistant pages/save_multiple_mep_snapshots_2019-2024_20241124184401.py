import os
import json
import urllib.parse  # For encoding URL components
import asyncio
import aiohttp
import aiofiles
from wayback import WaybackClient
from tqdm import tqdm  # Import tqdm for progress bar
from datetime import datetime
import unidecode  # To handle special character removal

# Constants
JSON_PATH = "C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/9 term/raw data/mep names/merged_mep_9term.json"
SAVE_DIR = "mep_assistant_mutiple_pages_htmls"
ERROR_LOG = os.path.join(SAVE_DIR, "download_errors_multiple_snapshots.log")
BASE_URL = "https://www.europarl.europa.eu/meps/en/{}/{}/assistants"
START_DATE = "20190716"
END_DATE = "20240710"
RETRIES = 3
DELAY_BETWEEN_DOWNLOADS = 5  # seconds
CONCURRENCY_LIMIT = 5  # Limit on concurrent downloads
TEST_MEP_COUNT = 5

# Utility Functions
async def load_mep_data(json_path):
    """Load MEP data from a JSON file."""
    print(f"Loading MEP data from: {json_path}")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            meps_data = json.load(f)
        print(f"Loaded {len(meps_data)} MEPs successfully.")
        return meps_data
    except Exception as e:
        print(f"Failed to load MEP data: {e}")
        exit(1)

def create_save_directory(save_dir):
    """Create the directory to save downloaded MEP pages."""
    os.makedirs(save_dir, exist_ok=True)

def format_mep_name(mep_name):
    """Format MEP name for URL use: remove special characters and format spaces."""
    formatted_name = unidecode.unidecode(mep_name).upper()
    
    if ' ' in formatted_name:
        name_parts = formatted_name.split()
        formatted_name = '+'.join(name_parts[:-1]) + '_' + name_parts[-1]
        
    return formatted_name

def get_wayback_snapshots(client, base_url, from_date, to_date):
    """Fetch unique daily snapshots from Wayback Machine for a given URL within a date range."""
    snapshots = []
    from_date_dt = datetime.strptime(from_date, "%Y%m%d")
    to_date_dt = datetime.strptime(to_date, "%Y%m%d")

    try:
        print(f"Fetching snapshots for {base_url} from {from_date_dt} to {to_date_dt}...")
        results = list(client.search(base_url, from_date=from_date_dt, to_date=to_date_dt))
        
        print(f"Total snapshots found: {len(results)}")
        
        if results:
            snapshots_by_day = {}
            for result in results:
                if hasattr(result, 'timestamp'):
                    try:
                        snapshot_date = result.timestamp.strftime('%Y%m%d')
                        full_url = result.raw_url
                        if snapshot_date not in snapshots_by_day:
                            snapshots_by_day[snapshot_date] = []
                        snapshots_by_day[snapshot_date].append(full_url)
                    except Exception as e:
                        print(f"Error formatting timestamp: {e}")
                        continue
                else:
                    continue

            snapshots = [url for urls in snapshots_by_day.values() for url in urls]
        else:
            print("No snapshots found for the given date range.")
    except Exception as e:
        print(f"Error fetching snapshots for date range {from_date} to {to_date}: {e}")

    return snapshots

# Main Download Function
async def fetch_snapshots(session, client, mep_id, mep_name, save_path, semaphore):
    """Fetch all MEP page snapshots asynchronously using Wayback Machine snapshots."""
    formatted_name = format_mep_name(mep_name)
    url = BASE_URL.format(mep_id, urllib.parse.quote(formatted_name, safe="+"))
    print(f"Generated URL: {url}")

    snapshot_urls = get_wayback_snapshots(client, url, START_DATE, END_DATE)
    downloaded_count = 0

    async with semaphore:
        for snapshot_url in snapshot_urls:
            try:
                async with session.get(snapshot_url) as response:
                    if response.status == 200:
                        content = await response.text()

                        # Save HTML file with unique timestamp in the name
                        snapshot_date = snapshot_url.split("/")[-2]  # Extract date from snapshot URL
                        html_file_path = os.path.join(save_path, f"{formatted_name}_{snapshot_date}.html")
                        async with aiofiles.open(html_file_path, 'w', encoding='utf-8') as f:
                            await f.write(content)

                        # Append snapshot info to text file
                        snapshot_info_path = os.path.join(save_path, "snapshot_info.txt")
                        async with aiofiles.open(snapshot_info_path, 'a', encoding='utf-8') as f:
                            await f.write(f"Snapshot URL: {snapshot_url}\n")

                        print(f"Downloaded snapshot for {mep_name} (ID: {mep_id}): {snapshot_url}")
                        downloaded_count += 1
                    else:
                        print(f"No data at archive URL {snapshot_url}, status {response.status}")
            except Exception as e:
                print(f"Error accessing archive URL for {mep_name} (ID: {mep_id}): {e}")

        if downloaded_count == 0:
            async with aiofiles.open(ERROR_LOG, 'a') as log:
                await log.write(f"Failed to download any snapshots for {mep_name} (ID: {mep_id}).\n")

    return downloaded_count

async def download_meps(meps_data):
    """Download MEP snapshots for all MEPs in the provided data."""
    total_meps = min(len(meps_data), TEST_MEP_COUNT)  # Remove this line to process all MEPs
    #total_meps = len(meps_data)
    print(f"Total MEPs to process: {total_meps}")

    create_save_directory(SAVE_DIR)
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    async with aiohttp.ClientSession(trust_env=True) as session:
        client = WaybackClient()
        tasks = []

        with tqdm(total=total_meps, desc="Downloading MEPs", unit="MEP") as pbar:
            for mep in meps_data:
                mep_id = mep["mep_id"]
                mep_name = mep["mep_name"]
                save_path = os.path.join(SAVE_DIR, mep_name.replace('/', '-'))
                os.makedirs(save_path, exist_ok=True)

                task = fetch_snapshots(session, client, mep_id, mep_name, save_path, semaphore)
                tasks.append(task)
                await asyncio.sleep(DELAY_BETWEEN_DOWNLOADS)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result, mep in zip(results, meps_data):
                if isinstance(result, int) and result > 0:
                    pbar.set_postfix({"Current MEP": mep["mep_name"]})
                    pbar.update(1)
                else:
                    print(f"Failed to retrieve URLs for {mep['mep_name']}.")

# Main entry point
async def main():
    meps_data = await load_mep_data(JSON_PATH)
    sorted_meps = sorted(meps_data, key=lambda x: x['mep_name'])
    await download_meps(sorted_meps)

if __name__ == "__main__":
    asyncio.run(main())
    print("Download completed. Check error log for any failed downloads.")
