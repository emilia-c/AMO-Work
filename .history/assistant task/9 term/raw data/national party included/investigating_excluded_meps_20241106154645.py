import re

# Define file paths
file_missing_htmls = 'missing_htmls_explanation.txt'
file_9termmeps = '9termmeps_not_included.txt'

# Read the MEP names from 9termmeps_not_included.txt
with open(file_9termmeps, 'r', encoding='utf-8') as f:
    meps_in_9term = {line.strip() for line in f if line.strip()}  # Strip to clean up any extra spaces

# Read the content of missing_htmls.explanation.txt
with open(file_missing_htmls, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Initialize a set for the MEP names in missing_htmls.explanation.txt
meps_in_explanation = set()

# Loop through each line and extract the MEP names (assuming the names are followed by ')')
for line in lines:
    # Match the MEP name after the number (e.g., 'Alicia HOMS GINEL')
    match = re.match(r'^\d+\) (.+)', line.strip())
    if match:
        meps_in_explanation.add(match.group(1))

# Compare and print names that are in 9termmeps_not_included.txt but not in missing_htmls.explanation.txt
not_in_explanation = meps_in_9term - meps_in_explanation
print("MEPs in 9termmeps_not_included.txt but not in missing_htmls.explanation.txt:")
for mep in not_in_explanation:
    print(mep)

# Now, update the missing_htmls.explanation.txt file if URL is missing or blank
updated_lines = []

for line in lines:
    if line.startswith("URL:"):
        # Check if the URL section is missing or just blank, add "NO ARCHIVED URL AVAILABLE"
        url_content = line.strip()[4:].strip()  # Get content after 'URL:' and strip spaces
        if not url_content:
            updated_lines.append("URL: NO ARCHIVED URL AVAILABLE\n")
        else:
            updated_lines.append(line)
    else:
        updated_lines.append(line)

# Save the updated content back to the file
with open(file_missing_htmls, 'w', encoding='utf-8') as f:
    f.writelines(updated_lines)

print(f"\nMissing or blank URLs have been updated in {file_missing_htmls}.")
