import json
import re

# Load JSON data into a dictionary
JSON_PATH = "C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/9 term/raw data/mep names and assistants/MEPs_9term_AREYOUTHERE.json"
CLEANED_JSON_PATH = "C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/9 term/raw data/mep names and assistants/cleaned_MEPs.json"

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

meps_data = load_mep_data(JSON_PATH)

# Function to count blank and None instances in person data
def count_blank_and_none_instances(data):
    blank_counts = {
        "name": 0,
        "party": 0,
        "country": 0,
    }
    
    none_counts = {
        "name": 0,
        "party": 0,
        "country": 0,
    }
    
    party_none_info = []  # To store information of MEPs with None party values
    
    for person in data:
        # Check and count blanks and None values for name, party, and country
        name = person.get("name")
        party = person.get("party")
        country = person.get("country")
        
        # Count blank instances
        if isinstance(name, str) and not name.strip():
            blank_counts["name"] += 1
        if isinstance(party, str) and not party.strip():
            blank_counts["party"] += 1
        if isinstance(country, str) and not country.strip():
            blank_counts["country"] += 1
        
        # Count None values and track their information
        if name is None:
            none_counts["name"] += 1
        if party is None:
            none_counts["party"] += 1
            party_none_info.append(person)  # Store entire person record
        if country is None:
            none_counts["country"] += 1

    return blank_counts, none_counts, party_none_info

# Get blank counts, none counts, and party none info
blank_counts, none_counts, party_none_info = count_blank_and_none_instances(meps_data)

# Print results
print("Blank instances count:")
for category, count in blank_counts.items():
    print(f"{category}: {count}")

print("\nNone values count:")
for category, count in none_counts.items():
    print(f"{category}: {count}")

# Print information for MEPs with None party values
if party_none_info:
    print("\nMEPs with None party values:")
    for person in party_none_info:
        print(json.dumps(person, ensure_ascii=False, indent=4))

# Clean the country values directly in the MEP data
for person in meps_data:
    if 'country' in person:
        country = person['country'].strip()
        # Use regex to keep only the country name
        match = re.match(r"^[^\n]*", country)  # Match everything before the first newline
        if match:
            person['country'] = match.group(0).strip()  # Update country to the cleaned version

# Filter out MEPs with None party values
cleaned_meps_data = [mep for mep in meps_data if mep.get("party") is not None]

# Collect unique countries and parties from the cleaned MEP data
unique_countries = {mep['country'] for mep in cleaned_meps_data}
unique_parties = {mep['party'] for mep in cleaned_meps_data}

# Save the cleaned MEPs data to a new JSON file
with open(CLEANED_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(cleaned_meps_data, f, ensure_ascii=False, indent=4)

# Print summary information
print(f"\nCleaned MEPs data saved to: {CLEANED_JSON_PATH}")
print(f"Total entries after cleaning: {len(cleaned_meps_data)}")
print(f"Unique countries: {len(unique_countries)}")
print(f"Unique parties: {len(unique_parties)}")

# Print unique countries and unique parties
print("\nUnique Countries:")
for country in unique_countries:
    print(country)

print("\nUnique Parties:")
for party in unique_parties:
    print(party)