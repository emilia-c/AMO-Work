Here is the logic for this folder: 

1) I tried first to scrape the sites directly using 9term_mepNames_extraction (scraping wayback directly folder). This was only able to get me MEP names from 2019-2020 before the wayback archive blocked me. 
This python code resulted in the json file mep_names_and_ids_2019.2020.json. 

2) So, I realized that it would be more efficient to download the htmls directly which led to the creation of download_mep_html_locally (downloading htmls folder). 

3) After the htmls were cached and I could scrape them locally they were scraped with extract_mep_names_2021-2024.py (scraping locally folder).
This python code resulted in the json file mep_names_and_ids_2019.2020.json. 

4) I had to merge the two JSON files which was done with the file merge_mep_jsons.py.
Running this code resulted in the file merged_mep_9term.json. 


Note: For a while I thought I could only download with ruby but I could not get it to work. The code I was testing with can be found in the folder 'testing with ruby'. 