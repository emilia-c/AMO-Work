import json
from datetime import datetime
import os
import subprocess
import time
import urllib.parse  # For encoding URL components

# Load MEP data from JSON
with open("C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/9 term/raw data/merged_mep_9term.json", "r", encoding="utf-8") as f:
    meps_data = json.load(f)

# Sort the entries alphabetically by 'mep_name'
sorted_data = sorted(meps_data, key=lambda x: x['mep_name'])
print(sorted_data)