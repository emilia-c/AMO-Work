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
JSON_PATH = "C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/9 term/raw data/merged_mep_9term.json"
SAVE_DIR = "mep_assistant_pages_htmls"
ERROR_LOG = os.path.join(SAVE_DIR, "download_errors.log")
BASE_URL = "https://www.europarl.europa.eu/meps/en/{}/{}/assistants"
START_DATE = "20190716"
END_DATE = "20240710"
RETRIES = 3
DELAY_BETWEEN_DOWNLOADS = 5  # seconds
#TEST_MEP_COUNT = 5  # Number of MEPs to test with
CONCURRENCY_LIMIT = 5  # Limit on concurrent downloads

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
    # Remove special characters and convert to uppercase
    formatted_name = unidecode.unidecode(mep_name).upper()
    
    # Replace spaces between first names with plus signs and between first and last names with underscores
    if ' ' in formatted_name:
        name_parts = formatted_name.split()
        # Join first names with '+' and the rest with '_'
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
                print(f"Processing result: {result}")

                if hasattr(result, 'timestamp'):
                    try:
                        # Extract date in YYYYMMDD format
                        snapshot_date = result.timestamp.strftime('%Y%m%d')
                        # Store full timestamped URL
                        full_url = result.raw_url
                        
                        if snapshot_date not in snapshots_by_day:
                            snapshots_by_day[snapshot_date] = []
                        snapshots_by_day[snapshot_date].append(full_url)  # Append URL to the list
                    except Exception as e:
                        print(f"Error formatting timestamp: {e}")
                        continue  # Skip this result if we can't process it
                else:
                    print("No timestamp found in result.")
                    continue  # Skip if timestamp does not exist

            # Flatten the list of URLs by day
            snapshots = [url for urls in snapshots_by_day.values() for url in urls]
        else:
            print("No snapshots found for the given date range.")
    except Exception as e:
        print(f"Error fetching snapshots for date range {from_date} to {to_date}: {e}")

    return snapshots

# Main Download Function
async def fetch_snapshot(session, client, mep_id, mep_name, save_path, semaphore):
    """Fetch MEP page snapshot asynchronously using Wayback Machine snapshots."""
    formatted_name = format_mep_name(mep_name)
    url = BASE_URL.format(mep_id, urllib.parse.quote(formatted_name, safe="+"))
    print(f"Generated URL: {url}")

    snapshot_urls = get_wayback_snapshots(client, url, START_DATE, END_DATE)
    
    async with semaphore:
        for snapshot_url in snapshot_urls:
            try:
                async with session.get(snapshot_url) as response:
                    if response.status == 200:
                        content = await response.text()

                        # Save HTML file
                        html_file_path = os.path.join(save_path, f"{formatted_name}.html")
                        async with aiofiles.open(html_file_path, 'w', encoding='utf-8') as f:
                            await f.write(content)

                        # Save snapshot info to text file
                        snapshot_info_path = os.path.join(save_path, "snapshot_info.txt")
                        async with aiofiles.open(snapshot_info_path, 'w', encoding='utf-8') as f:
                            await f.write(f"Snapshot URL: {snapshot_url}\n")

                        print(f"Downloaded successfully: {mep_name} (ID: {mep_id})")
                        return snapshot_url, url
                    else:
                        print(f"No data at archive URL {snapshot_url}, status {response.status}")
            except Exception as e:
                print(f"Error accessing archive URL for {mep_name} (ID: {mep_id}): {e}")

        # Log failed downloads
        async with aiofiles.open(ERROR_LOG, 'a') as log:
            await log.write(f"Failed to download {mep_name} (ID: {mep_id}).\n")

    return None, None

async def download_meps(meps_data):
    """Download MEP snapshots for all MEPs in the provided data."""
    # total_meps = min(len(meps_data), TEST_MEP_COUNT)  # Remove this line to process all MEPs
    total_meps = len(meps_data)  # Now it processes all MEPs
    print(f"Total MEPs to process: {total_meps}")

    create_save_directory(SAVE_DIR)
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    async with aiohttp.ClientSession(trust_env=True) as session:
        client = WaybackClient()
        tasks = []

        with tqdm(total=total_meps, desc="Downloading MEPs", unit="MEP") as pbar:
            for mep in meps_data:  # Change here to loop through all MEPs
                mep_id = mep["mep_id"]
                mep_name = mep["mep_name"]
                save_path = os.path.join(SAVE_DIR, mep_name.replace('/', '-'))  # Create safe directory name
                os.makedirs(save_path, exist_ok=True)

                task = fetch_snapshot(session, client, mep_id, mep_name, save_path, semaphore)
                tasks.append(task)
                await asyncio.sleep(DELAY_BETWEEN_DOWNLOADS)  # Adjust delay between requests

            # Gather tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Update progress bar
            for result, mep in zip(results, meps_data):  # Update this line as well
                archive_url, original_url = result if isinstance(result, tuple) else (None, None)
                if archive_url:
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