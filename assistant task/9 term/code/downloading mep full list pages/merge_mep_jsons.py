import json
import chardet

# 1. CHECK ENCODING OF FILES
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']  # Return just the encoding string

# Example usage
encoding1 = detect_encoding('C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/9 term/raw data/mep_names_and_ids_2019_2020.json')
encoding2 = detect_encoding('C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/9 term/raw data/mep_names_and_ids_2021-2024.json')

print(f"File 1 Encoding: {encoding1}")
print(f"File 2 Encoding: {encoding2}")

# 2. FUNCTION TO MERGE THE FILES BASED ON UNIQUE MEP IDS
def merge_json_files(file1, file2, output_file):
    # Load the data from the first file with detected encoding
    with open(file1, 'r', encoding=encoding1) as f:
        data1 = json.load(f)

    # Load the data from the second file with detected encoding
    with open(file2, 'r', encoding=encoding2) as f:
        data2 = json.load(f)

    # Use a dictionary to store unique mep_id instances
    unique_mep = {}

    # Add entries from the first file
    for entry in data1:
        unique_mep[entry['mep_id']] = entry

    # Add entries from the second file, only if mep_id is not already in the dictionary
    for entry in data2:
        unique_mep[entry['mep_id']] = entry

    # Convert the dictionary back to a list
    merged_data = list(unique_mep.values())

    # Save the merged data to a new JSON file without escaping non-ASCII characters
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=4)

# 3. RUN THE FUNCTION ON THE ORIGNAL MEP NAMES RESULTING IN A MERGED LIST
merge_json_files(
    'C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/9 term/raw data/mep_names_and_ids_2019_2020.json',
    'C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/9 term/raw data/mep_names_and_ids_2021-2024.json',
    'merged_mep_9term.json'
)
