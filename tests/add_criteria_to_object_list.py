#!/usr/bin/env python
# This script adds or updates the _criteria property in an existing object_list
# to define scoring criteria for the reviewer interface

import sqlite3
import json
import sys
import os
from pathlib import Path

# Database path from config
db_path = os.path.expanduser('/Users/chengzhangao/ae_database/ae_database.db')

def get_object_lists():
    """Get a list of all object_lists from the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query for object_lists
    cursor.execute("SELECT object_id, properties FROM nodes WHERE object_type='object_list'")
    rows = cursor.fetchall()
    
    object_lists = []
    for row in rows:
        object_id = row[0]
        properties = json.loads(row[1])
        name = properties.get('name', 'Unnamed')
        object_lists.append((object_id, name))
    
    conn.close()
    return object_lists

def add_criteria_property(object_list_id, criteria_config):
    """Add or update the _criteria property for the specified object_list"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get the current properties for the object_list
    cursor.execute("SELECT properties FROM nodes WHERE object_id=?", (object_list_id,))
    row = cursor.fetchone()
    
    if row:
        properties = json.loads(row[0])
        
        # Add or update the _criteria property
        properties['_criteria'] = criteria_config
        
        # Update the record in the database
        cursor.execute(
            "UPDATE nodes SET properties=? WHERE object_id=?",
            (json.dumps(properties), object_list_id)
        )
        
        conn.commit()
        print(f"Successfully updated object_list {object_list_id} with _criteria property.")
        
        # Print the current object list for verification
        print("\nUpdated object_list properties:")
        for key, value in properties.items():
            if key == 'object_ids':
                print(f"{key}: [... {len(value)} objects ...]")
            elif key == '_criteria':
                print(f"{key}: [... {len(value)} criteria items ...]")
            else:
                print(f"{key}: {value}")
    else:
        print(f"Object list with ID {object_list_id} not found.")
    
    conn.close()

def create_new_criterion():
    """Helper function to create a new criterion configuration"""
    criterion = {}
    
    print("\nCreating a new criterion:")
    criterion["label"] = input("Label (display name for the criterion): ")
    criterion["property_name"] = input("Property name (field name in the database): ")
    
    input_type = input("Input type (textarea, text, checkbox, menu) [default: text]: ").strip().lower()
    criterion["input_type"] = input_type if input_type in ['textarea', 'text', 'checkbox', 'menu'] else 'text'
    
    display_type = input("Display type (text, csv) [default: text]: ").strip().lower()
    criterion["display_type"] = display_type if display_type in ['text', 'csv'] else 'text'
    
    data_type = input("Data type (str, int) [default: str]: ").strip().lower()
    criterion["data_type"] = data_type if data_type in ['str', 'int'] else 'str'
    
    # If input type is menu, ask for options
    if criterion["input_type"] == 'menu':
        print("Enter menu options (one per line, empty line to finish):")
        options = []
        while True:
            option = input("Option (or empty to finish): ").strip()
            if not option:
                break
            options.append(option)
        criterion["options"] = options
    
    return criterion

def main():
    # Get available object lists
    object_lists = get_object_lists()
    
    if not object_lists:
        print("No object_lists found in the database.")
        return
    
    print("Available object_lists:")
    for i, (object_id, name) in enumerate(object_lists):
        print(f"{i+1}. {name} ({object_id})")
    
    try:
        selection = int(input("\nEnter the number of the object_list to modify (or 0 to exit): "))
        if selection == 0:
            return
        
        if selection < 1 or selection > len(object_lists):
            print("Invalid selection.")
            return
        
        object_list_id = object_lists[selection-1][0]
        
        # Define default criteria configuration
        default_criteria = [
            {
                "label": "Comments",
                "property_name": "comments",
                "input_type": "textarea",
                "display_type": "text",
                "data_type": "str"
            },
            {
                "label": "Evaluation",
                "property_name": "evaluation",
                "input_type": "menu",
                "display_type": "text",
                "data_type": "str",
                "options": ["great!", "good.", "ok.", "needs work.", "unacceptable"]
            }
        ]
        
        # Ask if the user wants to customize the criteria
        customize = input("Do you want to customize the criteria configuration? (y/n): ").lower() == 'y'
        
        criteria_config = []
        if customize:
            print("\nYou can add multiple criteria. Each criterion needs a label, property name, input type, etc.")
            
            while True:
                add_another = input("\nAdd a criterion? (y/n): ").lower() == 'y'
                if not add_another:
                    break
                
                criterion = create_new_criterion()
                criteria_config.append(criterion)
                
                print(f"Added criterion: {criterion['label']} ({criterion['property_name']})")
        else:
            # Use default criteria
            criteria_config = default_criteria
            print("Using default criteria configuration.")
        
        # Add the criteria property to the selected object_list
        add_criteria_property(object_list_id, criteria_config)
        
    except ValueError:
        print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main() 