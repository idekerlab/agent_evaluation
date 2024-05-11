import unittest
from models.dataset import Dataset
from app.database import Database

class TestDataset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = Database("bolt://localhost:7687", "neo4j", "fredfred")

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_dataset_lifecycle(self):
        dataset = Dataset.create(self.db, "Data Set 1", "data.csv", "A test experiment", "Sample dataset description")
        self.assertIsNotNone(dataset.id)

        loaded_dataset = Dataset.load(self.db, dataset.id)
        self.assertEqual(loaded_dataset.name, "Data Set 1")

        loaded_dataset.update(name="Data Set 2")
        updated_dataset = Dataset.load(self.db, dataset.id)
        self.assertEqual(updated_dataset.name, "Data Set 2")

        self.assertIsNotNone(updated_dataset.created)

        loaded_dataset.delete()
        self.assertIsNone(Dataset.load(self.db, dataset.id))

if __name__ == '__main__':
    unittest.main()
