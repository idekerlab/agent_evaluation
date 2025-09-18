#!/usr/bin/env python
# This script adds or updates the _order property in an existing object_list
# to test the property ordering functionality in the reviewer interface

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

def add_order_property(object_list_id, order_config):
    """Add or update the _order property for the specified object_list"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get the current properties for the object_list
    cursor.execute("SELECT properties FROM nodes WHERE object_id=?", (object_list_id,))
    row = cursor.fetchone()
    
    if row:
        properties = json.loads(row[0])
        
        # Add or update the _order property
        properties['_order'] = order_config
        
        # Update the record in the database
        cursor.execute(
            "UPDATE nodes SET properties=? WHERE object_id=?",
            (json.dumps(properties), object_list_id)
        )
        
        conn.commit()
        print(f"Successfully updated object_list {object_list_id} with _order property.")
        
        # Print the current object list for verification
        print("\nUpdated object_list properties:")
        for key, value in properties.items():
            if key == 'object_ids':
                print(f"{key}: [... {len(value)} objects ...]")
            else:
                print(f"{key}: {value}")
    else:
        print(f"Object list with ID {object_list_id} not found.")
    
    conn.close()

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
        
        # Define the order configuration
        order_config = {
            "name": 1,
            "description": 2, 
            "ndex_uuid": 3
            # Add more properties as needed
        }
        
        # Ask if the user wants to customize the order
        customize = input("Do you want to customize the order configuration? (y/n): ").lower() == 'y'
        
        if customize:
            print("\nEnter property names and their order ranks. Enter an empty property name to finish.")
            order_config = {}
            
            while True:
                prop_name = input("Property name (or empty to finish): ").strip()
                if not prop_name:
                    break
                    
                try:
                    rank = int(input(f"Rank for {prop_name}: "))
                    order_config[prop_name] = rank
                except ValueError:
                    print("Invalid rank. Please enter an integer.")
        
        # Add the order property to the selected object_list
        add_order_property(object_list_id, order_config)
        
    except ValueError:
        print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main() 