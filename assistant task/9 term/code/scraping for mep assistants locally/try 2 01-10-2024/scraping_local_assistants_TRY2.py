import json
import os
from bs4 import BeautifulSoup

class MEP:
    def __init__(self, file_path):
        self.file_path = file_path
        self.name = None
        self.mep_party = None
        self.mep_country = None
        self.assistants = {}  # This will hold assistants by type

    def log_error(self, message):
        """Log errors with specific messages for debugging purposes."""
        with open("error_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"File: {self.file_path}, MEP Name: {self.name or 'N/A'}, Error: {message}\n")

    def get_mep_data(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

            # Scrape MEP Name from multiple possible locations
            name_tag = soup.find('span', class_='ep_name erpl-member-card-full-member-name') or \
                       soup.find('span', class_='sln-member-name') or \
                       soup.find('div', class_='erpl_title-h1 mt-1')
            self.name = name_tag.get_text(strip=True) if name_tag else None
            if not self.name:
                self.log_error("MEP name not found.")

            # Scrape MEP Party - handle multiple structures
            mep_party_tag = soup.find('div', id='erpl-political-group-name') or \
                            soup.find('h3', class_='sln-political-group-name') or \
                            soup.find('h3', class_='erpl_title-h3 mt-1')
            self.mep_party = mep_party_tag.get_text(strip=True) if mep_party_tag else None
            if not self.mep_party:
                self.log_error("MEP party not found.")

            # Scrape MEP Country - handle multiple structures
            country_tag = soup.find('span', id='erpl-member-country-name') or \
                          soup.find('div', class_='erpl_title-h3 mt-1 mb-1')
            self.mep_country = country_tag.get_text(strip=True) if country_tag else None
            if not self.mep_country:
                self.log_error("MEP country not found.")

            # Existing method to find assistants in the first structure
            assistants_sections = soup.find_all('div', class_='ep_gridcolumn-content')
            for section in assistants_sections:
                # Find the type of assistants by looking for a preceding ep_name tag
                assistant_type_tag = section.find_previous('span', class_='ep_name')
                assistant_type = assistant_type_tag.get_text(strip=True) if assistant_type_tag else None
                
                if assistant_type in ["Accredited assistants", "Accredited assistants (grouping)", "Local assistants", "Service providers", "Paying agents"]:
                    if assistant_type not in self.assistants:
                        self.assistants[assistant_type] = []

                    # Extract each assistant's name within the list structure
                    name_tags = section.find_all('li')
                    for li in name_tags:
                        assistant_name_tag = li.find('span', class_='ep_name')
                        if assistant_name_tag:
                            assistant_name = assistant_name_tag.get_text(strip=True)
                            if assistant_name not in self.assistants[assistant_type]:  # Avoid duplicates
                                self.assistants[assistant_type].append(assistant_name)

            # New method to find assistants in the second structure
            accredited_assistants_section = soup.find('div', class_='erpl_type-assistants')
            if accredited_assistants_section:
                # We can assume the type here is "Accredited assistants"
                assistant_type = "Accredited assistants"
                if assistant_type not in self.assistants:
                    self.assistants[assistant_type] = []

                # Extract assistant names from the new structure
                assistant_tags = accredited_assistants_section.find_all('span', class_='erpl_assistant')
                for assistant_tag in assistant_tags:
                    assistant_name = assistant_tag.get_text(strip=True)
                    if assistant_name not in self.assistants[assistant_type]:  # Avoid duplicates
                        self.assistants[assistant_type].append(assistant_name)

        except Exception as e:
            self.log_error(f"Unexpected error during MEP data extraction: {e}")

    def to_dict(self):
        return {
            "name": self.name,
            "party": self.mep_party,
            "country": self.mep_country,
            "assistants": self.assistants
        }

def get_meps_from_snapshot(file_path, meps_list):
    mep = MEP(file_path)
    mep.get_mep_data()
    meps_list.append(mep.to_dict())

def save_to_json(meps_list):
    json_filename = "MEPs_9term_AREYOUTHERE.json"
    try:
        with open(json_filename, 'w', encoding='utf-8') as json_file:
            json.dump(meps_list, json_file, ensure_ascii=False, indent=4)
        print(f"MEP data saved to {json_filename}")
    except Exception as e:
        with open("error_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"Error saving data to JSON: {e}\n")
        print(f"Error saving data to JSON: {e}")

def main(directory):
    meps_list = []
    total_files = 0

    # Clear the log file at the start of each run
    open("error_log.txt", "w").close()

    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".html"):
                file_path = os.path.join(root, filename)
                total_files += 1
                try:
                    get_meps_from_snapshot(file_path, meps_list)
                except Exception as e:
                    with open("error_log.txt", "a", encoding="utf-8") as log_file:
                        log_file.write(f"Error with file {file_path}: {e}\n")

    # Save data if available
    if meps_list:
        save_to_json(meps_list)
    
    # Summary of results
    print(f"Processed {total_files} files.")
    print(f"Successfully saved data for {len(meps_list)} MEPs.")
    print(f"Check 'error_log.txt' for details on any errors encountered.")

# Example usage
if __name__ == "__main__":
    directory = 'C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/9 term/raw data/mep_assistant_pages_htmls'
    main(directory)