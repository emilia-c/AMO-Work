import requests
import xml.etree.ElementTree as ET

# Fetch the XML data from the URL
response = requests.get("https://www.europarl.europa.eu/meps/en/full-list/xml/")
root = ET.fromstring(response.content)

# Iterate over each 'mep' element to print more detailed data
for mep in root.findall(".//mep"):
    print("MEP:")
    for detail in mep:
        print(f"  {detail.tag}: {detail.text}")
    print("\n")
