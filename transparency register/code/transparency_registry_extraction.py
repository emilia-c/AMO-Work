import xml.etree.ElementTree as ET
import requests
import pandas as pd

# List of XML file URLs
xml_urls = [
    "https://data.europa.eu/euodp/en/data/storage/f/2024-07-03T094150/ODP_30-06-2024.xml",
    #"https://data.europa.eu/euodp/en/data/storage/f/2024-05-14T111116/Organisations%20in%20Transparency%20Register-2024-JAN.xml"
]

# Function to parse XML and extract specific fields
def parse_xml_extract_fields(root):
    data = []

    for entity in root.findall('.//interestRepresentative'):
        identification_code = entity.findtext('identificationCode', default="N/A")
        registration_date = entity.findtext('registrationDate', default="N/A")
        category_of_registration = entity.findtext('registrationCategory', default="N/A")
        name = entity.find('.//name/originalName').text if entity.find('.//name/originalName') is not None else "N/A"
        acronym = entity.findtext('acronym', default="N/A")
        head_office_city = entity.findtext('.//headOffice/city', default="N/A")
        head_office_country = entity.findtext('.//headOffice/country', default="N/A")
        
        data.append({
            'transparency_no': identification_code,
            'reg_date': registration_date,
            'name': name,
            'acronym': acronym,
            'hq_city': head_office_city,
            'hq_country': head_office_country
        })

    return pd.DataFrame(data)

# List to collect DataFrames from each file
all_dfs = []

# Loop through each XML URL
for url in xml_urls:
    # Fetch the XML data
    response = requests.get(url)
    response.raise_for_status()

    # Parse XML data from response content
    root = ET.fromstring(response.content)

    # Extract fields and create DataFrame for this XML file
    df = parse_xml_extract_fields(root)
    all_dfs.append(df)

# Concatenate all DataFrames from the list
combined_df = pd.concat(all_dfs, ignore_index=True)

# Drop duplicates based on transparency_no (or adjust based on unique identifier)
#unique_df = combined_df.drop_duplicates(subset='transparency_no', keep='first')
print(combined_df)
# clean of whitespace and all to lowercase 
#unique_df['name'] = unique_df['name'].str.replace(r'\n+', ' ', regex=True).str.strip()
#unique_df['name'] = unique_df['name'].str.lower().str.strip()

# Save the unique DataFrame to an Excel file
#unique_df.to_excel('2024_registered_orgs.xlsx', index=False, engine='openpyxl')