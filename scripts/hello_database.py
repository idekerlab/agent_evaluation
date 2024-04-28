import sys
import os

cwd = os.getcwd() # Current working directory
dirname = os.path.dirname(cwd) # Parent directory
# print("================")
# print(cwd)
# print(dirname)
sys.path.append(cwd)# Add the parent directory to the Python path
# print("================")
# print(sys.path)
# print("================")

from agent_evaluation.database import Database
from neo4j.exceptions import Neo4jError, ServiceUnavailable 


# Define the database connection details
uri = "bolt://localhost:7687"
user = "neo4j"
password = "fredfred"


# Create an instance of the Database class
db = Database(uri, user, password)

# Define the object to be added
bob = {
    'id': 'bob',
    'properties': {
        'name': 'robert'
    }
}

# Add the object to the database
try:
    db.add(bob, label="Person")
    print("Added Bob to the database.")
except Neo4jError as e:
    print(f"Error adding Bob to the database: {e}")

# Retrieve and print the object
try:
    bob_node = db.get('bob')
    if bob_node:
        print("Retrieved Bob from the database:", dict(bob_node))
    else:
        print("Bob not found in the database.")
except Neo4jError as e:
    print(f"Error retrieving Bob from the database: {e}")

# Remove the object from the database
try:
    db.remove('bob')
    print("Bob removed from the database.")
except Neo4jError as e:
    print(f"Error removing Bob from the database: {e}")

# Check if the object is still there
try:
    bob_node = db.get('bob')
    if not bob_node:
        print("Bob is successfully removed from the database.")
    else:
        print("Bob is still in the database.")
except Neo4jError as e:
    print(f"Error checking Bob in the database: {e}")

# Close the database connection
db.close()
