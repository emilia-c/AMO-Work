import json

# Function to rename assistant keys in the MEP data
def rename_assistant_keys(data):
    # Mapping of old keys to new keys
    key_mapping = {
        'assistants.accredited_assistants': 'Accredited assistants',
        'assistants.accredited_assistants_grouping': 'Accredited assistants (grouping)',
        'assistants.paying_agents': 'Paying agents',
        'assistants.local_assistants': 'Local assistants',
        'assistants.service_providers': 'Service providers',
        'assistants.trainees': 'Trainees',
        'assistants.local_assistants_grouping': 'Local assistants (grouping)',
        'assistants.paying_agents_grouping': 'Paying agents (grouping)',
        # Add any additional mappings as needed
    }

    # Process each MEP in the data
    for mep in data:
        if 'assistants' in mep:
            assistants = mep['assistants']
            # Create a new dictionary for renamed assistants
            new_assistants = {}
            for old_key, new_key in key_mapping.items():
                # Check if the old key exists in the assistants
                old_key_base = old_key.split('.')[-1]  # Get the last part for checking
                for key in list(assistants.keys()):
                    if key.lower() == old_key_base.lower():
                        # Rename and copy the list of assistants
                        new_assistants[new_key] = assistants[key]
                        # Remove the old key
                        del assistants[key]
                        break
            
            # Update the assistants with the new names
            assistants.update(new_assistants)

    return data

# Load original JSON data (replace with your actual file path)
input_file_path = 'C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/assistant task/9 term/raw data/final/9TERM_ALL.json'
output_file_path = 'C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/assistant task/9 term/raw data/final/9TERM_ALL_STANDARDIZED.json'

with open(input_file_path, 'r', encoding='utf-8') as f:
    original_data = json.load(f)

# Rename assistant keys
renamed_data = rename_assistant_keys(original_data)

# Write the updated data to a new JSON file
with open(output_file_path, 'w', encoding='utf-8') as f:
    json.dump(renamed_data, f, ensure_ascii=False, indent=4)

print(f"Updated JSON written to {output_file_path}")