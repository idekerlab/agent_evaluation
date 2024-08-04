import pandas as pd
import yaml
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

class Dataset:
    def __init__(self, db, 
                 name=None, data=None, 
                 experiment_description=None, 
                 description=None, object_id=None, created=None):
        self.db = db
        self.name = name
        self.data = data
        self.experiment_description = experiment_description
        self.description = description
        self.object_id = object_id
        self.created = created

    @classmethod
    def create(cls, db, name, data, experiment_description, description=""):
        properties = {
            "name": name,
            "data": data,
            "experiment_description": experiment_description,
            "description": description
        }
        object_id, created, _ = db.add(object_id=None, properties=properties, object_type="dataset")
        return cls(db, name, data, experiment_description, description, 
                   object_id=object_id, created=created)

    @classmethod
    def load(cls, db, object_id):
        properties, _ = db.load(object_id)
        if properties:
            return cls(db, **properties)
        return None

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.db.update(self.object_id, kwargs)

    def delete(self):
        self.db.remove(self.object_id)

def update_column_names(dataset_df, column_mapping):
    # Create a copy of the DataFrame to avoid modifying the original
    updated_dataset = dataset_df.copy()
    
    # Validate that all keys in column_mapping exist in the DataFrame
    invalid_columns = set(column_mapping.keys()) - set(updated_dataset.columns)
    if invalid_columns:
        raise ValueError(f"The following columns are not present in the DataFrame: {invalid_columns}")
    
    # Update the column names
    updated_dataset.rename(columns=column_mapping, inplace=True)
    
    return updated_dataset

def format_as_yaml(dataset_df, key_column=None):
    if key_column is not None and key_column not in dataset_df.columns:
        raise ValueError(f"Key column '{key_column}' not found in DataFrame")

    if key_column:
        # Use the specified column as keys
        data_dict = dataset_df.set_index(key_column).to_dict(orient='index')
    else:
        # Use row indices as keys
        data_dict = dataset_df.to_dict(orient='index')

    # Convert to YAML
    yaml_str = yaml.dump(data_dict, default_flow_style=False, sort_keys=False)
    
    return yaml_str

def format_as_xml(dataset_df, key_column=None):
    # Create the root element
    root = Element('dataset')

    # Iterate through DataFrame rows
    for idx, row in dataset_df.iterrows():
        # Create a new element for each row
        row_elem = SubElement(root, 'record')
        
        # If a key column is specified, use it as an attribute
        if key_column and key_column in dataset_df.columns:
            row_elem.set('key', str(row[key_column]))
        else:
            row_elem.set('id', str(idx))
        
        # Add each column as a subelement
        for col, value in row.items():
            if col != key_column:  # Skip the key column if it's used as an attribute
                field_elem = SubElement(row_elem, col)
                field_elem.text = str(value)

    # Convert to a string and pretty print
    rough_string = tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    xml_string = reparsed.toprettyxml(indent="  ")
    
    return xml_string
