import json
import os
from bs4 import BeautifulSoup

class MEP:
    def __init__(self, file_path):
        self.file_path = file_path
        self.name = None
        self.group = None
        self.country = None
        self.national_party = None
        self.assistants = {}

    def log_error(self, message):
        """Log errors with specific messages for debugging purposes."""
        with open("error_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"File: {self.file_path}, MEP Name: {self.name or 'N/A'}, Error: {message}\n")

    def get_mep_data(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

            # Scrape MEP Name
            name_tag = (
                soup.find('span', class_='sln-member-name') or
                soup.find('div', class_='erpl_title-h1 mt-1') or
                soup.find('span', class_='ep_name erpl-member-card-full-member-name')
            )

            self.name = name_tag.get_text(strip=True) if name_tag else None
            if not self.name:
                self.log_error("MEP name not found.")


            # Scrape MEP Group
            group_tag = soup.find('h3', class_='sln-political-group-name')
            self.group = group_tag.get_text(strip=True) if group_tag else None
            if not self.group:
                self.log_error("MEP group not found.")

            # Scrape MEP Country and National Party
            country_party_tag = soup.find('div', class_='erpl_title-h3 mt-1 mb-1')
            if country_party_tag:
                # Remove newline, tab characters, and extra spaces
                full_text = country_party_tag.get_text(separator=" ", strip=True).replace("\n", " ").replace("\t", " ").strip()
                
                # Split by " - " to get the country and national party
                parts = full_text.split(" - ", 1)

                self.country = parts[0].strip() if len(parts) > 0 else None
                self.national_party = parts[1].split(" (")[0].strip() if len(parts) > 1 else None

                if not self.country:
                    self.log_error("MEP country not found.")
                if not self.national_party:
                    self.log_error("MEP national party not found.")
            else:
                self.log_error("Country and National Party section not found.")

            # Existing method to find assistants in the first structure
            assistants_sections = soup.find_all('div', class_='ep_gridcolumn-content')
            for section in assistants_sections:
                assistant_type_tag = section.find_previous('span', class_='ep_name')
                assistant_type = assistant_type_tag.get_text(strip=True) if assistant_type_tag else None

                if assistant_type in ["Accredited assistants", "Local assistants", "Service providers", "Paying agents"]:
                    if assistant_type not in self.assistants:
                        self.assistants[assistant_type] = []

                    name_tags = section.find_all('li')
                    for li in name_tags:
                        assistant_name_tag = li.find('span', class_='ep_name')
                        if assistant_name_tag:
                            assistant_name = assistant_name_tag.get_text(strip=True)
                            if assistant_name not in self.assistants[assistant_type]:
                                self.assistants[assistant_type].append(assistant_name)

            # New method to find assistants in the second structure
            accredited_assistants_section = soup.find('div', class_='erpl_type-assistants')
            if accredited_assistants_section:
                assistant_type = "Accredited assistants"
                if assistant_type not in self.assistants:
                    self.assistants[assistant_type] = []

                assistant_tags = accredited_assistants_section.find_all('span', class_='erpl_assistant')
                for assistant_tag in assistant_tags:
                    assistant_name = assistant_tag.get_text(strip=True)
                    if assistant_name not in self.assistants[assistant_type]:
                        self.assistants[assistant_type].append(assistant_name)

        except Exception as e:
            self.log_error(f"Unexpected error during MEP data extraction: {e}")

    def to_dict(self):
        return {
            "name": self.name,
            "group": self.group,
            "country": self.country,
            "national_party": self.national_party,
            "assistants": self.assistants
        }

def get_meps_from_snapshot(file_path, meps_list):
    mep = MEP(file_path)
    mep.get_mep_data()
    meps_list.append(mep.to_dict())

def save_to_json(meps_list):
    json_filename = "9term_apas_w_nationalParty.json"
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
        for filename in files[:10]:  # For testing with the first 10 files
            if filename.endswith(".html"):
                file_path = os.path.join(root, filename)
                total_files += 1
                try:
                    get_meps_from_snapshot(file_path, meps_list)
                except Exception as e:
                    with open("error_log.txt", "a", encoding="utf-8") as log_file:
                        log_file.write(f"Error with file {file_path}: {e}\n")

    if meps_list:
        save_to_json(meps_list)
    
    print(f"Processed {total_files} files.")
    print(f"Successfully saved data for {len(meps_list)} MEPs.")
    print(f"Check 'error_log.txt' for details on any errors encountered.")

# Example usage
if __name__ == "__main__":
    directory = 'C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/assistant task/9 term/raw data/scraped html assistant pages'
    main(directory)