import requests
from bs4 import BeautifulSoup
import json
import time

# Define the base URL of the page you want to scrape
base_url = 'https://www.europarl.europa.eu/meps/en/assistants'

# Step 1: Query the Wayback Machine API to get all snapshots from 2019
def get_all_snapshots_in_2019(url):
    api_url = f'http://web.archive.org/cdx/search/cdx?url={url}&output=json&fl=timestamp&from=20190101&to=20191231&sort=asc'
    
    response = requests.get(api_url)
    if response.status_code == 200:
        snapshots = json.loads(response.text)
    return [snapshot[0] for snapshot in snapshots[1:]]  # Skip header and return all timestamps
        else:
           print("No snapshots found in 2019.")
           return []
    else:
        print(f"Failed to fetch Wayback Machine snapshots. Status code: {response.status_code}")
        return []

# Step 2: Retrieve content from a specific snapshot and extract only Accredited Assistants
def get_accredited_assistants_from_snapshot(timestamp, url):
    snapshot_url = f'https://web.archive.org/web/{timestamp}/{url}'
    
    try:
        response = requests.get(snapshot_url)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract Accredited Assistant names from the page
        accredited_assistants = set()  # Use a set to store unique accredited assistant names
        rows = soup.find_all('tr', class_='europarl-expandable-item')
        for row in rows:
            assistant_type = row.find('td', {'data-th': 'Type'}).get_text(strip=True)
            if assistant_type == 'Accredited Assistants':  # Only process Accredited Assistants
                assistant_name = row.find('td', {'data-th': 'Assistant'}).get_text(strip=True)
                accredited_assistants.add(assistant_name)  # Add to set to ensure uniqueness

        return accredited_assistants

    except requests.RequestException as e:
         print(f"Error retrieving snapshot {timestamp}: {e}")
    return set()

# Step 3: Main function to get all unique accredited assistants from all snapshots in 2019
def get_unique_accredited_assistants_from_2019(base_url):
    snapshots = get_all_snapshots_in_2019(base_url)
    unique_accredited_assistants = set()

    # Loop through each snapshot, extract accredited assistants, and add unique names to the set
    for timestamp in snapshots:
        print(f'Fetching data from snapshot {timestamp}...')
        assistants = get_accredited_assistants_from_snapshot(timestamp, base_url)
        unique_accredited_assistants.update(assistants)  # Add new assistants to the set
        
        # Optional: Add a short delay to avoid overwhelming the server
        time.sleep(1)
    
    return unique_accredited_assistants

# Step 4: Save the unique accredited assistant names to a file
def save_accredited_assistants_to_file(assistants, filename='unique_accredited_assistants_2019.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(list(assistants), f, ensure_ascii=False, indent=4)
    print(f"Unique accredited assistants saved to {filename}")

# Run the script
unique_accredited_assistants = get_unique_accredited_assistants_from_2019(base_url)

# Save the results
save_accredited_assistants_to_file(unique_accredited_assistants)

# Print the number of unique accredited assistants found
print(f"Total unique accredited assistants found in 2019: {len(unique_accredited_assistants)}")