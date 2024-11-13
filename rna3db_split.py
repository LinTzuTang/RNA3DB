import os
import json
import pandas as pd
import random
import argparse
from sklearn.model_selection import train_test_split

# Set a random seed for reproducibility
random.seed(42)

# Utility Functions
def read_json(path):
    """Read JSON data from a file."""
    with open(path, "r") as jsonfile:
        return json.load(jsonfile)

def process_json_to_df(json_file, structure_type):
    """Convert JSON data to a pandas DataFrame."""
    data = read_json(json_file)
    rows = []

    if structure_type == "structure":
        for set_name, components in data.items():
            for component, structures in components.items():
                for structure_id, structure_data in structures.items():
                    for sub_structure_id, details in structure_data.items():
                        rows.append({
                            "set": set_name,
                            "component": component,
                            "sequence_group": structure_id,
                            "chain_id": sub_structure_id,
                            "release_date": details.get("release_date"),
                            "structure_method": details.get("structure_method"),
                            "resolution": details.get("resolution"),
                            "length": details.get("length"),
                            "sequence": details.get("sequence")
                        })
    elif structure_type == "sequence":
        for set_name, sequence_data in data.items():
            for sequence_id, rna_data in sequence_data.items():
                for chain_id, details in rna_data.items():
                    rows.append({
                        "set": set_name,
                        "sequence_group": sequence_id,
                        "chain_id": chain_id,
                        "release_date": details.get("release_date"),
                        "structure_method": details.get("structure_method"),
                        "resolution": details.get("resolution"),
                        "length": details.get("length"),
                        "sequence": details.get("sequence")
                    })
    return pd.DataFrame(rows)

def split_and_assign_folds(df):
    """Split the DataFrame into train, validation, and test sets, then assign folds."""
    # Group by sequence_group for stratification
    grouped = df.groupby('sequence_group')
    groups = [group for _, group in grouped]

    # Split into train, validation, and test sets
    train_groups, test_groups = train_test_split(groups, test_size=0.2, random_state=42)
    train_groups, valid_groups = train_test_split(train_groups, test_size=0.125, random_state=42)

    # Assign sets
    train_set = pd.concat(train_groups).reset_index(drop=True)
    train_set['set'] = 'train'
    valid_set = pd.concat(valid_groups).reset_index(drop=True)
    valid_set['set'] = 'valid'
    test_set = pd.concat(test_groups).reset_index(drop=True)
    test_set['set'] = 'test'

    # Combine all sets into one DataFrame
    final_df = pd.concat([train_set, valid_set, test_set]).reset_index(drop=True)

    # Initialize fold summary and component dict for stratified folding
    fold_num_summary = {f'fold{i+1}': 0 for i in range(5)}
    component_dict = {group: final_df[final_df['sequence_group'] == group]['chain_id'].tolist()
                      for group in final_df['sequence_group'].unique()}

    # Sort components by the number of chain IDs (descending)
    component_dict = {k: v for k, v in sorted(component_dict.items(), key=lambda item: len(item[1]), reverse=True)}

    # Initialize the 'fold' column and assign folds
    final_df['fold'] = 0
    for group, chain_ids in component_dict.items():
        least_populated_folds = sorted(fold_num_summary.items(), key=lambda x: x[1])[:2]
        chosen_fold = random.choice(least_populated_folds)[0]
        
        for chain_id in chain_ids:
            final_df.loc[final_df['chain_id'] == chain_id, 'fold'] = int(chosen_fold[-1])
            fold_num_summary[chosen_fold] += 1

    return final_df

def main(structure_type, output_dir, output_filename):
    """Main function to process JSON data and split into train/valid/test with folds."""
    json_file = os.path.join(output_dir, f"split_{structure_type}.json")
    
    # Process JSON to DataFrame
    df = process_json_to_df(json_file, structure_type)
    
    # Split data and assign folds
    final_df = split_and_assign_folds(df)

    # Export to specified CSV filename
    output_file = os.path.join(output_dir, output_filename)
    final_df.to_csv(output_file, index=False)
    
    print(f"Processed {structure_type} data and saved to {output_file}")

# Argument Parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and split JSON data for RNA structure or sequence.")
    parser.add_argument("structure_type", choices=["sequence", "structure"], help="Type of data to process ('sequence' or 'structure').")
    parser.add_argument("output_dir", help="Directory where the JSON file is located and output will be saved.")
    parser.add_argument("output_filename", help="Name of the output CSV file.")
    
    args = parser.parse_args()
    main(args.structure_type, args.output_dir, args.output_filename)


# python rna3db_split.py sequence output_new_core core_sequence_split.csv