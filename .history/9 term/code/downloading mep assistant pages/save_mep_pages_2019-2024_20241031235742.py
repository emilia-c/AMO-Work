import asyncio
import aiohttp
import aiofiles
import json
import os
import urllib.parse  # For encoding URL components
from wayback import WaybackClient
from tqdm import tqdm  # Import tqdm for progress bar

# 1. SET-UP
# Load MEP data from JSON
json_path = "C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/9 term/raw data/merged_mep_9term.json"
print(f"Loading MEP data from: {json_path}")
try:
    with open(json_path, "r", encoding="utf-8") as f:
        meps_data = json.load(f)
    print(f"Loaded {len(meps_data)} MEPs successfully.")
except Exception as e:
    print(f"Failed to load MEP data: {e}")
    exit(1)

# Sort the entries alphabetically by 'mep_name'
sorted_meps = sorted(meps_data, key=lambda x: x['mep_name'])

# Directory to save all downloaded MEP pages
save_dir = "mep_assistant_pages"
os.makedirs(save_dir, exist_ok=True)

# Log file to keep track of errors
error_log = os.path.join(save_dir, "download_errors.log")

# Base URL pattern with MEP ID, Name, and the specific /assistants page
base_url = "https://www.europarl.europa.eu/meps/en/{}/{}/assistants#mep-card-content"

# Date range for snapshots
start_date = "20191010"
end_date = "20240330"

async def fetch_snapshot(session, client, mep_id, mep_name, save_path):
    """Fetch MEP page snapshot asynchronously."""
    url = base_url.format(mep_id, urllib.parse.quote(mep_name, safe="+"))
    print(f"Generated URL: {url}")  # Print the generated URL
    retries = 3  # Number of retries if download fails
    success = False

    for attempt in range(1, retries + 1):
        try:
            # Fetch snapshots from the Wayback Machine
            snapshots = list(client.search(url, from_date=start_date, to_date=end_date))
            if not snapshots:
                raise Exception(f"No snapshots found for {url}")

            # Get the most recent snapshot URL
            snapshot_url = snapshots[0].raw_url  # This will be in the format of the Wayback Machine
            archive_url = f"https://web.archive.org/web/{snapshot_url.split('/')[-2]}/{url.split('#')[0]}"
            print(f"Snapshot archive URL: {archive_url}")  # Print the snapshot archive URL

            # Fetch the snapshot page
            async with session.get(archive_url) as response:
                response.raise_for_status()
                content = await response.text()

                # Save to file
                file_path = os.path.join(save_path, f"{mep_name}.html")  # Save as MEP name instead of ID
                async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                    await f.write(content)

                success = True
                print(f"Downloaded successfully: {mep_name} (ID: {mep_id})")
                break  # Exit retry loop on success

        except Exception as e:
            print(f"Error on attempt {attempt} for {mep_name} (ID: {mep_id}): {e}")

            # Log error on last attempt
            if attempt == retries:
                async with aiofiles.open(error_log, 'a') as log:
                    await log.write(f"Failed to download {mep_name} (ID: {mep_id}) after {retries} attempts.\n")

            # Wait a bit before retrying
            await asyncio.sleep(2)  # Adjust if needed

async def main():
    client = WaybackClient()
    total_meps = len(sorted_meps)  # Total number of MEPs to download
    print(f"Total MEPs to process: {total_meps}")

    async with aiohttp.ClientSession() as session:
        tasks = []

        # Using tqdm for progress bar
        with tqdm(total=total_meps, desc="Downloading MEPs", unit="MEP") as pbar:
            for mep in sorted_meps:
                mep_id = mep["mep_id"]
                mep_name = mep["mep_name"].replace('/', '-')  # Ensure the MEP name is filesystem-friendly

                # Prepare save directory for the current MEP
                save_path = os.path.join(save_dir, mep_name)  # Save folder with MEP name
                os.makedirs(save_path, exist_ok=True)

                # Create a task for fetching this MEP's snapshot
                task = fetch_snapshot(session, client, mep_id, mep_name, save_path)
                tasks.append(task)

                # Update the progress bar
                pbar.set_postfix({"Current MEP": mep_name})
                pbar.update(1)

                # Wait between downloads to respect Wayback Machine rate limits
                await asyncio.sleep(10)  # Adjust delay as needed

            # Run all tasks concurrently
            await asyncio.gather(*tasks)

# Run the main async function
asyncio.run(main())

print("Download completed. Check error log for any failed downloads.")