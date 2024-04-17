from agent_evaluation.database import Database
from agent_evaluation.analyst import Analyst
from datetime import datetime
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

# Placeholder for initializing the Database instance
# db = Database(uri="your_neo4j_uri", user="your_username", password="your_password")

# Constructing the unique name with datetime
base_name = "fred"
unique_name = f"{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

try:
    # Instantiating the Analyst with 'persist=True' and other placeholder values
    analyst = Analyst(db=db, llm="Test", 
                      context="Test", prompt_template="Test", 
                      name=unique_name, description="Test", 
                      persist=True)

except Exception as e:
    print("An error occurred:", e)

finally:
    # Close the database session
    db.close()
    print("Database session closed.")
