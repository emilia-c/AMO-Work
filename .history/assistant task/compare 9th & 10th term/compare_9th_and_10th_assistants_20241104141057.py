import json
import pandas as pd

# Load JSON files for each term
with open('C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/assistant task/9 term/raw data/mep names and assistants/FINAL_9term_MEPs_with_dates_manual_change.json') as file:
    data_9th_term = json.load(file)

with open('C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/assistant task/10 term/raw data/29-10-2024/mep_assistants.json') as file:
    data_10th_term = json.load(file)

# Convert data to DataFrame
df_9th = pd.json_normalize(data_9th_term)
df_9th['term'] = 9  # Add term info
df_10th = pd.json_normalize(data_10th_term)
df_10th['term'] = 10

# Concatenate dataframes
df = pd.concat([df_9th, df_10th], ignore_index=True)
