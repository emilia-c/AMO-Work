import os
import json
from bs4 import BeautifulSoup

def get_meps_from_snapshot(snapshot_file_path, snapshot_date_str, meps_list):
    """Get MEP names, IDs, and date from a specific snapshot file."""
    try:
        # Read the HTML file locally
        with open(snapshot_file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        # Extract all MEP information from the HTML
        for mep_link in soup.find_all("a", class_="erpl_member-list-item-content"):
            # Extract the MEP name
            name_div = mep_link.find("div", class_="erpl_title-h4 t-item")
            if name_div:
                mep_name = name_div.text.strip()
                
                # Extract the MEP ID from the href attribute
                mep_href = mep_link["href"]  # Get the href link
                mep_id = mep_href.split("/")[-1]  # Extracting the ID from the URL

                # Append MEP details to the list
                meps_list.append({
                    "mep_id": mep_id,
                    "mep_name": mep_name,
                    "date_scraped": snapshot_date_str  # Set the date to the snapshot date
                })

    except Exception as e:
        print(f"Error fetching data from {snapshot_file_path}: {e}")

def save_to_json(meps_list):
    """Save the MEP list to a JSON file."""
    json_filename = "MEPs_2021-2024.json"
    try:
        with open(json_filename, 'w', encoding='utf-8') as json_file:
            json.dump(meps_list, json_file, ensure_ascii=False, indent=4)
        print(f"MEP data saved to {json_filename}")
    except Exception as e:
        print(f"Error saving data to JSON: {e}")

# Main function to iterate over files in a directory
def main(directory):
    meps_list = []  # Initialize a list to store MEP details
    # Iterate over all HTML files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".html"):  # Check for HTML files
            file_path = os.path.join(directory, filename)

            # Extract the snapshot date from the filename (assuming format is YYYY-MM-DD.html)
            snapshot_date_str = filename[:-5]  # Remove the '.html' part
            print(f"Processing {file_path} with date {snapshot_date_str}...")
            
            get_meps_from_snapshot(file_path, snapshot_date_str, meps_list)

    # Save all MEPs to a single JSON file after processing all files
    save_to_json(meps_list)

# Example usage
if __name__ == "__main__":
    # Specify the directory where your HTML files are stored
    directory = 'C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/9 term/cache'  # Update this to your directory

    main(directory)
