import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
from wayback import WaybackClient  # Ensure you have this installed
from tqdm import tqdm  # For progress bar

# Base URL for MEPs and the web archive
base_url = "https://www.europarl.europa.eu/meps/en/full-list/all"

# Date range for snapshots
start_date_str = "20220101"  # January 1, 2019
end_date_str = "20220330"      # June 30, 2024

# A list to store MEP entries
meps_list = []

def get_meps_from_snapshot(snapshot_url, snapshot_date_str):
    """Get MEP names, IDs, and date from a specific snapshot."""
    try:
        response = requests.get(snapshot_url)
        response.raise_for_status()  # Raise an error for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')

        for mep in soup.find_all("a", class_="ep_content"):
            # Extract MEP name and ID from the <a> tag
            mep_name = mep["title"].strip()  # MEP name from title attribute
            mep_href = mep["href"]  # MEP URL
            mep_id = mep_href.split('/')[-1]  # Extracting the ID from the URL

            # Append MEP details to the list
            meps_list.append({
                "mep_id": mep_id,
                "mep_name": mep_name,
                "date_scraped": snapshot_date_str  # Set the date to the snapshot date
            })
            # Save the current MEP list to JSON after each addition
            save_to_json(meps_list)

    except Exception as e:
        print(f"Error fetching data from {snapshot_url}: {e}")

def save_to_json(meps_list):
    """Save the MEP list to a JSON file."""
    json_filename = "MEPs_2022.json"
    try:
        with open(json_filename, 'w', encoding='utf-8') as json_file:
            json.dump(meps_list, json_file, ensure_ascii=False, indent=4)
        print(f"MEP data saved to {json_filename}")
    except Exception as e:
        print(f"Error saving data to JSON: {e}")

def get_wayback_snapshots(base_url, from_date, to_date):
    """Fetch all snapshots from Wayback Machine for the given URL within a date range,
    and filter to one per day."""

    # Initialize WaybackClient
    client = WaybackClient()
    snapshots = []

    # Convert from_date and to_date from strings to datetime objects
    from_date_dt = datetime.strptime(from_date, "%Y%m%d")
    to_date_dt = datetime.strptime(to_date, "%Y%m%d")

    try:
        print(f"Fetching snapshots for {base_url} from {from_date_dt} to {to_date_dt}...")
        results = list(client.search(base_url, from_date=from_date_dt, to_date=to_date_dt))

        # Log the retrieved results for debugging
        print(f"Total snapshots found: {len(results)}")
        
        if results:
            # Filter results to keep only the first snapshot for each day
            snapshots_by_day = {}
            for result in results:
                snapshot_date = result.timestamp
                if snapshot_date not in snapshots_by_day:
                    snapshots_by_day[snapshot_date] = result.raw_url  # Keep only the first snapshot per day

            # Collect snapshots in date order
            snapshots = [url for url in sorted(snapshots_by_day.items())]
        else:
            print("No snapshots found for the given date range.")
    except Exception as e:
        print(f"Error fetching snapshots for date range {from_date} to {to_date}: {e}")

    return snapshots

# Fetch snapshots for the specified date range
snapshots = get_wayback_snapshots(base_url, start_date_str, end_date_str)

# Loop through each snapshot to extract MEP data
for snapshot in snapshots:
    snapshot_date_str = snapshot[0].strftime('%Y-%m-%d')  # Convert to string without timezone
    snapshot_url = snapshot[1].replace("http://", "https://")  # Ensure URL uses https

    print(f"Fetching MEPs from: {snapshot_url}")
    
    get_meps_from_snapshot(snapshot_url, snapshot_date_str)

    # Delay for 10 seconds between requests
    time.sleep(10)

# Final save to ensure all collected data is written
save_to_json(meps_list)
