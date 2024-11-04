2024_assistants.json - raw json file of 719 meps (not sure why there are not 720, I will fix this manually in the dataframe I am making from the json)

10term_assistants_extraction.py 
- code that extracts the mep information and based on mep_api which is available on github (https://github.com/mgutmann/mep_api)
- all information (mep name, assistants, assistant type, mep party) is taken from the assistants page of the meps
- the code also reconstructs the urls to get to said assistant pages based on a full list of meps