import json
import os
from bs4 import BeautifulSoup

class MEP:
    def __init__(self, file_path):
        self.file_path = file_path
        self.name = None
        self.mep_group = None
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

            # Scrape MEP Name from multiple possible locations
            name_tag = soup.find('span', class_='ep_name erpl-member-card-full-member-name') or \
                       soup.find('span', class_='sln-member-name') or \
                       soup.find('div', class_='erpl_title-h1 mt-1')
            self.name = name_tag.get_text(strip=True) if name_tag else None
            if not self.name:
                self.log_error("MEP name not found.")

            # Scrape MEP Party - handle multiple structures
            mep_group_tag = soup.find('div', id='erpl-political-group-name') or \
                            soup.find('h3', class_='sln-political-group-name') or \
                            soup.find('h3', class_='erpl_title-h3 mt-1')
            self.mep_group = mep_group_tag.get_text(strip=True) if mep_group_tag else None
            if not self.mep_group:
                self.log_error("MEP group not found.")

            # Scrape MEP Country and National Party
            # First method using the original structure
            country_party_tag = soup.find('div', class_='erpl_title-h3 mt-1 mb-1')
            if country_party_tag:
                full_text = country_party_tag.get_text(separator=" ", strip=True).replace("\n", " ").replace("\t", " ").strip()
                parts = full_text.split(" - ", 1)
                self.country = parts[0].strip() if len(parts) > 0 else None
                self.national_party = parts[1].split(" (")[0].strip() if len(parts) > 1 else None

            # Second method using the alternative structure
            if not self.country or not self.national_party:
                country_party_section = soup.find('div', class_='ep-a_heading ep-layout_level2')
                if country_party_section:
                    country_tag = country_party_section.find('span', id='erpl-member-country-name')
                    self.country = country_tag.get_text(strip=True) if country_tag else None
                    full_text = country_party_section.get_text(separator=" ", strip=True)
                    parts = full_text.split(" - ", 1)
                    self.national_party = parts[1].split(" (")[0].strip() if len(parts) > 1 else None

            # Logging if extraction failed
            if not self.country:
                self.log_error("MEP country not found.")
            if not self.national_party:
                self.log_error("MEP national party not found.")

            # Existing code for extracting assistants follows
            assistants_sections = soup.find_all('div', class_='ep_gridcolumn-content')
            for section in assistants_sections:
                assistant_type_tag = section.find_previous('span', class_='ep_name')
                assistant_type = assistant_type_tag.get_text(strip=True) if assistant_type_tag else None

                if assistant_type in ["Accredited assistants", "Accredited assistants (grouping)", "Local assistants", "Service providers", "Paying agents"]:
                    if assistant_type not in self.assistants:
                        self.assistants[assistant_type] = []

                    name_tags = section.find_all('li')
                    for li in name_tags:
                        assistant_name_tag = li.find('span', class_='ep_name')
                        if assistant_name_tag:
                            assistant_name = assistant_name_tag.get_text(strip=True)
                            if assistant_name not in self.assistants[assistant_type]:
                                self.assistants[assistant_type].append(assistant_name)

            # List of valid assistant types
            valid_assistant_types = ["Accredited assistants", "Accredited assistants (grouping)", "Local assistants", "Service providers", "Paying agents"]

            # New method to find assistants in the second structure with dynamic assistant type extraction
            accredited_assistants_sections = soup.find_all('h4', class_='erpl_title-h4')  # Find all titles with the class 'erpl_title-h4'
            
            for section in accredited_assistants_sections:
                # Dynamically get the assistant type from the heading
                assistant_type = section.get_text(strip=True)  # e.g., "Accredited assistants"
                
                # Check if the assistant type is in the valid list
                if assistant_type in valid_assistant_types:
                    # Initialize the assistant type in the dictionary if it doesn't exist
                    if assistant_type not in self.assistants:
                        self.assistants[assistant_type] = []

                    # Find the container with the assistants (div with class 'erpl_type-assistants')
                    accredited_assistants_section = section.find_next('div', class_='erpl_type-assistants')
                    if accredited_assistants_section:
                        # Extract assistant names from <span class="erpl_assistant">
                        print(accredited_assistants_section.prettify())
                        assistant_tags = accredited_assistants_section.find_all('span', class_='erpl_assistant')
                        for assistant_tag in assistant_tags:
                            assistant_name = assistant_tag.get_text(strip=True)  # Get the text inside the span
                            if assistant_name and assistant_name not in self.assistants[assistant_type]:
                                self.assistants[assistant_type].append(assistant_name)

                    # If no assistants are found under this type, the list remains empty
                               
        except Exception as e:
            self.log_error(f"Unexpected error during MEP data extraction: {e}")

    def to_dict(self):
        return {
            "name": self.name,
            "group": self.mep_group,
            "country": self.country,
            "national_party": self.national_party,
            "assistants": self.assistants
        }

def get_meps_from_snapshot(file_path, meps_list):
    mep = MEP(file_path)
    mep.get_mep_data()
    meps_list.append(mep.to_dict())

def save_to_json(meps_list):
    json_filename = "9term_apas_w_nationalParty_noMANUAL2.json"
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
    empty_directories = 0  # Counter for directories with no HTML files

    # Clear the log file at the start of each run
    open("error_log.txt", "w").close()

    for root, _, files in os.walk(directory):
        html_files = [file for file in files if file.endswith(".html")]
        
        # Check if the current directory has no HTML files
        if not html_files:
            empty_directories += 1
            with open("error_log.txt", "a", encoding="utf-8") as log_file:
                log_file.write(f"Directory '{root}' is empty or contains no HTML files.\n")
            continue  # Skip to the next directory

        # Process HTML files in this directory
        for filename in html_files: 
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
    print(f"Encountered {empty_directories} empty directories (no HTML files found).")
    print(f"Check 'error_log.txt' for details on any errors encountered.")

# Example usage
if __name__ == "__main__":
    directory = 'C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/assistant task/9 term/raw data/scraped html assistant pages'
    main(directory)