import re
import json

def parse_mep_data(text):
    # Split the text by entries starting with a number followed by `)`
    entries = re.split(r'\d+\)\s+', text.strip())
    data = []

    for entry in entries:
        if not entry.strip():
            continue

        mep = {}

        # Extract Name
        name_match = re.search(r'Name:\s*(.*)', entry)
        mep['name'] = name_match.group(1).strip() if name_match else None

        # Extract National party
        party_match = re.search(r'National party:\s*(.*)', entry)
        mep['national_party'] = party_match.group(1).strip() if party_match else None

        # Extract Group
        group_match = re.search(r'Group:\s*(.*)', entry)
        mep['group'] = group_match.group(1).strip() if group_match else None

        # Extract Country
        country_match = re.search(r'Country:\s*(.*)', entry)
        mep['country'] = country_match.group(1).strip() if country_match else None

        # Add date_scraped field
        mep['date_scraped'] = "Scraped manually via Parltack"

        # Initialize assistants dictionary
        assistants = {
            "Accredited assistants": [],
            "Accredited assistants (grouping)": [],
            "Local assistants": [],
            "Local assistants (grouping)": [],
            "Paying agents": [],
            "Service providers": [],
            "Trainees": []
        }

        # Helper function to extract lists of items under each category
        def extract_list(category):
            pattern = rf'{category}\s*(.*?)(?=\n[A-Z]|$)'
            match = re.search(pattern, entry, re.DOTALL)
            if match:
                # Find all lines starting with optional whitespace followed by a dash and then the assistant's name
                items = re.findall(r'[-\s]*\s*(.+)', match.group(1))
                return [item.strip() for item in items if item.strip()]
            return []

        # Extract each category of assistants
        assistants["Accredited assistants"] = extract_list("Accredited assistants")
        assistants["Accredited assistants (grouping)"] = extract_list("Accredited assistants \\(grouping\\)")
        assistants["Local assistants"] = extract_list("Local assistants")
        assistants["Local assistants (grouping)"] = extract_list("Local assistants \\(grouping\\)")
        assistants["Paying agents"] = extract_list("Paying agents")
        assistants["Service providers"] = extract_list("Service providers")
        assistants["Trainees"] = extract_list("Trainees")

        mep['assistants'] = assistants

        # Append the parsed MEP data to the list
        data.append(mep)

    return data

# Read the input text file
with open('manual_assistant_additions_meps9and10.txt', 'r', encoding='utf-8') as file:
    text_content = file.read()

# Parse the data
parsed_data = parse_mep_data(text_content)

# Convert the parsed data to JSON
json_output = json.dumps(parsed_data, indent=4, ensure_ascii=False)

# Save the JSON output to a file
with open('mep_data.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_output)

print("Data successfully parsed and saved to mep_data.json")
