# List all objects script
import sys
import os

cwd = os.getcwd()  # Current working directory
sys.path.append(cwd)  # Add to the Python path

from app.sqlite_database import SqliteDatabase
# from sqlalchemy import text
from app.config import load_database_config
import json

def is_json(value):
    try:
        json.loads(value)
        return True
    except (ValueError, TypeError):
        return False
        
def list_all_objects():
    _, database_uri, _, _ = load_database_config()
    db = SqliteDatabase(database_uri)
    try:
        # Find all objects without filtering by object_type
        query = "SELECT id, properties FROM nodes"
        objects = {}
        with db.engine.connect() as conn:
            result = conn.execute(text(query))
            for row in result:
                object_id = row[0]
                properties_as_json = row[1] # JSON string
                if not is_json(properties_as_json):
                    print(f"Skipping malformed JSON for id: {object_id}")
                    continue    
                print(f"ID: {object_id} Properties: {properties_as_json}")
                properties = db.deserialize_properties(properties_as_json)
                print(f"ID: {object_id} Properties: {len(properties)}")
                objects[object_id] = properties
        
        # Print out all objects
        for object_id, properties in objects.items():
            print(f"ID: object_id")
            for key, value in properties.items():
                print(f"  {key}: {value}")
            print()

    finally:
        db.close()

# Example usage
if __name__ == "__main__":
    list_all_objects()