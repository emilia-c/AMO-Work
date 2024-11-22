import json

# Load the first JSON (Meetings Data)
with open('C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/transparency register/9 term/raw data/9term_mep_meetings_FULL.json', 'r', encoding='utf-8') as file:
    meetings_data = json.load(file)

# Load the second JSON (Supplementary Data)
with open('C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/assistant task/9 term/raw data/final national party merged/FINAL_cleaned_9-10term.json', 'r', encoding='utf-8') as file:
    supplementary_data = json.load(file)

# Create a dictionary from the supplementary data for quick lookup by name
supplementary_dict = {entry['name']: entry for entry in supplementary_data}

# Merge the data
merged_data = []

for meeting_entry in meetings_data:
    name = meeting_entry["name"]
    # Find the corresponding supplementary entry by name
    supplementary_entry = supplementary_dict.get(name, {})

    # Create a merged entry
    merged_entry = {
        "name": name,
        "group": supplementary_entry.get("group", ""),
        "origin_country": supplementary_entry.get("country", ""),
        "national_party": supplementary_entry.get("national_party", ""),
        "meetings": meeting_entry.get("meetings", {})
    }

    # Add the merged entry to the final list
    merged_data.append(merged_entry)

with open('9term_meetings_ALL_INFO.json', 'w', encoding='utf-8') as file:
    json.dump(merged_data, file, indent=4, ensure_ascii=False)

print("Data merged successfully and saved to 'merged_data.json'.")
