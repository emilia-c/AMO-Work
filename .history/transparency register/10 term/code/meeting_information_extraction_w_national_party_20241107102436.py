from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import json
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

class MEP:
    def __init__(self, url):
        self.url = url
        self.name = None
        self.group = None  # Changed from 'mep_party' to 'group'
        self.mep_country = None
        self.mep_national_party = None  # New variable for national party
        self.meetings = {}
        
        # Setup Selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
        chrome_options.add_argument("start-maximized")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(service=ChromeService(), options=chrome_options)

    def get_mep_data(self):
        self.driver.get(self.url)
        time.sleep(3)  # Wait for the page to load
        
        # Scrape MEP Name
        name_tag = self.driver.find_element(By.CSS_SELECTOR, 'span.sln-member-name')
        if name_tag:
            self.name = name_tag.text.strip()

        # Scrape MEP Group (formerly party)
        group_tag = self.driver.find_element(By.CSS_SELECTOR, 'h3.erpl_title-h3.mt-1.sln-political-group-name')
        if group_tag:
            self.group = group_tag.text.strip()

        # Scrape MEP Country
        mep_country_tag = self.driver.find_element(By.CSS_SELECTOR, 'div.erpl_title-h3.mt-1.mb-1')
        if mep_country_tag:
            country_text = mep_country_tag.text.strip()
            last_open_index = country_text.rfind("(")
            last_close_index = country_text.rfind(")")
        
            if last_open_index != -1 and last_close_index != -1 and last_open_index < last_close_index:
                self.mep_country = country_text[last_open_index + 1:last_close_index].strip()
            else:
                self.mep_country = "N/A"  # Fallback in case the format is unexpected

        # Scrape MEP National Party
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        mep_national_party_tag = soup.find('div', class_='erpl_title-h3 mt-1 mb-1')
        if mep_national_party_tag:
            national_party_text = mep_national_party_tag.text.strip()
            if " - " in national_party_text:
                # Extract the text before the parentheses and after the hyphen
                self.mep_national_party = national_party_text.split(" - ")[1].split(" (")[0]
            else:
                print(f"Warning: MEP National Party information not found or formatted incorrectly for {self.url}")

        # Load all meetings
        self.load_meetings()

    def load_meetings(self):
        while True:
            try:
                # Wait for the Load More button to be present
                load_more_button = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'europarl-expandable-async-loadmore')]"))
                )

                # Scroll into view
                self.driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                time.sleep(1)  # Ensure the button is visible

                # Wait until the button is visible and enabled
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of(load_more_button)
                )
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(load_more_button)
                )

                # Click using JavaScript
                self.driver.execute_script("arguments[0].click();", load_more_button)

                # Allow time for new meetings to load
                time.sleep(2)

            except TimeoutException:
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                break

        # Now extract all meeting data
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        meeting_elements = soup.find_all('div', class_='erpl_document')
        
        for idx, meeting_element in enumerate(meeting_elements):
            meeting_data = {}

            # Meeting reason (title within span.t-item inside h3)
            reason_tag = meeting_element.find('h3', class_='erpl_document-title erpl_title-h3 mb-1 a-i')
            if reason_tag:
                reason_text = reason_tag.find('span', class_='t-item')
                if reason_text:
                    meeting_data['reason'] = reason_text.text.strip()

            # Date and place
            date_place_tag = meeting_element.find('div', class_='erpl_document-subtitle d-inline')
            if date_place_tag:
                date_tag = date_place_tag.find('time')
                place_tag = date_place_tag.find('span', class_='erpl_document-subtitle-location')
                if date_tag:
                    meeting_data['date'] = date_tag.text.strip()
                if place_tag:
                    meeting_data['place'] = place_tag.text.strip()

            # Capacity
            capacity_tag = meeting_element.find('span', class_='erpl_document-subtitle-capacity')
            if capacity_tag:
                meeting_data['capacity'] = capacity_tag.text.strip()

            # Committee code
            committee_tag = meeting_element.find('span', class_='erpl_badge erpl_badge-committee')
            if committee_tag:
                meeting_data['committee_code'] = committee_tag.text.strip()

            # Meeting with
            meeting_with_tag = meeting_element.find('span', class_='erpl_document-subtitle-author')
            if meeting_with_tag:
                meeting_data['meeting_with'] = meeting_with_tag.text.strip()

            # Store meeting data in self.meetings with a unique key
            self.meetings[f"{idx}"] = meeting_data

    def to_dict(self):
        return {
            "name": self.name,
            "group": self.group,  # Changed from 'party' to 'group'
            "origin_country": self.mep_country,
            "national_party": self.mep_national_party,  # Include national party in the dictionary
            "meetings": self.meetings
        }

    def close(self):
        self.driver.quit()  # Close the browser when done

# construct the MEP url from the base url of a list of all MEPs, need to extract their name from here as the page with assistant information includes their information
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
            return f"https://www.europarl.europa.eu/meps/en/{mep_id}/{first_name_part}+{last_name_part}/meetings/past#detailedcardmep"
        else:
            return f"https://www.europarl.europa.eu/meps/en/{mep_id}/{last_name_part}/meetings/past#detailedcardmep"
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

def scrape_meps(url):
    mep = MEP(url)
    mep.get_mep_data()
    return mep.to_dict()

def main():
    # Example URLs for MEPs
    mep_links = get_mep_links()  # Get all MEP links

    # Limit to the first five MEPs for testing
    #mep_links = mep_links[:5]

    all_mep_data = []  # List to hold all MEP data as dictionaries

    for mep_url in tqdm(mep_links, desc="Scraping MEPs"):
        mep_data = scrape_meps(mep_url)
        all_mep_data.append(mep_data)
        time.sleep(1)  # Optional: To avoid overwhelming the server

    with open("mep_meetings_FULL_w_nationalParty.json", "w", encoding="utf-8") as outfile:
        json.dump(all_mep_data, outfile, indent=4, ensure_ascii=False)


    print(json.dumps(all_mep_data, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()