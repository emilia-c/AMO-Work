import pandas as pd
import json
from fuzzywuzzy import process

# Load JSON data into a dictionary
JSON_PATH = "C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/9 term/raw data/merged_mep_9term.json"

def load_mep_data(json_path):
    """Load MEP data from a JSON file."""
    print(f"Loading MEP data from: {json_path}")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            meps_data = json.load(f)
        print(f"Loaded {len(meps_data)} MEPs successfully.")
        return meps_data
    except Exception as e:
        print(f"Failed to load MEP data: {e}")
        exit(1)

# Load and sort the MEPs data by 'mep_name'
meps_data = load_mep_data(JSON_PATH)
sorted_meps = sorted(meps_data, key=lambda x: x['mep_name'])

# Create a set of MEP names with spaces removed, for comparison
mep_names_no_spaces = {mep['mep_name'].replace(" ", "").strip().lower() for mep in sorted_meps}

# Read only the first sheet of the Excel file into a DataFrame
EXCEL_PATH = "C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/9 term/raw data/from_domi_all_mep_names_9term.xlsx"
df = pd.read_excel(EXCEL_PATH, sheet_name=0)  # `sheet_name=0` specifies the first sheet

# Create 'member_name' with spaces intact, and then a version without spaces for matching
df['member_name'] = df['member.first_name'].str.strip() + ' ' + df['member.last_name'].str.strip()
df['member_name_no_spaces'] = df['member_name'].str.replace(" ", "").str.lower()

# Compare and count matches using the no-spaces version
df['is_match'] = df['member_name_no_spaces'].apply(lambda name: name in mep_names_no_spaces)
match_count = df['is_match'].sum()
print(f"Total matches found: {match_count}")

# Filter for unmatched member names and find the closest MEP name for each
unmatched_df = df[df['is_match'] == False].copy()
unmatched_df['closest_mep_name'] = unmatched_df['member_name'].apply(
    lambda name: process.extractOne(name, [mep['mep_name'] for mep in sorted_meps])[0]
)

# Identify MEPs in the JSON data that don't have a match in the Excel data
excel_member_names_no_spaces = set(df['member_name_no_spaces'])
unmatched_meps = [mep['mep_name'] for mep in sorted_meps if mep['mep_name'].replace(" ", "").strip().lower() not in excel_member_names_no_spaces]

# Create a DataFrame for unmatched MEPs
unmatched_meps_df = pd.DataFrame(unmatched_meps, columns=['mep_name'])
unmatched_meps_df['closest_member_name'] = unmatched_meps_df['mep_name'].apply(
    lambda name: process.extractOne(name, df['member_name'])[0]
)

# Output unmatched rows and MEP names that didn't match
print("\nUnmatched Member Names with Closest MEP Suggestions:")
print(unmatched_df[['member_name', 'closest_mep_name']])

print("\nMEPs from JSON with No Matches in Excel and Closest Excel Member Names:")
print(unmatched_meps_df)

# Save results to a new sheet in the Excel file
with pd.ExcelWriter(EXCEL_PATH, engine='openpyxl', mode='a') as writer:
    unmatched_df[['member_name', 'is_match', 'closest_mep_name']].to_excel(writer, sheet_name="9term_meps_investigation", index=False)
    unmatched_meps_df.to_excel(writer, sheet_name="unmatched_meps_in_json", index=False)
print(f"Unmatched rows and unmatched MEPs saved to '9term_meps_investigation' and 'unmatched_meps_in_json' in {EXCEL_PATH}")