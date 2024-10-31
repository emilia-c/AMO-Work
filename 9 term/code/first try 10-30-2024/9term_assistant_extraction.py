import requests
import json
import time
import os
import pickle
from bs4 import BeautifulSoup
from tqdm import tqdm
from collections import defaultdict
from wayback import WaybackClient
from datetime import datetime, timedelta

# 1. SET UP CACHE (save api request results)
# Define the cache file path
CACHE_FILE = 'wayback_cache.pkl'

# Load cache from file if it exists and is not empty
if os.path.exists(CACHE_FILE) and os.path.getsize(CACHE_FILE) > 0:
    with open(CACHE_FILE, 'rb') as f:
        try:
            cache = pickle.load(f)
        except EOFError:
            # If the file is empty, initialize an empty cache
            cache = {}
else:
    cache = {}

def save_cache():
    """Save the cache to a file."""
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(cache, f)

# 2. GET WAYBACK SNAPSHOTS
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

class ArchivedMEP:
    """Class to hold information about an archived MEP and their assistants."""
    def __init__(self, url):
        self.url = url
        self.name = None
        self.mep_party = None
        self.assistants = defaultdict(list)  # Assistant names with snapshot dates

    def get_mep_data(self, snapshot_url):
        """Retrieve MEP data from a specific snapshot URL."""
        response = requests.get(snapshot_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Scrape MEP Name
        name_tag = soup.find('span', class_='sln-member-name')
        if name_tag:
            self.name = name_tag.text.strip()

        # Scrape MEP Party
        mep_party_tag = soup.find('h3', class_='erpl_title-h3 mt-1 sln-political-group-name')
        if mep_party_tag:
            self.mep_party = mep_party_tag.text.strip()

        # Locate all assistant sections
        assistants_sections = soup.find_all('div', class_='erpl_type-assistants')
        for section in assistants_sections:
            assistant_type = section.find('h4', class_='erpl_title-h4').text.strip()
            if assistant_type not in self.assistants:
                self.assistants[assistant_type] = {}

            # Extract assistant names
            for assistant_tag in section.find_all('div', class_='erpl_type-assistants-item'):
                assistant_name = assistant_tag.find('span', class_='erpl_assistant').text.strip()
                
                # Store assistant name with snapshot date
                if assistant_name not in self.assistants[assistant_type]:
                    self.assistants[assistant_type][assistant_name] = []
                self.assistants[assistant_type][assistant_name].append(snapshot_url)

    def to_dict(self):
        """Convert the archived MEP data to a dictionary."""
        return {
            "name": self.name,
            "party": self.mep_party,
            "assistants": self.assistants
        }

def construct_archived_mep_url(mep_name, mep_id, snapshot_url):
    """Construct the full URL for the MEP assistant page based on the snapshot URL."""
    names = mep_name.split()
    first_names = []
    last_names = []

    for name in names:
        if name.isupper():
            last_names.append(name)
        else:
            first_names.append(name)

    first_name_part = '+'.join(first_names)
    last_name_part = '+'.join(last_names)

    if last_names:
        if first_names:
            return f"{snapshot_url}http://www.europarl.europa.eu/meps/en/{mep_id}/{first_name_part}+{last_name_part}/assistants#mep-card-content"
        else:
            return f"{snapshot_url}http://www.europarl.europa.eu/meps/en/{mep_id}/{last_name_part}/assistants#mep-card-content"
    else:
        return f"{snapshot_url}http://www.europarl.europa.eu/meps/en/{mep_id}/{first_name_part}/home"

def get_archived_mep_links(from_date, to_date):
    """Scrape MEP links from the archived version of the MEP list page."""
    base_url = "http://www.europarl.europa.eu/meps/en/full-list"
    
    # Get the closest snapshot for the base page
    snapshot_urls = get_wayback_snapshots(base_url, from_date, to_date)
    if not snapshot_urls:
        print("No snapshots found for the given date range.")
        return []
    
    # Use the first snapshot found
    snapshot_url = snapshot_urls[0]
    
    response = requests.get(snapshot_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    mep_links = []
    
    # Find all MEP links in the archived structure
    for mep in soup.select('a.ep_content'):
        mep_url_base = mep['href']
        
        # Extract MEP name and ID
   mep_name = mep.find('span', class_='ep_name member-name').text.strip()
        mep_id = mep_url_base.split('/')[-1]     m
        
        # Construct full archived assistant page URL
        mep_assistant_url = construct_archived_mep_url(mep_name, mep_id, snapshot_url)
        mep_links.append(mep_assistant_url)

    return mep_links

def scrape_archived_meps(url):
    """Scrape MEP data from the archived assistant page."""
    mep = ArchivedMEP(url)
    mep.get_mep_data(url)  # Use the MEP's own snapshot URL
    return mep.to_dict()  # Return dictionary directly


def main():
    from_date = "20190101"  # Start of 2019
    to_date = "20191231"    # End of 2019

    # Step 1: Retrieve archived MEP links
    print("Fetching archived MEP links...")
    mep_links = get_archived_mep_links(from_date, to_date)
    
    # Step 2: Limit to the first 5 MEP links for testing purposes
    if not mep_links:
        print("No MEP links found for the given date range.")
        return
    
    mep_links = mep_links[:5]  # Limit to 5 for testing

    all_mep_data = []

    # Step 3: Scrape MEP assistants data for each URL, showing progress
    print("Scraping MEP assistants data...")
    for mep_url in tqdm(mep_links, desc="Scraping MEPs"):
        try:
            mep_data = scrape_archived_meps(mep_url)
            all_mep_data.append(mep_data)
        except Exception as e:
            print(f"Error scraping {mep_url}: {e}")
        time.sleep(5)  # Delay to avoid server overload
    
    # Step 4: Save the data to a JSON file
    output_file = "mep_assistants_test.json"
    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(all_mep_data, outfile, ensure_ascii=False, indent=4)
    
    print(f"Data saved to {output_file}")
    print(json.dumps(all_mep_data, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()