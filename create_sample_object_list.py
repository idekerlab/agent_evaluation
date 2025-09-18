#!/usr/bin/env python
"""
Script to create a sample object_list with specified criteria
"""

import sys
import os
import json
from datetime import datetime

# Add the app directory to the path so we can import from it
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.config import load_database_uri
from app.sqlite_database import SqliteDatabase

def create_sample_object_list():
    """Create a sample object_list with specified criteria"""
    # Connect to the database
    uri = load_database_uri()
    db = SqliteDatabase(uri)
    
    # Find some hypotheses
    hypotheses = db.find('hypothesis', {})
    
    if not hypotheses or len(hypotheses) < 3:
        print("Not enough hypotheses found in the database.")
        return
    
    # Take the first three hypotheses
    hypothesis_ids = [h['object_id'] for h in hypotheses[:3]]
    
    # Create the object_list
    object_list = {
        "type": "object_list",
        "name": "Sample Hypotheses for Review",
        "description": "A collection of sample hypotheses for demonstration of the review interface",
        "object_ids": hypothesis_ids,
        "_criteria": [
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
    }
    
    # Add to database
    object_list_id, properties, obj_type = db.add(object_id=None, properties=object_list, object_type="object_list")
    
    print(f"Created object_list with ID: {object_list_id}")
    print(f"Contains hypotheses: {', '.join(hypothesis_ids)}")
    
    # Close the database connection
    db.close()
    
    return object_list_id

if __name__ == "__main__":
    create_sample_object_list()
