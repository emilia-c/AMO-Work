import json
from datetime import datetime
import os
import subprocess
import time
import urllib.parse  # For encoding URL components

# Load MEP data from JSON
with open("C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/9 term/raw data/merged_mep_9term.json", "r", encoding="utf-8") as f:
    meps_data = json.load(f)

# Step 1: Convert date_scraped to datetime objects
for entry in meps_data:
    entry['date_scraped'] = datetime.strptime(entry['date_scraped'], "%Y-%m-%d")

# Step 2: Find the latest date
latest_date = max(entry['date_scraped'] for entry in meps_data)

# Step 3: Count entries with dates that are not the latest
non_latest_count = sum(1 for entry in meps_data if entry['date_scraped'] < latest_date)

print(f"Number of entries with dates not equal to the latest date: {non_latest_count}")

# Step 4: Sort the entries alphabetically by 'mep_name'
sorted_data = sorted(meps_data, key=lambda x: x['mep_name'])
