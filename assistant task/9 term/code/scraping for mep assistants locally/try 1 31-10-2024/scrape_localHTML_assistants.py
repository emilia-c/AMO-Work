import json
import os
from bs4 import BeautifulSoup

from bs4 import BeautifulSoup

class MEP:
    def __init__(self, file_path):
        self.file_path = file_path
        self.name = None
        self.mep_party = None
        self.mep_country = None
        self.assistants = {}  # This will hold the assistants by type

    def get_mep_data(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        # Scrape MEP Name
        name_tag = soup.find('span', class_='ep_name erpl-member-card-full-member-name')
        if name_tag:
            self.name = name_tag.text.strip()

        # Scrape MEP Party
        mep_party_tag = soup.find('div', id='erpl-political-group-name')
        if mep_party_tag:
            self.mep_party = mep_party_tag.text.strip()

        # Scrape MEP Country
        country_tag = soup.find('span', id='erpl-member-country-name')
        if country_tag:
            self.mep_country = country_tag.text.strip()

        # Locate all assistant sections using the erpl_type-assistants structure
        assistants_sections = soup.find_all('div', class_='erpl_type-assistants')
        for section in assistants_sections:
            assistant_type_tag = section.find('h4', class_='erpl_title-h4')
            if assistant_type_tag:
                assistant_type = assistant_type_tag.text.strip()
                # Only capture specific assistant types
                if assistant_type in ["Accredited assistants", "Accredited assistants (grouping)", "Local assistants", "Service providers", "Paying agents"]:
                    self.assistants[assistant_type] = []  # Initialize list for this assistant type
                
                    # Extract assistant names using the ep_name class
                    name_tags = section.find_all('span', class_='ep_name')
                    for name_tag in name_tags:
                        assistant_name = name_tag.text.strip()
                        # Avoid duplicates in the list
                        if assistant_name not in self.assistants[assistant_type]:
                            self.assistants[assistant_type].append(assistant_name)

        # Locate assistant sections using the ep_gridrow-content structure
        grid_content_sections = soup.find_all('div', class_='ep_gridrow-content')
        for grid_section in grid_content_sections:
            # Find the title (e.g., "Accredited assistants") for the assistant type
            assistant_type_tag = grid_section.find('span', class_='ep_name')
            if assistant_type_tag:
                assistant_type = assistant_type_tag.text.strip()
                # Only capture specific assistant types
                if assistant_type in ["Accredited assistants", "Accredited assistants (grouping)", "Local assistants", "Service providers", "Paying agents"]:
                    if assistant_type not in self.assistants:
                        self.assistants[assistant_type] = []  # Initialize list if this type wasn't found before

                    # Extract names under this assistant type using the ep_name class
                    name_tags = grid_section.find_all('span', class_='ep_name')
                    for name_tag in name_tags:
                        name_text = name_tag.text.strip()
                        # Avoid duplicates in the list
                        if name_text not in self.assistants[assistant_type]:
                            self.assistants[assistant_type].append(name_text)

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
    if mep.name:  # Only add if the MEP name was successfully scraped
        meps_list.append(mep.to_dict())
    else:
        print(f"MEP data incomplete in {file_path}")

def save_to_json(meps_list):
    json_filename = "MEPs_9termPLS.json"
    try:
        with open(json_filename, 'w', encoding='utf-8') as json_file:
            json.dump(meps_list, json_file, ensure_ascii=False, indent=4)
        print(f"MEP data saved to {json_filename}")
    except Exception as e:
        print(f"Error saving data to JSON: {e}")

def main(directory):
    meps_list = []
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".html"):
                file_path = os.path.join(root, filename)
                print(f"Processing file: {file_path}")
                get_meps_from_snapshot(file_path, meps_list)

    if meps_list:
        save_to_json(meps_list)
    else:
        print("No MEP data found to save.")

# Example usage
if __name__ == "__main__":
    directory = 'C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/9 term/raw data/mep_assistant_pages_htmls'
    main(directory)
