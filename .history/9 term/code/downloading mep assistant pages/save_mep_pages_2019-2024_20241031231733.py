import json
from datetime import datetime
import os
import subprocess
import time
import urllib.parse  # For encoding URL components


# 1. SET-UP
# Load MEP data from JSON
with open("C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/9 term/raw data/merged_mep_9term.json", "r", encoding="utf-8") as f:
    meps_data = json.load(f)

# Sort the entries alphabetically by 'mep_name'
sorted_meps = sorted(meps_data, key=lambda x: x['mep_name'])

# Directory to save all downloaded MEP pages
save_dir = "mep_assistant_pages"
os.makedirs(save_dir, exist_ok=True)

# Log file to keep track of errors
error_log = os.path.join(save_dir, "download_errors.log")

# Base URL pattern with MEP ID, Name, and the specific /assistants page
base_url = "https://www.europarl.europa.eu/meps/en/{}/{}/assistants#mep-card-content"

# Date range for snapshots
start_date = "20191010"
end_date = "20240330"

# Test for a specific MEP ID (replace with the desired ID)
test_mep_id = "197490"  # Example MEP ID for testing
test_mep = next((mep for mep in sorted_meps if mep["mep_id"] == test_mep_id), None)

if test_mep:
    mep_id = test_mep["mep_id"]
    mep_name = urllib.parse.quote(test_mep["mep_name"], safe="+")  # URL-encode name
    url = base_url.format(mep_id, mep_name)
    retries = 3  # Number of retries if download fails
    success = False

    for attempt in range(1, retries + 1):
        try:
            # Prepare save directory and file path
            save_path = os.path.join(save_dir, mep_id)
            os.makedirs(save_path, exist_ok=True)
            file_path = os.path.join(save_path, f"{mep_id}.html")

            # Build the wayback_machine_downloader command with date range
            command = [
                "wayback_machine_downloader", url,
                "--directory", save_path,
                "--only", f"/meps/en/{mep_id}/",  # Restrict download to the MEP's path
                "--from", start_date,
                "--to", end_date
            ]

            print(f"Attempt {attempt}/{retries}: Downloading {test_mep['mep_name']} (ID: {mep_id})")
            subprocess.run(command, check=True)
            success = True

            # Check if file was populated
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                print(f"Downloaded successfully: {test_mep['mep_name']} (ID: {mep_id})")
            else:
                raise Exception("File was not populated after download.")

            # Exit retry loop on success
            break

        except subprocess.CalledProcessError as e:
            print(f"Error on attempt {attempt} for {test_mep['mep_name']} (ID: {mep_id}): {e}")

            # Log error on last attempt
            if attempt == retries:
                with open(error_log, "a") as log:
                    log.write(f"Failed to download {test_mep['mep_name']} (ID: {mep_id}) after {retries} attempts.\n")
            else:
                # Wait a bit before retrying
                time.sleep(2)  # Adjust if needed

    # Wait between downloads to respect Wayback Machine rate limits
    if success:
        time.sleep(10)  # Adjust delay as needed

else:
    print(f"MEP with ID {test_mep_id} not found.")

print("Download completed. Check error log for any failed downloads.")