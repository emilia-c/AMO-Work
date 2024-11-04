import json
import os
import pandas as pd

# 1. Load JSON files for each term
def load_mep_data(json_path):
    """Load MEP data from a JSON file."""
    print(f"Loading MEP data from: {json_path}")
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        exit(1)
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            file_content = f.read().strip()  # Strip any extra whitespace
            if not file_content:
                raise ValueError("File is empty")
            
            # Validate JSON by loading
            meps_data = json.loads(file_content)  
            print(f"Loaded {len(meps_data)} MEPs successfully.")
            return meps_data
    
    except json.JSONDecodeError as e:
        print(f"JSON decode error at character {e.pos}: {e}")
    except ValueError as e:
        print(f"ValueError: {e}")
    except Exception as e:
        print(f"Failed to load MEP data: {e}")
    exit(1)

# File paths (replace with your paths)
data_9th_term = load_mep_data('C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/assistant task/9 term/raw data/final/9TERM_ALL_STANDARDIZED.json')
data_10th_term = load_mep_data('C:/Users/Emilia/Documents/Uni Helsinki/Year Three/AMO Freelance/assistant task/10 term/raw data/29-10-2024/mep_assistants.json')

# Convert data to DataFrame
df_9th = pd.json_normalize(data_9th_term)
df_9th['term'] = 9  # Add term info
df_10th = pd.json_normalize(data_10th_term)
df_10th['term'] = 10

# Concatenate dataframes
all_meps = pd.concat([df_9th, df_10th], ignore_index=True)

# explore dfs 
# print(all_meps.columns)
#print(all_meps.head())
#print(all_meps.tail())

#row_data = all_meps[all_meps['name'] == 'Abir AL-SAHLANI']

#for column in row_data.columns:
#    print(f"{column}: {row_data[column].values[0]}")





import pandas as pd
import numpy as np

# Function to extract only relevant assistants
def extract_assistants(row):
    assistants = []
    # Focus only on "Accredited assistants" and "Accredited assistants (grouping)"
    relevant_groups = ['assistants.Accredited assistants', 'assistants.Accredited assistants (grouping)']
    
    for group in relevant_groups:
        # Check if the group exists in the row
        if group in row and isinstance(row[group], list):
            names = row[group]
            for name in names:
                assistants.append({
                    'assistant_name': name,
                    'mep_name': row['name'],  # Updated to use 'mep_name'
                    'party': row['party'],
                    'country': row['country'],
                    'term': row['term']
                })
    return assistants

# Flatten assistants for easier comparison
assistant_data = pd.DataFrame(
    [item for sublist in all_meps.apply(extract_assistants, axis=1) for item in sublist]
)

# Pivot data to trace assistant movement across terms
movement_df = assistant_data.pivot_table(
    index='assistant_name',
    columns='term',
    values=['mep_name', 'party'],
    aggfunc='first'
)

# Flatten the MultiIndex columns
movement_df.columns = [f"{col[0]}_{col[1]}" for col in movement_df.columns]
movement_df = movement_df.reset_index()

# Display the movement DataFrame
print(movement_df)


# Detect and count movements between parties
movement_df['party_changed'] = movement_df['party_9'] != movement_df['party_10']
party_movement_summary = movement_df['party_changed'].value_counts().rename_axis('changed_party').reset_index(name='count')
print(party_movement_summary)

import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()

# Add nodes and edges based on assistant movement data
for _, row in movement_df.iterrows():
    assistant = row['assistant_name']
    party_9, party_10 = row['party_9'], row['party_10']
    G.add_node(assistant, term_9=party_9, term_10=party_10)
    
    if row['party_changed']:  # Only add edges for assistants who changed parties
        G.add_edge(party_9, party_10, assistant=assistant)

# Draw the graph
plt.figure(figsize=(12, 8))
nx.draw(G, with_labels=True, node_size=700, node_color="skyblue", font_size=10, font_weight="bold")
plt.title("Assistant Movement Across European Parliament Terms")
plt.show()
