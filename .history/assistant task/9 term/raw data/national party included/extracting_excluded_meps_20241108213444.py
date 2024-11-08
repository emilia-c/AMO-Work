import os

# Path to the error log file
input_file_path = 'error_log_9term.txt'
output_file_path = '9termmeps_not_included.txt'

# Open the error log file for reading
with open(input_file_path, 'r', encoding='utf-8') as file:
    # List to store the MEP names
    mep_names = []

    # Read each line in the file
    for line in file:
        # Check if the line is related to a directory (contains 'is empty' text)
        if "is empty or contains no HTML files" in line:
            # Extract the last directory name from the path
            # Split by backslash and take the last part (folder name)
            dir_path = line.split("Directory '")[1].split("'")[0]
            mep_name = dir_path.split(os.sep)[-1]  # Get the last folder name
            mep_names.append(mep_name)
        
        # Check if the line is about a specific HTML file error
        elif "Error: MEP national party not found" in line:
            # Extract the file name (MEP name) from the path
            file_path = line.split("File: ")[1].split(",")[0]
            mep_name = file_path.split(os.sep)[-2]  # Get the folder name which is the MEP name
            mep_names.append(mep_name)

# Write the extracted MEP names into the output file
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    for mep in mep_names:
        output_file.write(mep + '\n')

print(f"MEP names extracted and saved to {output_file_path}")