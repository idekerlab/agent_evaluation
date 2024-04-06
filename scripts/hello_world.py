from agent_evaluation.database import Database
import sys
import os

# Append the path of the parent directory to sys.path to find the agent_evaluation module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
            'name': 'test',
            'text': 'hello world!'
        }
    }

    # Add the node to the database
    db.add(obj)
    print("Node added to the database.")

    # Retrieve the node using a custom query
    query = "MATCH (n:Node {id: 'test_node'}) RETURN n"
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
