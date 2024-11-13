import csv
import pandas as pd
import json
import numpy as np
import argparse

def read_json(path):
    with open(path, 'r') as jsonfile:
        data = json.load(jsonfile)
    return data

def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, indent=4)

def flatten_splt_json(data):
    flat_list = []

    for split, components in data.items():
        for component, rfams in components.items():
            for rfam, rnas in rfams.items():
                for rna_id, details in rnas.items():
                    flat_list.append({
                        "split": split,
                        "component": component,
                        "Rfam": rfam,
                        "RNA_ID": rna_id
                    })
    
    return pd.DataFrame(flat_list)

def filter_rnas(input_json_path, csv_path, output_json_path):
    all_rnas = read_json(input_json_path)
    df_hariboss = pd.read_csv(csv_path)
    df_hariboss['RNA_ID'] = df_hariboss['pdbid'] + '_' + df_hariboss['rna_chain']
    ids = df_hariboss['RNA_ID'].unique()
    filtered_rnas = {key: value for key, value in all_rnas.items() if key in ids}
    write_json(output_json_path, filtered_rnas)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter RNA data based on RNA_IDs from a CSV file")
    parser.add_argument('input_json', type=str, help='Path to the input JSON file (parse.json)')
    parser.add_argument('csv_file', type=str, help='Path to the CSV file containing RNA information')
    parser.add_argument('output_json', type=str, help='Path to the output JSON file (filtered_parse.json)')

    args = parser.parse_args()

    filter_rnas(args.input_json, args.csv_file, args.output_json)
