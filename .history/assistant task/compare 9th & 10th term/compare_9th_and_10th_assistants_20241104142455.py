import json
import pandas as pd

# 1. Load JSON files for each term
def load_mep_data(json_path):
    """Load MEP data from a JSON file."""
    print(f"Loading MEP data from: {json_path}")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            meps_data = json.load(f)
        print(f"Loaded {len(meps_data)} MEPs successfully.")
        return meps_data
    except Exception as e:
        print(f"Failed to load MEP data: {e}")
        exit(1)

data_9th_term = load_mep_data('C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/assistant task/9 term/raw data/mep names and assistants/FINAL_9term_MEPs_with_dates_manual_change.json')
data_10th_term = load_mep_data('C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/assistant task/10 term/raw data/29-10-2024/mep_assistants.json')

# Convert data to DataFrame
df_9th = pd.json_normalize(data_9th_term)
df_9th['term'] = 9  # Add term info
df_10th = pd.json_normalize(data_10th_term)
df_10th['term'] = 10

# Concatenate dataframes
df = pd.concat([df_9th, df_10th], ignore_index=True)