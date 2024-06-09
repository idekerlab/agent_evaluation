import unittest
from models.analyst import Analyst
from app.database import Database

class TestAnalyst(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = Database("bolt://localhost:7687", "neo4j", "fredfred")

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_analyst_lifecycle(self):
        analyst = Analyst.create(self.db, "llm_id_123", "Test context", "Prompt template here", "John Doe", "Sample description")
        self.assertIsNotNone(analyst.id)

        loaded_analyst = Analyst.load(self.db, analyst.id)
        self.assertEqual(loaded_analyst.name, "John Doe")

        loaded_analyst.update(name="Jane Doe")
        updated_analyst = Analyst.load(self.db, analyst.id)
        self.assertEqual(updated_analyst.name, "Jane Doe")

if __name__ == '__main__':
    unittest.main()
