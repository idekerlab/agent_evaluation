import unittest
from models.llm import LLM
from app.database import Database

class TestLLMIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Establish a connection to the Neo4j database
        cls.db = Database("bolt://localhost:7687", "neo4j", "fredfred")

    @classmethod
    def tearDownClass(cls):
        # Close the database connection
        cls.db.close()

    def test_llm_integration(self):
        # Test the integration of creating, loading, updating, and deleting an LLM

        # Create an LLM
        llm = LLM.create(self.db, type="OpenAI", model_name="gpt-3.5-turbo", max_tokens=2048, seed=42, temperature=0.5)
        self.assertIsNotNone(llm.id)

        # Load the LLM
        loaded_llm = LLM.load(self.db, llm.id)
        self.assertEqual(loaded_llm.model_name, "gpt-3.5-turbo")

        # Update the LLM
        new_temperature = 0.7
        loaded_llm.update(temperature=new_temperature)
        updated_llm = LLM.load(self.db, llm.id)
        self.assertEqual(updated_llm.temperature, new_temperature)

        # Delete the LLM
        self.db.remove(loaded_llm.id)
        self.assertIsNone(LLM.load(self.db, loaded_llm.id))

if __name__ == '__main__':
    unittest.main()
