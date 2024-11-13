import os
import json
import pandas as pd
from sklearn.model_selection import StratifiedKFold
import numpy as np

# File paths
output_dir = "output_rrna_removed_filtered"
json_file_structure = os.path.join(output_dir, "split.json")
json_file_sequence = os.path.join(output_dir, "split_seq.json")
chain_ids_file = "non_RNA_SM_complexes.csv"
# chain_ids_to_remove =  [
#     "7lne", "7lnf", "7lng", "8vax", "8sy1", "7u8a",
#     "7kuk", "7kul", "7kum", "7kun", "7kuo", "7kup",
#     "8swg", "8swo", "8sx5", "8sx6", "8sxl",
#     "7u87", "7u88", "7u89", "8vaw"
# ]


def read_json(path):
    """Read JSON data from a file."""
    with open(path, "r") as jsonfile:
        data = json.load(jsonfile)
    return data


def read_chain_ids(csv_file):
    """Read chain IDs from a CSV file."""
    df = pd.read_csv(csv_file, header=0)
    return df["non_RNA_SM_complexes"].tolist()


def process_json_to_df(json_file, structure_type):
    """Convert JSON data to a pandas DataFrame."""
    data = read_json(json_file)
    rows = []

    if structure_type == "structure":
        for set_name, components in data.items():
            for component, structures in components.items():
                for structure_id, structure_data in structures.items():
                    for sub_structure_id, details in structure_data.items():
                        row = {
                            "set": set_name,
                            "component": component,
                            "sequence_group": structure_id,
                            "chain_id": sub_structure_id,
                            "release_date": details.get("release_date", None),
                            "structure_method": details.get("structure_method", None),
                            "resolution": details.get("resolution", None),
                            "length": details.get("length", None),
                            "sequence": details.get("sequence", None),
                        }
                        rows.append(row)
    elif structure_type == "sequence":
        for set_name, sequence_data in data.items():
            for sequence_id, rna_data in sequence_data.items():
                for chain_id, details in rna_data.items():
                    row = {
                        "set": set_name,
                        "sequence_group": sequence_id,
                        "chain_id": chain_id,
                        "release_date": details.get("release_date", None),
                        "structure_method": details.get("structure_method", None),
                        "resolution": details.get("resolution", None),
                        "length": details.get("length", None),
                        "sequence": details.get("sequence", None),
                    }
                    rows.append(row)
    return pd.DataFrame(rows)


def remove_chain_ids(df, chain_ids_prefixes):
    """Remove rows with specified chain_id prefixes."""
    mask = df["chain_id"].str[:4].isin(chain_ids_prefixes)
    return df[~mask]


def save_to_csv(df, filename):
    """Save DataFrame to CSV."""
    df.to_csv(filename, index=False)


def split_to_folds(df, num_folds=5, random_state=42):
    """Split the DataFrame into stratified folds."""
    unique_sequence_groups = df["sequence_group"].unique()
    group_counts = df.groupby("sequence_group").size().reset_index(name="count")

    skf = StratifiedKFold(n_splits=num_folds, shuffle=True, random_state=random_state)
    for fold_number, (train_index, test_index) in enumerate(
        skf.split(group_counts, group_counts["count"]), 1
    ):
        group_counts.loc[test_index, "fold"] = fold_number

    df = df.merge(
        group_counts[["sequence_group", "fold"]], on="sequence_group", how="left"
    )
    df["fold"] = df["fold"].astype(int)
    return df.drop(columns=["set"]).reindex(
        columns=["fold"] + [col for col in df.columns if col != "fold"]
    )


def main():
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Read chain IDs from the CSV file
    chain_ids_to_remove = read_chain_ids(chain_ids_file)

    # Process structure JSON
    df_structure = process_json_to_df(json_file_structure, "structure")
    df_structure = remove_chain_ids(df_structure, chain_ids_to_remove)
    save_to_csv(df_structure, os.path.join(output_dir, "split_structure_sequence.csv"))

    # Process sequence JSON
    df_sequence = process_json_to_df(json_file_sequence, "sequence")
    df_sequence = remove_chain_ids(df_sequence, chain_ids_to_remove)
    save_to_csv(df_sequence, os.path.join(output_dir, "split_sequence.csv"))

    # Split sequence data into stratified folds
    df_sequence_folds = split_to_folds(df_sequence)
    save_to_csv(df_sequence_folds, os.path.join(output_dir, "split_seq_5_fold.csv"))

    print("Processing complete. Files saved to:", output_dir)


if __name__ == "__main__":
    main()
