import sys
import os

cwd = os.getcwd()  # Current working directory
sys.path.append(cwd)  # Add to the Python path

import app.ae as ae
from app.database import Database


# bolt+s://deckard.ideker.ucsd.edu/db/data as: neo4j with password: Bl@d3Runn3r

# Define the database connection details
uri = "bolt+s://deckard.ideker.ucsd.edu/db/data"
user = "neo4j"
password = "Bl@d3Runn3r"

print("Creating a database instance...")
db = Database(uri, user, password)

llm_id = 'fake_llm_id'
analyst_context = "Cancer research"
analyst_prompt_template = " Given the following data: {data}, and the experiment description: {experiment_description} generate a novel hypothesis providing a mechanistic explanation for some aspect of the data, followed by a proposal for a validation experiment."

print("Creating an analyst...")
analyst_id_1 = ae.create_analyst(db,
                                 llm_id=llm_id,
                                 context=analyst_context,
                                 prompt_template=analyst_prompt_template,
                                 name="Jane")

analyst_from_db = db.load(analyst_id_1)

print(analyst_from_db)

print("Removing analyst...")
db.remove(analyst_id_1)
