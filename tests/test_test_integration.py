import unittest
from models.analysis_run import Test
from app.database import Database

class TestTestIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = Database("bolt://localhost:7687", "neo4j", "fredfred")

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_test_lifecycle(self):
        test = Test.create(self.db, ["analyst1", "analyst2"], "dataset123", 3, 
                           ["hypothesis1", "hypothesis2"], "Test description")
        self.assertIsNotNone(test.id)
        self.assertIsNotNone(test.created)

        loaded_test = Test.load(self.db, test.id)
        self.assertEqual(loaded_test.description, "Test description")

        loaded_test.update(description="Updated Test description")
        updated_test = Test.load(self.db, test.id)
        self.assertEqual(updated_test.description, "Updated Test description")

        loaded_test.delete()
        self.assertIsNone(Test.load(self.db, test.id))

if __name__ == '__main__':
    unittest.main()
 