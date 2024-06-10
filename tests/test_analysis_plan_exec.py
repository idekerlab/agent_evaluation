import unittest
import pandas as pd
import os
import sys
sys.path.append(os.path.abspath('..'))
from models.llm_old import LLM
from models.analyst import Analyst
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

        _, database_uri, _, _ = load_database_config()
        self.db = SqliteDatabase(database_uri)


    def test_full_analysis_workflow(self):

        # Load a AnalysisPlan
        self.analysis_plan = AnalysisPlan.load(self.db, "analysis_plan_9645e69f-565d-44fe-8b0a-b4e8a66bd37f")

        # Generate an AnalysisRun from the AnalysisPlan
        analysis_run = self.analysis_plan.generate_analysis_run()

        # Run analysis using AnalysisRunner
        runner = AnalysisRunner(self.db, analysis_run.object_id)
        result = runner.run()
        self.assertIn("All hypotheses generated or attempts exhausted.", result)

if __name__ == '__main__':
    unittest.main()
