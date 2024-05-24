import unittest
from unittest.mock import MagicMock
from models.analysis_plan import TestPlan
from services.analysisrunner import AnalysisRunner

class TestAnalysisWorkflow(unittest.TestCase):
    def setUp(self):
        # Assuming db is some kind of database interface that you've defined
        self.db = MagicMock()
        self.testplan_id = "tp123"
        self.test_id = "t123"
        self.analyst_ids = ['a1', 'a2']
        self.dataset_id = 'd1'
        self.n_hypotheses_per_analyst = 2

        # Mock database loading mechanisms
        self.db.add = MagicMock(return_value=(self.testplan_id, "2024-05-10"))
        self.db.load = MagicMock(side_effect=self.db_load)

    def db_load(self, id):
        if id == self.testplan_id:
            return {
                "id": self.testplan_id,
                "analyst_ids": self.analyst_ids,
                "dataset_id": self.dataset_id,
                "n_hypotheses_per_analyst": self.n_hypotheses_per_analyst,
                "description": "Test test plan"
            }
        elif id == self.test_id:
            return {
                "id": self.test_id,
                "testplan_id": self.testplan_id,
                "analyst_ids": self.analyst_ids,
                "dataset_id": self.dataset_id,
                "n_hypotheses_per_analyst": self.n_hypotheses_per_analyst,
                "hypothesis_ids": [],
                "attempts": {analyst: [] for analyst in self.analyst_ids},
                "status": "pending"
            }
        return None

    def test_full_analysis_workflow(self):
        # Create TestPlan
        testplan = TestPlan.create(self.db, self.analyst_ids, self.dataset_id, self.n_hypotheses_per_analyst, "A test plan for integration testing")

        # Generate a Test from the TestPlan
        test = testplan.generate_test()

        # Run analysis using AnalysisRunner
        runner = AnalysisRunner(self.db, test.id)
        result = runner.run()
        self.assertTrue("All hypotheses generated or attempts exhausted." in result)

if __name__ == '__main__':
    unittest.main()
