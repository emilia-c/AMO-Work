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
            group_tag = (
                soup.find('h3', class_='sln-political-group-name') or
                soup.find('div', id='erpl-political-group-name') or 
                soup.find('h3', class_='erpl_title-h3 mt-1')
            )

            self.group = group_tag.get_text(strip=True) if group_tag else None
            if not self.group:
                self.log_error("MEP group not found.")

            # Scrape MEP Country and National Party
            country_party_tag = soup.find('div', class_='erpl_title-h3 mt-1 mb-1')
            if country_party_tag:
                full_text = country_party_tag.get_text(separator=" ", strip=True).replace("\n", " ").replace("\t", " ").strip()
                parts = full_text.split(" - ", 1)
                self.country = parts[0].strip() if len(parts) > 0 else None
                self.national_party = parts[1].split(" (")[0].strip() if len(parts) > 1 else None

            # First method (using ep_gridcolumn-content structure)
            assistants_sections = soup.find_all('div', class_='ep_gridcolumn-content')
            for section in assistants_sections:
                # Find the assistant type (e.g., Accredited assistants, Local assistants)
                assistant_type_tag = section.find_previous('span', class_='ep_name')
                assistant_type = assistant_type_tag.get_text(strip=True) if assistant_type_tag else None

                # Only proceed if the assistant type is one of the recognized ones
                if assistant_type in ["Accredited assistants", "Local assistants", "Service providers", "Paying agents"]:
                    if assistant_type not in self.assistants:
                        self.assistants[assistant_type] = []

                    name_tags = section.find_all('li')
                    for li in name_tags:
                        assistant_name_tag = li.find('span', class_='ep_name')
                        if assistant_name_tag:
                            assistant_name = assistant_name_tag.get_text(strip=True)
                            if assistant_name not in self.assistants[assistant_type]:  # Avoid duplicates
                                self.assistants[assistant_type].append(assistant_name)

            # Second method (using erpl_type-assistants structure for Accredited assistants)
            accredited_assistants_section = soup.find('div', class_='erpl_type-assistants')
            if accredited_assistants_section:
                assistant_type = "Accredited assistants"
                if assistant_type not in self.assistants:
                    self.assistants[assistant_type] = []

                assistant_tags = accredited_assistants_section.find_all('span', class_='erpl_assistant')
                for assistant_tag in assistant_tags:
                    assistant_name = assistant_tag.get_text(strip=True)
                    if assistant_name not in self.assistants[assistant_type]:  # Avoid duplicates
                        self.assistants[assistant_type].append(assistant_name)

            # New method to find "Accredited assistants (grouping)" in a separate structure
            accredited_assistants_grouping_section = soup.find('h4', class_='erpl_title-h4', string="Accredited assistants (grouping)")
            if accredited_assistants_grouping_section:
                assistant_type = "Accredited assistants (grouping)"
                if assistant_type not in self.assistants:
                    self.assistants[assistant_type] = []

                # Find assistants under "Accredited assistants (grouping)"
                assistant_tags = accredited_assistants_grouping_section.find_next('div', class_='erpl_type-assistants-item').find_all('span', class_='erpl_assistant')
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
        with open("error_log_9term.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"Error saving data to JSON: {e}\n")
        print(f"Error saving data to JSON: {e}")

def main(directory):
    meps_list = []
    total_files = 0
    empty_directories = 0  # Counter for directories with no HTML files

    # Clear the log file at the start of each run
    open("error_log.txt", "w").close()

    # Check if the specified directory exists
    if not os.path.isdir(directory):
        print(f"Directory '{directory}' does not exist.")
        with open("error_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"Directory '{directory}' does not exist.\n")
        return

    for root, _, files in os.walk(directory):
        html_files = [file for file in files if file.endswith(".html")]
        
        # Check if the current directory has no HTML files
        if not html_files:
            empty_directories += 1
            with open("error_log.txt", "a", encoding="utf-8") as log_file:
                log_file.write(f"Directory '{root}' is empty or contains no HTML files.\n")
            continue  # Skip to the next directory

        # Process HTML files in this directory
        for filename in html_files[:]:  # Limit to the first 10 files for testing
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