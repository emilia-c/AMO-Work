import pandas as pd
import json
import os
from fuzzywuzzy import process

# 1. READ IN DATA
file_path = "C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/9 term/raw data/mep names and assistants/FINAL_9term_MEPs_with_dates_manual_change.json"

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

# 2. JSON TO PANDAS DATAFRAME
assistant_to_details = {}  # Dictionary to track which assistants work for which MEPs and parties

# Iterate over each MEP's data
for mep in data:
    mep_name = mep['name']
    mep_party = mep['party']
    mep_country = mep['country']
    mep_date_scraped = mep.get('date_scraped', None)  # Extract the date scraped

    # Check for Accredited assistants
    if 'Accredited assistants' in mep['assistants']:
        assistants = mep['assistants']['Accredited assistants']
        
        for assistant in assistants:
            if assistant not in assistant_to_details:
                assistant_to_details[assistant] = {
                    'assistant_type': 'apa',
                    'meps': set(),
                    'parties': set(),
                    'countries': set(),
                    'dates_scraped': set()  # Add a set for dates
                }
            assistant_to_details[assistant]['meps'].add(mep_name)
            assistant_to_details[assistant]['parties'].add(mep_party)
            assistant_to_details[assistant]['countries'].add(mep_country)
            if mep_date_scraped:  # Add date if it exists
                assistant_to_details[assistant]['dates_scraped'].add(mep_date_scraped)

    # Check for Accredited assistants (grouping)
    if 'Accredited assistants (grouping)' in mep['assistants']:
        assistants_grouping = mep['assistants']['Accredited assistants (grouping)']
        
        for assistant in assistants_grouping:
            if assistant not in assistant_to_details:
                assistant_to_details[assistant] = {
                    'assistant_type': 'apa grouped',
                    'meps': set(),
                    'parties': set(),
                    'countries': set(),
                    'dates_scraped': set()  # Add a set for dates
                }
            else:
                # If already exists, change to "both" if it's a grouped assistant
                if assistant_to_details[assistant]['assistant_type'] == 'apa':
                    assistant_to_details[assistant]['assistant_type'] = 'both'
                    
            assistant_to_details[assistant]['meps'].add(mep_name)
            assistant_to_details[assistant]['parties'].add(mep_party)
            assistant_to_details[assistant]['countries'].add(mep_country)
            if mep_date_scraped:  # Add date if it exists
                assistant_to_details[assistant]['dates_scraped'].add(mep_date_scraped)

# 3. Fuzzy Matching for Manual Exploration of Names
def explore_similar_assistants(assistant_details):
    assistants_list = list(assistant_details.keys())
    similar_assistants_dict = {}

    for assistant in assistants_list:
        # Find similar assistants
        similar_assistants = process.extract(assistant, assistants_list, limit=None)
        # Filter out matches between 92% and 98% (exclude 100%)
        similar_assistants = [(a, score) for a, score in similar_assistants if 92 <= score < 100]
        
        # Store results in the dictionary if there are any matches
        if similar_assistants:
            similar_assistants_dict[assistant] = similar_assistants
            
    return similar_assistants_dict

# Get similar assistants for merging
similar_assistants_for_merging = explore_similar_assistants(assistant_to_details)

# 4. Merge assistants with high similarity scores
merged_assistants = {}

# Function to merge details
def merge_assistant_details(assistant_names):
    merged_details = {
        'assistant_type': None,
        'meps': set(),
        'parties': set(),
        'countries': set(),
        'dates_scraped': set(),
    }
    
    for name in assistant_names:
        if name in assistant_to_details:
            details = assistant_to_details[name]
            merged_details['meps'].update(details['meps'])
            merged_details['parties'].update(details['parties'])
            merged_details['countries'].update(details['countries'])
            merged_details['dates_scraped'].update(details['dates_scraped'])
            # Set the assistant_type to the most specific type found (apa > apa grouped > both)
            if merged_details['assistant_type'] is None:
                merged_details['assistant_type'] = details['assistant_type']
            else:
                # Determine the type hierarchy
                if details['assistant_type'] == 'apa grouped':
                    merged_details['assistant_type'] = 'both'
                elif merged_details['assistant_type'] == 'apa grouped':
                    merged_details['assistant_type'] = 'both'

    return merged_details

# Handle exact matches by checking lowercase equivalence first
lowercase_dict = {}
for assistant in assistant_to_details.keys():
    lower_name = assistant.lower()
    if lower_name not in lowercase_dict:
        lowercase_dict[lower_name] = [assistant]
    else:
        lowercase_dict[lower_name].append(assistant)

# Merge exact matches (lowercase)
for assistants in lowercase_dict.values():
    if len(assistants) > 1:  # Only merge if there are duplicates
        merged_details = merge_assistant_details(assistants)
        # Keep the name with ASCII characters if available
        ascii_names = [name for name in assistants if all(ord(char) < 128 for char in name)]
        merged_assistant_name = max(ascii_names, key=lambda x: (x.lower(), x)) if ascii_names else assistants[0]
        merged_assistants[merged_assistant_name] = merged_details

# Now merge based on fuzzy matches (92% to 98%)
for assistant, similar in similar_assistants_for_merging.items():
    # Get the set of unique assistants in this group
    similar_assistants_set = set([assistant] + [name for name, score in similar])
    
    # Check for existing lowercase matches to avoid duplicates
    merged_details = merge_assistant_details(similar_assistants_set)

    # Handle the naming preference with ASCII
    ascii_names = [name for name in similar_assistants_set if all(ord(char) < 128 for char in name)]
    
    if ascii_names:
        # Choose the name with ASCII characters to keep
        merged_assistant_name = max(ascii_names, key=lambda x: (x.lower(), x))
    else:
        # Just keep the first one in the set if no ASCII names are found
        merged_assistant_name = next(iter(similar_assistants_set))

    # If this merged assistant already exists, combine the details
    if merged_assistant_name not in merged_assistants:
        merged_assistants[merged_assistant_name] = merged_details
    else:
        existing_details = merged_assistants[merged_assistant_name]
        existing_details['meps'].update(merged_details['meps'])
        existing_details['parties'].update(merged_details['parties'])
        existing_details['countries'].update(merged_details['countries'])
        existing_details['dates_scraped'].update(merged_details['dates_scraped'])

# 5. Add non-merged assistants to the final output
for assistant, details in assistant_to_details.items():
    if assistant not in merged_assistants:
        merged_assistants[assistant] = details

# 6. Create the final DataFrame
rows = []
for assistant, details in merged_assistants.items():
    meps_list = ', '.join(details['meps'])
    parties_list = ', '.join(details['parties'])
    countries_list = ', '.join(details['countries'])
    term = '9'
    dates_scraped_list = ', '.join(sorted(details['dates_scraped']))  # Join unique dates, sorted
    
    rows.append({
        'assistant_name': assistant,
        'assistant_type': details['assistant_type'],  # Maintain original type
        'mep(s)': meps_list,
        'mep(s) country': countries_list,
        'political_group(s)': parties_list,
        'date_scraped': dates_scraped_list,  # Add the dates scraped here
        'term': term
    })

assistants_9term = pd.DataFrame(rows)

# 7. ADD NEW COLUMNS FOR POLITICAL GROUP ABBREVIATIONS (unchanged)
political_grp_abbrv_dict = {
    "EPP": "Group of the European People's Party (Christian Democrats)",
    "S&D": "Group of the Progressive Alliance of Socialists and Democrats in the European Parliament",
    "Renew Europe": "Renew Europe Group",
    "G/EFA": "Group of the Greens/European Free Alliance",
    "NI": "Non-inscrits",
    "ECR": "European Conservatives and Reformists Group", 
    "ID": "Identity and Democracy Group", 
    "GUE/NGL": "The Left group in the European Parliament - GUE/NGL",
}

# Reverse the dictionary to map from full name to abbreviation
abbreviation_mapping = {v: k for k, v in political_grp_abbrv_dict.items()}

# Replace full names with abbreviations in the DataFrame
assistants_9term['political_group(s)'] = assistants_9term['political_group(s)'].apply(
    lambda x: ', '.join([abbreviation_mapping.get(party, party) for party in x.split(', ')])
)

# 8. Get unique MEP names from the 'mep(s)' column (unchanged)
unique_meps = set()
for meps in assistants_9term['mep(s)']:
    unique_meps.update(meps.split(', '))

# Get the length of the unique MEPs list
unique_mep_count = len(unique_meps)

# Print the unique MEPs and their count
print(f"Number of unique MEP names: {unique_mep_count}")
assistants_9term.to_excel('9term_assistants_all.xlsx', index=False, engine='openpyxl')