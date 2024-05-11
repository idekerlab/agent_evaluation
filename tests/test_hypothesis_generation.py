import unittest
from services.hypothesis_generation import HypothesisGenerator
from app.database import Database

class TestHypothesisGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = Database("bolt://localhost:7687", "neo4j", "fredfred")
        cls.generator = HypothesisGenerator(cls.db)

    def test_generate_hypothesis_with_test(self):
        # Assuming IDs for an existing analyst, dataset, and test
        analyst_id = "some_analyst_id"
        dataset_id = "some_dataset_id"
        test_id = "some_test_id"
        hypothesis_id = self.generator.generate_hypothesis(analyst_id, dataset_id, test_id=test_id)
        self.assertIsNotNone(hypothesis_id)
        # Optionally, verify that the created hypothesis is linked to the specified test

    def test_generate_hypothesis_without_test(self):
        analyst_id = "some_analyst_id"
        dataset_id = "some_dataset_id"
        hypothesis_id = self.generator.generate_hypothesis(analyst_id, dataset_id)
        self.assertIsNotNone(hypothesis_id)
        # Optionally, verify that the created hypothesis is not linked to any test

if __name__ == '__main__':
    unittest.main()
