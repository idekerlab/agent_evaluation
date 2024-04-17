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

from agent_evaluation.database import Database
from agent_evaluation.llm import OpenAI_LLM

# Define the database connection details
uri = "bolt://localhost:7687"
user = "neo4j"
password = "fredfred"

# Initialize the Database object
db = Database(uri, user, password)

try:
    # Instantiating the LLM with 'persist=True' and other placeholder values
    gpt_3_5 = OpenAI_LLM(
        db=db,
        model_name="gpt-3.5-turbo-1106",
        persist=False)
    
    response, tokens_used = gpt_3_5.query(
        "you are a helpful assistant. ", 
        "What is the captial of France? Answer in one sentence.")
    print(response)

    # remove the LLM object from the database
    db.remove(gpt_3_5.id)
except Exception as e:
    print("hello_llm: An error occurred:", e)

finally:
    # remove the # Close the database session
    db.close()
    print("Database session closed.")
