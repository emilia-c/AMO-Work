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

        # Initialize assistants dictionary
        assistants = {
            "Accredited assistants": [],
            "Accredited assistants (grouping)": [],
            "Local assistants": [],
            "Local assistants (grouping)": [],
            "Paying agents": [],
            "Service providers": []
        }

        # Helper function to extract lists of assistants by category
        def extract_assistants(category):
            pattern = rf'{category}\s*- ([^\n]+)'
            matches = re.findall(pattern, entry)
            return [match.strip() for match in matches]

        # Extract Accredited assistants
        assistants["Accredited assistants"] = extract_assistants("Accredited assistants")

        # Extract Accredited assistants (grouping)
        assistants["Accredited assistants (grouping)"] = extract_assistants("Accredited assistants \\(grouping\\)")

        # Extract Local assistants
        assistants["Local assistants"] = extract_assistants("Local assistants")

        # Extract Local assistants (grouping)
        assistants["Local assistants (grouping)"] = extract_assistants("Local assistants \\(grouping\\)")

        # Extract Paying agents
        assistants["Paying agents"] = extract_assistants("Paying agents")

        # Extract Service providers
        assistants["Service providers"] = extract_assistants("Service providers")

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
with open('meps_manually_added.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_output)

print("Data successfully parsed and saved to mep_data.json")
