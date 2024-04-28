import sys
import os

cwd = os.getcwd() # Current working directory
sys.path.append(cwd)# Add to the Python path

from agent_evaluation.temporary_database import TemporaryDatabase
import agent_evaluation.core as ae

# Define the database connection details
uri = "bolt://localhost:7687"
user = "neo4j"
password = "fredfred"

# Create a database instance
# It can be either a neo4j Database object or a TemporaryDatabase object
# db = Database(uri, user, password)
db = TemporaryDatabase()

llm_id = ae.create_llm(type="OpenAI", model_name="gpt-3.5-turbo-1106")

analyst_context = "Cancer research"
analyst_prompt_template = """
Given the following data: 
{data}, and the experiment description: 
{experiment_description}
generate a novel hypothesis providing a mechanistic explanation for some aspect of the data,
followed by a proposal for a validation experiment.
"""

analyst_id_1 = ae.create_analyst(db,
                                 llm_id=llm_id,
                                 context=analyst_context, 
                                 prompt_template=analyst_prompt_template, 
                                 name="Jane")  
                 
analyst_id_2 = ae.create_analyst(db,
                                 llm_id=llm_id, 
                                 context=analyst_context, 
                                 prompt_template=analyst_prompt_template, 
                                 name = "John")                   

data = "...." # some data


dataset_id = ae.create_dataset(db,
                               data=data,
                               experiment_description="Analysis of gene expression and mutations in cancer cells.")    

# test generating a hypothesis in the database
hypothesis_id = ae.generate_hypothesis(analyst_id_1, dataset_id) 
# retrieve the hypothesis from the database
hypothesis_dict = db.load(hypothesis_id)

test_plan_id = ae.create_test_plan([analyst_id_1, analyst_id_2], dataset_id, n_hypotheses=2)

test_id = ae.execute_test_plan(test_plan_id)

reviewer_context = 'You are a scientist adept at impartially evaluating the quality of hypotheses.'   

revewer_prompt_template = """
...
"""

reviewer_id = ae.create_reviewer(llm_id=llm_id, 
                             context=reviewer_context, 
                             prompt_template=revewer_prompt_template, 
                             name="Pasteur")

review_plan_id = ae.create_review_plan([reviewer_id], test_id)

review_id = ae.execute_review_plan(review_plan_id)

# remove the objects from the database
db.remove(analyst_id_1)
db.remove(analyst_id_2)
db.remove(dataset_id)
db.remove(hypothesis_id)
db.remove(test_plan_id)
db.remove(test_id) # this will also first remove the hypotheses
db.remove(reviewer_id)
db.remove(review_plan_id)
db.remove(review_id) # this will also first remove the comparisons



