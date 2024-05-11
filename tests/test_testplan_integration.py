import unittest
from models.testplan import TestPlan
from app.database import Database

class TestTestPlan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = Database("bolt://localhost:7687", "neo4j", "fredfred")

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_testplan_lifecycle(self):
        testplan = TestPlan.create(self.db, ["analyst1", "analyst2"], "dataset123", 3, "Test plan description")
        self.assertIsNotNone(testplan.id)

        loaded_testplan = TestPlan.load(self.db, testplan.id)
        self.assertEqual(loaded_testplan.n_hypotheses_per_analyst, 3)

        loaded_testplan.update(n_hypotheses_per_analyst=5)
        updated_testplan = TestPlan.load(self.db, testplan.id)
        self.assertEqual(updated_testplan.n_hypotheses_per_analyst, 5)

        loaded_testplan.delete()
        self.assertIsNone(TestPlan.load(self.db, testplan.id))

if __name__ == '__main__':
    unittest.main()
