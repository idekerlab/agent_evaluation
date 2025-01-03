import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.json_object import Json
from app.sqlite_database import SqliteDatabase
from app.config import load_database_uri
import json

def main():
    # Get database connection
    uri = load_database_uri()
    db = SqliteDatabase(uri)
    
    try:
        # Read the JSON file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, 'test_hypothesis.json')
        
        with open(json_path, 'r') as f:
            json_data = json.load(f)
        
        # Create Json object
        json_obj = Json(
            name="Test Hypothesis JSON",
            json_data=json_data
        )
        
        # Add to database
        object_id, properties, _ = db.add(None, json_obj.to_dict(), "json")
        
        print(f"Created JSON object with ID: {object_id}")
        
    finally:
        db.close()

if __name__ == '__main__':
    main()
