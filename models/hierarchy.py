"""
This module contains the Hierarchy class for the agent evaluation module.
One source of Datasets is a hierarchical network in HCX (CX2) format.
Optionally, a parent interactome network in CX2 format will be used in creating Dataset instances.
We therefore need a Hierarchy class to represent the hierarchical network with methods to
obtain the parent network and to create Dataset instances from the hierarchical network. 
"""

import json
import pandas as pd
import os
import yaml
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from models.dataset import Dataset
import csv
from io import StringIO

class Hierarchy():
    def __init__(self, hierarchy_cx, derived_from_cx=None):
        self.hierarchy_cx = hierarchy_cx
        self.derived_from_cx = derived_from_cx

    def get_experiment_description(self):
        return self.hierarchy_cx.get_network_attributes().get("experiment_description")
    

    def get_assemblies(self, filter=None):
        assemblies = []
        for assembly in self.hierarchy_cx.get_nodes().values():
            attributes = assembly.get("v")
            # print(attributes.get("name"))
            size = attributes.get("CD_MemberList_Size")
           
            members = attributes.get("CD_MemberList")
            # print(members)
            if members is not None and size is not None:
                if filter is not None:
                    names = filter.get("names")
                    if names is not None:
                        names = [name.lower() for name in names]
                    assembly_names = get_assembly_names(assembly)
                    if assembly_names is not None:
                        assembly_names = [name.lower() for name in assembly_names]
                    if names is not None and not any_element_in(assembly_names, names):
                        continue
                    max_size = filter.get("max_size")
                    if max_size is not None and size > max_size:
                        # print(f'size {size} is greater than max_size {max_size}')
                        continue
                    min_size = filter.get("min_size")
                    if min_size is not None and size < min_size:
                        continue
                assemblies.append(assembly) 
        return assemblies
    

    # Adds the data from the interactome to the assemblies selected by the filter.
    # returns those assemblies
    def add_data_from_interactome(self, filter=None, columns=None):
        assemblies = self.get_assemblies(filter)
        name_column = columns.get("name") if columns is not None else None
        if name_column is None:
            raise ValueError("The 'name' column must be specified in the columns mapping")
        interactome_nodes = self.derived_from_cx.get_nodes().values()
        interactome_data =[]
        for interactome_node in interactome_nodes:
            interactome_node_attributes = interactome_node.get("v")
            if columns is not None:
                node_data = {}
                for key, value in interactome_node_attributes.items(): 
                    # if key == "name":
                    #     if value == "BST2":
                    #         print(f'key = {key}, value = {value} data = {interactome_node_attributes}')
                    # if key == "Inhibits_SARS":
                    #     print(f'key = {key}, value = {value} data = {interactome_node_attributes}')
                    if key in columns:
                        mapped_key = columns[key]
                        node_data[mapped_key] = value
                interactome_data.append(node_data)
            else:
                interactome_data.append(interactome_node_attributes)
        for assembly in assemblies:
            attributes = assembly.get("v")
            members = attributes.get("CD_MemberList").split(" ")
            assembly_data = {}
            for data in interactome_data:
                if data[name_column] in members:
                    assembly_data[data[name_column]] = data
            self.hierarchy_cx.set_node_attribute(assembly["id"], "data", json.dumps(assembly_data))
        return assemblies


    def add_data_from_file(self, file_path, key_column='name', columns=None, 
                           filter=None, sheet_name=0, delimiter=None):
        # Determine file type from extension
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()

        # Read the file based on its type
        if file_extension == '.xlsx':
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        elif file_extension == '.csv':
            df = pd.read_csv(file_path, delimiter=',' if delimiter is None else delimiter)
        elif file_extension == '.tsv':
            df = pd.read_csv(file_path, delimiter='\t' if delimiter is None else delimiter)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}. Supported types are .xlsx, .csv, and .tsv")
        

        # # Ensure the key column exists in the input file/dataframe
        # if key_column not in df.columns:
        #     raise ValueError(f"Key column '{key_column}' not found in the file")

        # # Move the key_column to the first position if it's not already there
        # if df.columns[0] != key_column:
        #     df = df[[key_column] + [col for col in df.columns if col != key_column]]

        # # Select columns
        # if columns:
        #     df = df[[col for col in columns if col in df.columns]]

        # # Ensure key_column is still present after column selection
        # if key_column not in df.columns:
        #     df.insert(0, key_column, df.index)

# Ensure the key column exists in the input file/dataframe
        if key_column not in df.columns:
            raise ValueError(f"Key column '{key_column}' not found in the file")

        # Prepare the list of columns to keep, ensuring key_column is first
        if columns:
            # Create a mapping of old column names to new column names
            column_mapping = {old: new for old, new in columns.items() if old in df.columns}
            
            # Ensure key_column is in the mapping
            if key_column not in column_mapping:
                column_mapping[key_column] = key_column
            
            # Create ordered list of columns to keep
            columns_to_keep = [col for col in df.columns if col in column_mapping]
            
            # Ensure key_column is first
            if key_column in columns_to_keep and columns_to_keep[0] != key_column:
                columns_to_keep.remove(key_column)
                columns_to_keep.insert(0, key_column)
        else:
            columns_to_keep = df.columns.tolist()
            if columns_to_keep[0] != key_column:
                columns_to_keep.remove(key_column)
                columns_to_keep.insert(0, key_column)
            column_mapping = {col: col for col in columns_to_keep}

        # Select and reorder columns
        df = df[columns_to_keep]

        # Rename columns while maintaining order
        df.columns = [column_mapping[col] for col in df.columns]

        # Convert DataFrame to list of dictionaries
        data_dict_list = df.to_dict('records')

        def clean_dict(d):
            return {k: v for k, v in d.items() if pd.notna(v) and v != "" and v is not None}

        # Clean the dictionaries
        cleaned_data_dict_list = [clean_dict(d) for d in data_dict_list]

        # Get assemblies
        assemblies = self.get_assemblies(filter)

        for assembly in assemblies:
            attributes = assembly.get("v")
            members = attributes.get("CD_MemberList", "").split(" ")
            assembly_data = {}
            
            # iterate over all the data rows
            for gene_dict in cleaned_data_dict_list:
                mapped_key_column = columns[key_column]
                if mapped_key_column in gene_dict:
                    gene_symbol = gene_dict[mapped_key_column]
                    if gene_symbol in members:
                        assembly_data[gene_symbol] = gene_dict
            else:
                print(f'mapped key column {mapped_key_column} is not in data row {gene_dict}')
            #filtered_file_data = [data for data in cleaned_data_dict_list if data[columns[key_column]] in members]
            
            # Add filtered data to assembly
            self.hierarchy_cx.set_node_attribute(assembly["id"], "data", json.dumps(assembly_data))

        return assemblies
    
        
import re

def remove_number_suffix(text):
    # This pattern matches a space, followed by an opening parenthesis,
    # then any number of digits (possibly with a decimal point),
    # and finally a closing parenthesis at the end of the string
    pattern = r'\s\(\d+(?:\.\d+)?\)$'
    
    # Use re.sub to replace the matched pattern with an empty string
    return re.sub(pattern, '', text)

def get_assembly_names(assembly):
    names = []
    attributes = assembly.get("v")
    size = attributes.get("CD_MemberList_Size")
    if "LLM Name" in attributes and attributes.get("LLM Name") is not None:
        llm_name = remove_number_suffix(attributes.get("LLM Name"))
        if llm_name != "skipped":
            names.append(llm_name)
    if "CD_CommunityName" in attributes and attributes.get("CD_CommunityName") is not None and attributes.get("CD_CommunityName") != "(none)":
        names.append(f'({size}) {attributes.get("CD_CommunityName")}')
    if "name" in attributes and attributes.get("name") is not None:
        names.append(f'({size}) {attributes.get("name")}')
    return names
        
def any_element_in(list1, list2):
    return bool(set(list1) & set(list2))

def dataset_from_assembly(db, assembly, type="csv", columns=None, decimal_places=None, experiment_description=""):
    data_dict = json.loads(assembly["v"]["data"])
    name_column = columns.get("name") if columns is not None else None
    if name_column is None:
        raise ValueError("The 'name' column must be specified in the columns mapping")

    # Filter the data dict on columns
    if columns is not None:
        filtered_data_dict = {}
        for key, value in data_dict.items():
            filtered_data_dict[key] = {col: value[col] for col in columns if col in value}
        data_dict = filtered_data_dict

    if type == "yaml":
        datastring = yaml.dump(data_dict, default_flow_style=False, sort_keys=False)
    elif type == "xml":
        datastring = format_as_xml(data_dict)
    elif type == "csv":
        datastring = data_dict_to_csv(data_dict, columns=None, decimal_places=decimal_places)
    else:
        raise ValueError(f"Unsupported data format type: {type}")
    
    assembly_names = json.dumps(get_assembly_names(assembly), indent=4)
    if len(assembly_names) == 0:
        dataset_name = assembly["v"][name_column]
    else:
        dataset_name = json.loads(assembly_names)[0]  # Assuming we want the first name
    dataset = Dataset.create(db, dataset_name, datastring, experiment_description, description=assembly_names)
    return dataset

def data_dict_to_csv(data_dict, columns=None, decimal_places=None):
    if isinstance(data_dict, str):
        data_dict = json.loads(data_dict)
    
    # Scan the data_dict for all properties if columns is not specified
    if columns is None:
        columns = set()
        for item in data_dict.values():
            columns.update(item.keys())
        columns = sorted(columns)
    
    # Prepare the CSV data
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['GeneSymbol'] + columns)
    
    # Write data rows
    for gene_symbol, gene_data in data_dict.items():
        row = [gene_symbol]
        for col in columns:
            value = gene_data.get(col, '')
            # Preserve the format, especially for numbers
            if isinstance(value, (int, float)):
                if isinstance(value, float) and decimal_places is not None:
                    value = f"{value:.{decimal_places}f}"
                else:
                    value = f"{value}"
            row.append(value)
        writer.writerow(row)
    
    return output.getvalue()

def format_as_xml(data_dict):
    root = Element('dataset')

    for key, item in data_dict.items():
        record = SubElement(root, 'record')
        record.set('id', str(key))
        
        for field, value in item.items():
            field_elem = SubElement(record, field)
            field_elem.text = str(value)

    rough_string = tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    xml_string = reparsed.toprettyxml(indent="  ")
    
    return xml_string

def reduce_float_precision(dataset_df, decimal_places, round_columns=None):
    # Create a copy of the DataFrame to avoid modifying the original
    rounded_df = dataset_df.copy()
    
    # Identify float columns
    float_columns = rounded_df.select_dtypes(include=['float64', 'float32']).columns
    
    # Round float columns to specified decimal places
    for col in float_columns:
        if round_columns is None:
            rounded_df[col] = rounded_df[col].round(decimal_places)
        if col in round_columns:
            rounded_df[col] = rounded_df[col].round(decimal_places)
    return rounded_df