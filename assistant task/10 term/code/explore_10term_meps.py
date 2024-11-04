import pandas as pd
import json
import os

# 1. READ IN DATA
file_path = "C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/mep_assistants.json"

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

# Extract only the name, party, and country fields
extracted_data = [{'name': item['name'], 'party': item['party'], 'country': item['country']} for item in data]

# Create DataFrame
mep_countries = pd.DataFrame(extracted_data)

print(mep_countries['name'].nunique())

# FIND MISSING MEP 

# Find MEPs with empty or missing assistant information
meps_with_no_assistants = []

for mep in data:
    assistants = mep.get('assistants', {})
    accredited_assistants = assistants.get('Accredited assistants', [])
    grouped_assistants = assistants.get('Accredited assistants (grouping)', [])
    
    # Check if both accredited and grouped assistants are empty or missing
    if not accredited_assistants and not grouped_assistants:
        meps_with_no_assistants.append(mep['name'])

# Output the result
if meps_with_no_assistants:
    print("MEPs with no assistants assigned:", meps_with_no_assistants)
else:
    print("All MEPs have at least one assistant.")