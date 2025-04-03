import json
import os
import sys
import argparse
from app.sqlite_database import SqliteDatabase
from app.config import load_database_uri

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Save hypothesis data to SQLite database')
    parser.add_argument('--db-uri', dest='db_uri', help='SQLite database URI (overrides config file)')
    parser.add_argument('--hypothesis-file', dest='hypothesis_file', 
                        help='Path to the hypothesis JSON file (default: app/static/sample_hypothesis_3.json)')
    args = parser.parse_args()
    
    # Load the hypothesis data from the JSON file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    hypothesis_path = args.hypothesis_file or os.path.join(script_dir, "app", "static", "sample_hypothesis_3.json")
    
    try:
        with open(hypothesis_path, "r") as file:
            hypothesis_data = json.load(file)
    except FileNotFoundError:
        print(f"Error: Hypothesis file not found at {hypothesis_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in hypothesis file {hypothesis_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading hypothesis file: {e}")
        sys.exit(1)
        
    print(f"Loaded hypothesis data: {hypothesis_data['name']}")
    
    # Get the database URI
    uri = args.db_uri
    if not uri:
        try:
            uri = load_database_uri()
            if not uri:
                print("Error: Database URI not found in config file.")
                print("Please create a config file at ~/ae_config/config.ini with:")
                print("[SQLITE]")
                print("URI = sqlite:///path/to/your/database.db")
                print("\nOr provide a database URI with the --db-uri parameter.")
                sys.exit(1)
        except Exception as e:
            print(f"Error loading database URI from config: {e}")
            print("Please create a config file at ~/ae_config/config.ini with:")
            print("[SQLITE]")
            print("URI = sqlite:///path/to/your/database.db")
            print("\nOr provide a database URI with the --db-uri parameter.")
            sys.exit(1)
    
    print(f"Using database URI: {uri}")
    
    # Initialize the database connection
    try:
        db = SqliteDatabase(uri)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)
        
    # Extract the object_id and object_type
    object_id = hypothesis_data.get("object_id")
    if not object_id:
        print("Error: No object_id found in the hypothesis data.")
        sys.exit(1)
        
    object_type = hypothesis_data.get("type")
    if not object_type:
        print("Error: No 'type' field found in the hypothesis data.")
        print("Setting default type to 'hypothesis'.")
        object_type = "hypothesis"
    
    # Remove object_id and type from properties as they're stored separately
    properties = {k: v for k, v in hypothesis_data.items() if k not in ["object_id", "type"]}
    
    try:
        # First check if the object already exists
        existing_properties, _ = db.load(object_id)
        
        if existing_properties:
            print(f"Hypothesis with ID {object_id} already exists. Updating...")
            db.update(object_id, properties)
            print(f"Successfully updated hypothesis: {object_id}")
        else:
            print(f"Creating new hypothesis with ID: {object_id}")
            added_id, _, _ = db.add(object_id=object_id, properties=properties, object_type=object_type)
            print(f"Successfully saved hypothesis to database with ID: {added_id}")
    except Exception as e:
        print(f"Error saving hypothesis to database: {e}")
        sys.exit(1)
    
    print("Operation completed successfully.")
    
if __name__ == "__main__":
    main() 