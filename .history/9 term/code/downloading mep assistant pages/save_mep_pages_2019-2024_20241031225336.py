import json
import os
import subprocess
import time
import urllib.parse  # For encoding URL components

# Load MEP data from JSON
with open("C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/9 term/raw data/merged_mep_9term.json", "r", encoding="utf-8") as f:
    meps_data = json.load(f)

# Extract unique MEPs by ID
unique_meps = {mep["mep_id"]: mep for mep in meps_data}.values()

count = 0
for mep in unique_meps: 
    count +=1
print(count)