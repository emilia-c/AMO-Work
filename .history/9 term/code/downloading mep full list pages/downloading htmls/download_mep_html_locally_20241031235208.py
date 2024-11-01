import asyncio
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from wayback import WaybackClient
import random

# Set up constants
base_url = "https://www.europarl.europa.eu/meps/en/full-list/all"
start_date_str = "20210101"
end_date_str = "20240715"
cache_dir = "cache"  # Directory to store cached snapshots
meps_list = []

# Ensure cache directory exists
os.makedirs(cache_dir, exist_ok=True)

async def get_meps_from_snapshot(session, snapshot_url, snapshot_date_str):
    """Get MEP names, IDs, and date from a specific snapshot asynchronously."""
    try:
        cache_file = os.path.join(cache_dir, f"{snapshot_date_str}.html")

        # Check if the data is cached
        if os.path.exists(cache_file):
            print(f"Loading data from cache for {snapshot_date_str}")
            async with aiofiles.open(cache_file, 'r', encoding='utf-8') as f:
                text = await f.read()
        else:
            # Fetch data if not cached
            async with session.get(snapshot_url) as response:
                response.raise_for_status()
                text = await response.text()

                # Cache the fetched HTML content
                async with aiofiles.open(cache_file, 'w', encoding='utf-8') as f:
                    await f.write(text)

        # Parse the HTML content
        soup = BeautifulSoup(text, 'html.parser')
        for mep in soup.find_all("a", class_="ep_content"):
            mep_name = mep["title"].strip()
            mep_href = mep["href"]
            mep_id = mep_href.split('/')[-1]

            meps_list.append({
                "mep_id": mep_id,
                "mep_name": mep_name,
                "date_scraped": snapshot_date_str
            })
        await save_to_json(meps_list)

    except Exception as e:
        print(f"Error fetching data from {snapshot_url}: {e}")

async def save_to_json(meps_list):
    """Save the MEP list to a JSON file asynchronously."""
    json_filename = "MEPs_2021_2024.json"
    try:
        async with aiofiles.open(json_filename, 'w', encoding='utf-8') as json_file:
            await json_file.write(json.dumps(meps_list, ensure_ascii=False, indent=4))
    except Exception as e:
        print(f"Error saving data to JSON: {e}")

def get_wayback_snapshots(base_url, from_date, to_date):
    """Fetch all snapshots from Wayback Machine for the given URL within a date range."""
    client = WaybackClient()
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
                snapshot_date = result.timestamp
                if snapshot_date not in snapshots_by_day:
                    snapshots_by_day[snapshot_date] = result.raw_url
            snapshots = [url for url in sorted(snapshots_by_day.items())]
        else:
            print("No snapshots found for the given date range.")
    except Exception as e:
        print(f"Error fetching snapshots for date range {from_date} to {to_date}: {e}")

    return snapshots

async def main():
    snapshots = get_wayback_snapshots(base_url, start_date_str, end_date_str)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for snapshot in snapshots:
            snapshot_date_str = snapshot[0].strftime('%Y-%m-%d')
            snapshot_url = snapshot[1].replace("http://", "https://")

            print(f"Queueing MEPs fetch from: {snapshot_url}")
            task = get_meps_from_snapshot(session, snapshot_url, snapshot_date_str)
            tasks.append(task)

            # Add a random delay to avoid overloading the server
            await asyncio.sleep(random.uniform(1, 3))

        # Run all tasks concurrently
        await asyncio.gather(*tasks)

    await save_to_json(meps_list)

# Run the main async function
asyncio.run(main())
