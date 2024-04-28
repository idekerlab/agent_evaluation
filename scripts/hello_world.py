import sys
import os

cwd = os.getcwd() # Current working directory
dirname = os.path.dirname(cwd) # Parent directory
print("================")
print(cwd)
print(dirname)
sys.path.append(cwd)# Add the parent directory to the Python path
print("================")
print(sys.path)
print("================")

from app.database import Database

# Define the database connection details
uri = "bolt://localhost:7687"
user = "neo4j"
password = "fredfred"

# Initialize the Database object
db = Database(uri, user, password)

try:
    # Define the node to be added
    obj = {
        'id': 'test_node',
        'properties': {
            'text': 'hello world!'
        }
    }

    # Add the node to the database
    db.add(obj, label="test_node")
    print("Node added to the database.")

    # Retrieve the node using a custom query
    query = "MATCH (n {id: 'test_node'}) RETURN n"
    result = db.query(query)
    if result:
        print("Retrieved node:", result)
    else:
        print("Node not found.")

    # Delete the node from the database
    db.remove('test_node')
    print("Node removed from the database.")

except Exception as e:
    print("An error occurred:", e)

finally:
    # Close the database session
    db.close()
    print("Database session closed.")
