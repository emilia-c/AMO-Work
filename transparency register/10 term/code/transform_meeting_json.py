import pandas as pd
import json
import os
import re

# 1. READ IN DATA
file_path = "C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/transparency register/raw data/final 10-30-2024/mep_meetings_FULL.json"

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

# 2. EXTRACT MEETING DATA TO A NEW DATAFRAME
rows = []

# Iterate over each MEP's data
for mep in data:
    mep_name = mep['name']
    mep_party = mep['party']
    mep_country = mep['origin_country']

    # Check for 'meetings' data and iterate over each meeting
    if 'meetings' in mep:
        meetings = mep['meetings']
        
        for meeting_id, meeting in meetings.items():
            # Ensure all required fields are present in each meeting
            if meeting:  # skip empty meetings
                rows.append({
                    'meeting_reason': meeting.get('reason', 'N/A'),
                    'meeting_with': meeting.get('meeting_with', 'N/A'),
                    'meeting_date': meeting.get('date', 'N/A'),
                    'meeting_place': meeting.get('place', 'N/A'),
                    'capacity': meeting.get('capacity', 'N/A'),
                    'committee_code': meeting.get('committee_code', 'N/A'),
                    'mep_name': mep_name,
                    'mep_party': mep_party,
                    'mep_country': mep_country
                })

# 3. CREATE THE FINAL DATAFRAME
meetings_df = pd.DataFrame(rows)

# 4. ADD PARTY ABBREVIATIONS
political_grp_abbrv_dict = {
    "Group of the European People's Party (Christian Democrats)": "EPP",
    "Group of the Progressive Alliance of Socialists and Democrats in the European Parliament": "S&D",
    "Renew Europe Group": "Renew Europe",
    "Group of the Greens/European Free Alliance": "Greens/EFA",
    "The Left group in the European Parliament - GUE/NGL": "The Left",
    "Non-attached Members": "NI",
    "Patriots for Europe Group": "PfE",
    "European Conservatives and Reformists Group": "ECR",
    "Europe of Sovereign Nations Group": "ESN"
}

# Map the full names to abbreviations
meetings_df['mep_party'] = meetings_df['mep_party'].apply(
    lambda x: political_grp_abbrv_dict.get(x, x)
)

# EXPLORE MEPS DATA 
#print(meetings_df['meeting_with'].head())
#print(meetings_df.tail())
# Check the first few unique values in 'meeting_with' to see the format and any inconsistencies
#print(meetings_df['meeting_with'].value_counts())

# CLEAN & STANDARDIZE
# Strip leading/trailing whitespace, and replace multiple newline characters with a single space
meetings_df['meeting_with'] = meetings_df['meeting_with'].str.replace(r'\n+', ' ', regex=True).str.strip()
meetings_df['meeting_with'] = meetings_df['meeting_with'].str.lower().str.strip()

# EXTRACT TRANSPARENCY NOS
# extract any instances of transparency no (either in meeting reason or meeting with)
# Sample regex pattern to match transparency numbers in the format of numbers with a hyphen (e.g., 316522140912-19)
transparency_pattern = r'(?:transparency no\.?\s*)?(\d{12}-\d{2})' 

# MILAN DID NOT DO HIS DD, WRONG DIGIT 

# Function to extract transparency number from a given text
def extract_transparency_no(row):
    # Search for pattern in both 'meeting_reason' and 'meeting_with' columns
    match = re.search(transparency_pattern, row['meeting_with'] or ['meeting_reason'])
    return match

# Apply the function to both 'meeting_reason' and 'meeting_with' columns and combine results
# Apply the function to each row in the DataFrame
meetings_df['transparency_no'] = meetings_df.apply(extract_transparency_no, axis=1)

# Display the DataFrame with only rows where transparency_no is not None
non_null_transparency = meetings_df[meetings_df['transparency_no'].notna()]

# Display the filtered DataFrame
print (non_null_transparency)


# Count occurrences of each unique 'meeting_with' entity
#meeting_counts = meetings_df['meeting_with'].value_counts().reset_index()
#meeting_counts.columns = ['meeting_with', 'count']
# export meeting counts to excel
#meeting_counts.to_excel('all_meetings_who_with.xlsx', index=False, engine='openpyxl')


# EXPORT TO EXCEL
#XX.to_excel('all_meetings_who_with.xlsx', index=False, engine='openpyxl')