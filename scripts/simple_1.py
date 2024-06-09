
import sys
import os

cwd = os.getcwd()  # Current working directory
sys.path.append(cwd)  # Add to the Python path

import app.ae as ae
from app.temporary_database import TemporaryDatabase
from app.database import Database


from agent_evaluation.hierarchy import Hierarchy
import json
import ndex2 
from ndex2.cx2 import RawCX2NetworkFactory

# Create NDEx2 python client
client = ndex2.client.Ndex2()

# Create CX2Network factory
factory = RawCX2NetworkFactory()

# Define the database connection details
uri = "bolt://localhost:7687"
user = "neo4j"
password = "fredfred"

# Create a database instance
# It can be either a neo4j Database object or a TemporaryDatabase object
db = Database(uri, user, password)
# db = TemporaryDatabase()

# llm_id = ae.create_llm(db, type="OpenAI", model_name="gpt-3.5-turbo-1106")
llm_id = ae.create_llm(db, type="Groq", model_name="llama3-8b-8192")
print(db.load(llm_id))

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
                                 name="John")

# Dengue string interactome network c223d6db-b0e2-11ee-8a13-005056ae23aa
client_resp = client.get_network_as_cx2_stream('c223d6db-b0e2-11ee-8a13-005056ae23aa')

# Convert downloaded interactome network to CX2Network object
interactome = factory.get_cx2network(json.loads(client_resp.content))

# Display information about the interactome network 
print('Name: ' + interactome.get_name())
print('Number of nodes: ' + str(len(interactome.get_nodes())))
print('Number of edges: ' + str(len(interactome.get_edges())))

# Dengue hierarchy
# https://www.ndexbio.org/viewer/networks/59bbb9f1-e029-11ee-9621-005056ae23aa
client_resp = client.get_network_as_cx2_stream('59bbb9f1-e029-11ee-9621-005056ae23aa')

# Convert downloaded interactome network to CX2Network object
hierarchy = factory.get_cx2network(json.loads(client_resp.content))

# Display information about the hierarchy network and output 1st 100 characters of CX2
print('Name: ' + hierarchy.get_name())
print('Number of nodes: ' + str(len(hierarchy.get_nodes())))
print('Number of edges: ' + str(len(hierarchy.get_edges())))

dengue_hierarchy = Hierarchy(hierarchy, interactome)
print(dengue_hierarchy.get_experiment_description())
datasets = dengue_hierarchy.get_datasets(member_attributes=["name", "DV3_24h-Mock_24h"],
                                         filter={"max_size": 6})[32:33:]   #[1:33:31]          

data = datasets[0].get("data")


dataset_id = ae.create_dataset(db,
                               data=str(data),
                               experiment_description="Analysis of differential abundance of proteins at 24 hours in dengue infected cells.")

# test generating a hypothesis in the database
# hypothesis_id = ae.generate_hypothesis(db,
#                                        analyst_id_1, 
#                                        dataset_id)
# retrieve the hypothesis from the database
# hypothesis_dict = db.load(hypothesis_id)

# print(hypothesis_dict.get("hypothesis_text"))

test_plan_id = ae.create_test_plan(db, 
                                   [analyst_id_1, analyst_id_2], 
                                   dataset_id, 
                                   n_hypotheses_per_analyst=2)

print("running create_test")
test_id = ae.create_test(db, test_plan_id)

reviewer_context = 'You are a scientist adept at impartially evaluating the quality of hypotheses.'

revewer_prompt_template = """
Please review this formatted data from a set of 'omics experiments, followed by hypotheses about the data.
REMEMBER, a fold change value below 1.0 is a decrease in abundance, and a fold change value above 1.0 is an increase in abundance.
Treat all fold change values between 0.95 and 1.05 as not significantly different from 1.0, i.e., no change in abundance.
Your task is to compare the hypotheses and provide a ranking of the hypotheses based on their novelty, 
quality of scientific reasoning, and factual accuracy. Your report should include a rationale for the ranking.

Here an example of the yaml output format that you should use:

- hypothesis_id: MAPLE
  ranking: 2
  rationale: >
    This hypothesis is plausible and well reasoned but is not novel: 
    the fact that AKT1 can phosphorylate GSK3B is well known.

- hypothesis_id: ASPEN
  ranking: 3
  rationale: >
    While this hypothesis is novel, it is implausible because it 
    depends on unsupported statements, such as the claim that RB1 
    is a transcription factor.

- hypothesis_id: WILLOW
  ranking: 1
  rationale: >
    This hypothesis is a highly novel and convincing explanation 
    for the observed upregulation of NFKB1.
<data>
{data}
</data>
<hypotheses>
{hypotheses_section}
</hypotheses>
"""

reviewer_id = ae.create_reviewer(db,
                                 llm_id=llm_id,
                                 context=reviewer_context,
                                 prompt_template=revewer_prompt_template,
                                 name="Pasteur")

review_plan_id = ae.create_review_plan(db,[reviewer_id], test_id)

review_set_id = ae.create_review_set(db, review_plan_id)

review_set = db.load(review_set_id)
review_ids = ae.get_property(review_set, "review_ids")
review = db.load(review_ids[0]) 
print("----------------------------------------")
print(data)
print("----------------------------------------")
print(ae.get_property(review, "hypotheses_section"))
print("----------------------------------------")
print(ae.get_property(review, "result"))   


# remove the objects from the database
clean_up = False
if clean_up is True:
    db.remove(analyst_id_1)
    db.remove(analyst_id_2)
    db.remove(dataset_id)
    db.remove(test_plan_id)
    db.remove(test_id)  # note that this doesn't remove the hypotheses
    db.remove(reviewer_id)
    db.remove(review_plan_id)
    db.remove(review_set_id)  # this will also not remove the reviews

