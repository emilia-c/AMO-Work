import pandas as pd
import json
import os

# 1. READ IN DATA
file_path = "C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/assistant task/10 term/mep_assistants_national_party.json"

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
    mep_party = mep['mep_national_party']
    mep_group = mep['mep_group']
    mep_country = mep['country']

    # Check for Accredited assistants
    if 'Accredited assistants' in mep['assistants']:
        assistants = mep['assistants']['Accredited assistants']
        
        for assistant in assistants:
            if assistant not in assistant_to_details:
                assistant_to_details[assistant] = {
                    'assistant_type': 'apa',
                    'meps': set(),
                    'groups':set(),
                    'parties': set(),
                    'countries': set()
                }
            assistant_to_details[assistant]['meps'].add(mep_name)
            assistant_to_details[assistant]['groups'].add(mep_group)
            assistant_to_details[assistant]['parties'].add(mep_party)
            assistant_to_details[assistant]['countries'].add(mep_country)

    # Check for Accredited assistants (grouping)
    if 'Accredited assistants (grouping)' in mep['assistants']:
        assistants_grouping = mep['assistants']['Accredited assistants (grouping)']
        
        for assistant in assistants_grouping:
            if assistant not in assistant_to_details:
                assistant_to_details[assistant] = {
                    'assistant_type': 'apa grouped',
                    'meps': set(),
                    'groups': set(),
                    'parties': set(),
                    'countries': set()
                }
            else:
                # If already exists, change to "both" if it's a grouped assistant
                if assistant_to_details[assistant]['assistant_type'] == 'apa':
                    assistant_to_details[assistant]['assistant_type'] = 'both'
                    
            assistant_to_details[assistant]['meps'].add(mep_name)
            assistant_to_details[assistant]['groups'].add(mep_group)
            assistant_to_details[assistant]['parties'].add(mep_party)
            assistant_to_details[assistant]['countries'].add(mep_country)

# 3. Create the final DataFrame
rows = []
for assistant, details in assistant_to_details.items():
    meps_list = ', '.join(details['meps'])
    groups_list = ', '.join(details['groups'])
    parties_list = ', '.join(details['parties'])
    countries_list = ', '.join(details['countries'])
    year = '5-11-2024'
    term = '10'
    
    rows.append({
        'assistant_name': assistant,
        'assistant_type': details['assistant_type'],
        'mep(s)': meps_list,
        'mep(s) country': countries_list,
        'political_group(s)': groups_list,
        'meps(s) national parties': parties_list,
        'date_scraped': year, 
        'term': term
    })

assistants_2024 = pd.DataFrame(rows)

# 4. ADD NEW COLUMNS FOR POLITICAL GROUP ABBREVIATIONS
political_grp_abbrv_dict = {
    "EPP": "Group of the European People's Party (Christian Democrats)",
    "S&D": "Group of the Progressive Alliance of Socialists and Democrats in the European Parliament",
    "Renew Europe": "Renew Europe Group",
    "Greens/EFA": "Group of the Greens/European Free Alliance",
    "The Left": "The Left group in the European Parliament - GUE/NGL",
    "NI": "Non-attached Members",
    "PfE": "Patriots for Europe Group", 
    "ECR": "European Conservatives and Reformists Group", 
    "ESN": "Europe of Sovereign Nations Group"
}

# Reverse the dictionary to map from full name to abbreviation
abbreviation_mapping = {v: k for k, v in political_grp_abbrv_dict.items()}

# Add a new column with abbreviations while keeping the original column
assistants_2024['political_group_abbrv'] = assistants_2024['political_group(s)'].apply(
    lambda x: ', '.join([abbreviation_mapping.get(party, party) for party in x.split(', ')])
)


# 5. Get unique MEP names from the 'mep(s)' column
# Split the mep(s) column and flatten the list of names, then get unique values
unique_meps = set()
for meps in assistants_2024['mep(s)']:
    unique_meps.update(meps.split(', '))

# Get the length of the unique MEPs list
unique_mep_count = len(unique_meps)

# Print the unique MEPs and their count
#print(f"Unique MEP names: {unique_meps}")
print(f"Number of unique MEP names: {unique_mep_count}")

# 6. SAVE FINAL DF TO CSV
# Write to Excel
assistants_2024.to_excel('10term_assistants_wparty.xlsx', index=False, engine='openpyxl')