from app.database import Database
from agent_evaluation.analyst import Analyst
from agent_evaluation.llm import OpenAI_LLM
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
# base_name = "fred"
# unique_name = f"{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

analyst_context = """
You are a helpful analyst of genomic, proteomic, and other biological data. 
"""

analyst_prompt_template = """ 
The provided proteomics "dataset" includes interacting proteins and the measurements of their differential abundance as a ratio between treated and non-treated samples, where the treatment is the infection of human cells with Dengue virus. 
Not all proteins in the dataset have differential abundance measurements.

The dataset has 2 columns with the following headers: name, DV3_24h-Mock_24h. 
The first column contains the protein names and the last columns contains the abundance measurements.
Please note that measurements <0 reflect a "decreased abundance" while measurements >0 indicate an "increased abundance".

Your task is to leverage this dataset to analyze a subset of interacting proteins that are defined as “proteins of interest".

First, determine what proteins of interest show a differential abundance recorded in the dataset. 
Then, based on this information and on the known functions of all other proteins of interest, 
I want you to generate a hypothesis describing the mechanisms that may contribute to the disease state 
and could potentially be targeted by drug therapies.

Your hypothesis should meet the following criteria:
1) Include one or more molecular mechanism involving one or more proteins of interest
2) Be plausible - grounded in known molecular functions and interactions
3) Be novel - proposing mechanisms either not known or not known to be relevant to the experimental context
4) Be actionable - can be validated with relatively low-cost experimental techniques

When presenting your results, please adhere to the following guidelines:

- Avoid including any code.
- Do not describe the analytical steps you took.
- Do not merely list the proteins of interest, regardless whether they show a differential abundance recorded in the dataset or not.
- Build your hypotheses taking into consideration the interplay among all proteins of interest, not only those that show a differential abundance in the dataset.

- Your output should consist solely of the identified proteins of interest with changed abundance levels, and the hypothesis you propose.

Here is the set of proteins of interest: 
{data}
"""

analyst_description = "Jane the test analyst"     

try:
    # Instantiate the LLM with 'persist=True' and gpt-3.5-turbo-1106
    the_llm = OpenAI_LLM(
        db=db,
        model_name="gpt-3.5-turbo-1106",
        persist=True)
    
    # Instantiate the Analyst with 'persist=True'
    # and specify the LLM by its db_unique_id so that it is loaded from the database
    jane = Analyst(db=db, 
                      llm_unique_id=the_llm.db_unique_id, 
                      context=analyst_context, 
                      prompt_template=analyst_prompt_template, 
                      description=analyst_description, 
                      persist=True)
    
    print(f'analyst = {jane.llm} persisted={jane.persisted} db_unique_id={jane.db_unique_id}')  

except Exception as e:
    print("An error occurred:", e)

finally:
    # remove the Analyst object from the database
    if jane.persisted is True:
        db.remove(jane.db_unique_id)
        print(f"Analyst object {jane.db_unique_id} removed from the database.") 

    # remove the LLM object from the database
    if the_llm.persisted is True:
        db.remove(the_llm.db_unique_id)
        print(f"LLM object {the_llm.db_unique_id} removed from the database.") 

    # Close the database session
    db.close()
    print("Database session closed.")
