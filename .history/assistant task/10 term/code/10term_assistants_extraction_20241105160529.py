import requests
from bs4 import BeautifulSoup
import json
import time
from tqdm import tqdm

# STEP 1: SCRAPE ALL OF THE DATA 
# Scrape all the MEP information wanted (MEP name, MEP group, MEP national party, MEP country of origin, assistant names, assistant type)
class MEP:
    def __init__(self, url):
        self.url = url
        self.name = None
        self.mep_group = None
        self.mep_national_party = None
        self.mep_country = None
        self.assistants = {}

    def get_mep_data(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Scrape MEP Name
        name_tag = soup.find('span', class_='sln-member-name')
        if name_tag:
            self.name = name_tag.text.strip()
        else:
            print(f"Warning: MEP name not found for {self.url}")

        # Scrape MEP Group
        mep_group_tag = soup.find('h3', class_='erpl_title-h3 mt-1 sln-political-group-name')
        if mep_group_tag:
            self.mep_group = mep_group_tag.text.strip()
        else:
            print(f"Warning: MEP Group information not found for {self.url}")
        
        # Scrape MEP National Party
        mep_national_party_tag = soup.find('div', class_='erpl_title-h3 mt-1 mb-1')
        if mep_national_party_tag:
            national_party_text = mep_national_party_tag.text.strip()
            if " - " in national_party_text:
                # Extract the text before the parentheses and after the hyphen
                self.mep_national_party = national_party_text.split(" - ")[1].split(" (")[0]
            else:
                print(f"Warning: MEP National Party information not found or formatted incorrectly for {self.url}")

        # Scrape MEP Country
        if mep_national_party_tag:
            country_text = mep_national_party_tag.text.strip()
            if "(" in country_text and ")" in country_text:
                self.mep_country = country_text[country_text.find("(")+1:country_text.find(")")]

        # Locate all assistant sections
        assistants_sections = soup.find_all('div', class_='erpl_type-assistants')
        for section in assistants_sections:
            assistant_type = section.find('h4', class_='erpl_title-h4').text.strip()
            self.assistants[assistant_type] = []
            
            # Extract assistant names
            for assistant_tag in section.find_all('div', class_='erpl_type-assistants-item'):
                assistant_name = assistant_tag.find('span', class_='erpl_assistant').text.strip()
                self.assistants[assistant_type].append(assistant_name)

    def to_dict(self):
        # Create a dictionary representation of the MEP data
        return {
            "name": self.name,
            "mep_group": self.mep_group,
            "mep_national_party": self.mep_national_party,
            "country": self.mep_country,
            "assistants": self.assistants
        }

# construct the MEP url from the base url of a list of all MEPs, need to extract their name from here as the page with asssitant information includes their information
def construct_mep_url(mep_name, mep_id):
    names = mep_name.split()
    first_names = []
    last_names = []

    for name in names:
        if name.isupper():
            last_names.append(name)
        else:
            first_names.append(name)

    first_name_part = '+'.join(first_names)
    last_name_part = '+'.join(last_names)

    if last_names:
        if first_names:
            return f"https://www.europarl.europa.eu/meps/en/{mep_id}/{first_name_part}+{last_name_part}/assistants#detailedcardmep"
        else:
            return f"https://www.europarl.europa.eu/meps/en/{mep_id}/{last_name_part}/assistants#detailedcardmep"
    else:
        return f"https://www.europarl.europa.eu/meps/en/{mep_id}/{first_name_part}/home"

def get_mep_links():
    base_url = "https://www.europarl.europa.eu/meps/en/full-list/all"
    response = requests.get(base_url)
    response.raise_for_status()  # Raise an error for bad responses
    soup = BeautifulSoup(response.content, 'html.parser')
    
    mep_links = []
    for mep in soup.select('a.erpl_member-list-item-content'):
        mep_url_base = mep['href']
        mep_name = mep.select_one('.erpl_title-h4.t-item').text.strip()
        mep_id = mep_url_base.split('/')[-1]
        mep_url = construct_mep_url(mep_name, mep_id)
        mep_links.append(mep_url)

    return mep_links

# RUNNING THE THING
def scrape_meps(url):
    mep = MEP(url)
    mep.get_mep_data()
    return mep.to_dict()  # Return dictionary directly

def main():
    mep_links = get_mep_links()  # Get all MEP links

    # Limit to the first five MEPs for testing
    mep_links = mep_links[:5]

    all_mep_data = []  # List to hold all MEP data as dictionaries

    # Use tqdm to show a progress bar for scraping MEP assistants
    for mep_url in tqdm(mep_links, desc="Scraping MEPs"):
        mep_data = scrape_meps(mep_url)  # Get data for each MEP
        all_mep_data.append(mep_data)  # Append MEP data dictionary to the list
        time.sleep(1)  # Optional: Add delay to avoid overwhelming the server

    # Save the data to a JSON file
    with open("mep_assistants_national_party.json", "w", encoding="utf-8") as outfile:
        json.dump(all_mep_data, outfile, ensure_ascii=False, indent=4)

    print(json.dumps(all_mep_data, indent=4, ensure_ascii=False))  # Print the result to console

if __name__ == "__main__":
    main()    
