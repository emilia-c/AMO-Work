import pandas as pd
import json
import os
import re

# 1. READ IN DATA
file_path = "C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/9 term/raw data/mep names and assistants/cleaned_9term_MEPs.json"

# Check if file exists
if not os.path.exists(file_path):
    raise FileNotFoundError(f"The file at {file_path} does not exist.")

# Open and load the JSON data from the file using UTF-8 encoding
try:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
except UnicodeDecodeError as e:
    raise ValueError(f"Encoding error: {e}")
except json.JSONDecodeError as e:
    raise ValueError(f"Error decoding JSON: {e}")

# 2. Define the function to extract the date scraped
def extract_date_scraped(mep_name):
    # Use the MEP name directly to create the path (keep spaces)
    snapshot_info_path = f"C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/9 term/raw data/mep_assistant_pages_htmls/{mep_name}/snapshot_info.txt"
    
    # Check if snapshot_info.txt exists
    if os.path.exists(snapshot_info_path):
        with open(snapshot_info_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Extract the date from the URL
            match = re.search(r'web\/(\d{8})', content)  # Look for 8 consecutive digits
            if match:
                date_str = match.group(1)  # Get the matched date string
                # Format the date as YYYY-MM-DD
                return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    
    return "Added manually"  # Set to "N/A" if not found or adjust to any specific date you want

# 3. Update the JSON data with scraped dates
for mep in data:
    mep_name = mep['name']
    # Extract the date scraped for each MEP
    mep['date_scraped'] = extract_date_scraped(mep_name)

# 4. Save the updated JSON data back to a file
output_file_path = "C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/9 term/raw data/mep names and assistants/FINAL_9term_MEPs_with_dates_manual_change.json"
with open(output_file_path, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print(f"Updated JSON data has been saved to {output_file_path}")