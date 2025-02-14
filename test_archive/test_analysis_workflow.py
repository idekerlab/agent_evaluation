import unittest
import pandas as pd
import os
import sys
sys.path.append(os.path.abspath('..'))
from models.llm import LLM
from models.agent import Agent
from models.dataset import Dataset
from models.analysis_plan import AnalysisPlan
from services.analysisrunner import AnalysisRunner
from app.sqlite_database import SqliteDatabase
from app.config import load_database_config

class TestAnalysisWorkflow(unittest.TestCase):
    def setUp(self):
        # Load the db connection details
        # db_type, uri, user, password = load_database_config(path='~/ae_config/test_config.ini')
        # self.db = Database(uri, db_type, user, password)

        _, database_uri, _, _ = load_database_config(path='~/ae_config/test_config.ini')
        self.db = SqliteDatabase(database_uri)

        # Load data
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_file_path = os.path.join(project_root, "files", "dengue_with_uniprot_top_49.csv")
        data = pd.read_csv(data_file_path).to_csv(index=False)

        context = "Host-virus infection mechanisms, immune response."
        prompt_template = """
Please analyze these results of these experiments: {experiment_description}

Here is the data in CSV format:
{data}

Generate a hypothesis providing a mechanistic explanation for some aspect of the data.
Use your knowledge of host-virus infection mechanisms and the immune response to 
produce a NOVEL hypothesis, not one where the relationships and causal effect is already 
known or would be unsurprising to a researcher.
Focus on causal relationships between proteins and their role in the immune response.
Followed the hypothesis with a proposal for a validation experiment.
Choose a name for the hypothesis and put it before the main hypothesis text.
"""

        # Create LLM
        self.llm = LLM.create(self.db, type="Groq", model_name="llama3-70b-8192") 
        
        # Create analyst
        self.analyst = Agent.create(self.db, self.llm.object_id, context , prompt_template)

        experiment_description = "Dengue virus infection in human cells"

        # Create dataset
        self.dataset = Dataset.create(self.db, 
                                      "dengue data",
                                      data, 
                                      experiment_description)

        # Create a AnalysisPlan
        self.analysis_plan = AnalysisPlan.create(self.db, 
                                         [self.analyst.object_id], 
                                         self.dataset.object_id, 1, 
                                         "Analysis Plan for Dengue Research")

    def test_full_analysis_workflow(self):
        # Generate an AnalysisRun from the AnalysisPlan
        analysis_run = self.analysis_plan.generate_analysis_run()

        # Run analysis using AnalysisRunner
        runner = AnalysisRunner(self.db, analysis_run.object_id)
        result = runner.run()
        self.assertIn("All hypotheses generated or attempts exhausted.", result)

if __name__ == '__main__':
    unittest.main()
