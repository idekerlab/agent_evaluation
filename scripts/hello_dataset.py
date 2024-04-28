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

from app.database import Database
from agent_evaluation.dataset import Dataset

# Define the database connection details
uri = "bolt://localhost:7687"
user = "neo4j"
password = "fredfred"

# Initialize the Database object
db = Database(uri, user, password)

try:
    # Creating a new dataset
    data = """
        gene_symbol, expression, mutation
        BRCA1, high, no
        TP53, low, yes
        """
    
    new_dataset = Dataset(
        db=db,
        genes_of_interest={'BRCA1', 'TP53'},
        data=data,
        experiment_description="Analysis of gene expression and mutations in cancer cells.",
        persist=True
    )
    print(f"New Dataset: {new_dataset.db_unique_id} experiment_description: {new_dataset.experiment_description} data: {new_dataset.data}  genes_of_interest: {new_dataset.genes_of_interest}  ")


    # new_dataset is now persisted. An instance can be loaded based on the unique identifier
    existing_dataset = Dataset(db=db, db_unique_id=new_dataset.db_unique_id)

    print(f"Existing Dataset: {existing_dataset.db_unique_id} experiment_description: {existing_dataset.experiment_description} data: {existing_dataset.data}  genes_of_interest: {existing_dataset.genes_of_interest}  ")

    print("Loading the existing dataset")
    existing_dataset.load()

    print(f"Existing Dataset: {existing_dataset.db_unique_id} experiment_description: {existing_dataset.experiment_description} data: {existing_dataset.data}  genes_of_interest: {existing_dataset.genes_of_interest}  ")

    # Print details to verify
    print(f"Loaded Dataset: {existing_dataset.db_unique_id}")
    print(f"Description: {existing_dataset.experiment_description}")
    print(f"Data: {existing_dataset.data}")

except Exception as e:
    print("An error occurred:", e)

finally:
    # remove the Dataset object from the database
    if new_dataset.persisted is True:
        db.remove(new_dataset.db_unique_id)
        print(f"Dataset object {new_dataset.db_unique_id} removed from the database.")  

    # Close the database session
    db.close()
    print("Database session closed.")

