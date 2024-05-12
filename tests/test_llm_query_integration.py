import unittest
from models.llm import LLM
from app.database import Database
from app.config import load_neo4j_config

class TestLLMIntegration(unittest.TestCase):
    def setUp(self):
        # Load the Neo4j connection details
        uri, user, password = load_neo4j_config()   
        self.db = Database(uri, user, password)

        self.llm_openai = LLM(self.db, type="OpenAI", model_name="gpt-3.5-turbo-1106", max_tokens=100, seed=42, temperature=0.5)
        self.llm_groq = LLM(self.db, type="Groq", model_name="llama3-70b-8192", max_tokens=100, seed=42, temperature=0.5)

    def test_query_openai_real(self):
        context = "Context information"
        prompt = "What is machine learning?"
        response = self.llm_openai.query_openai(context, prompt)
        self.assertIn("machine learning", response)  # Adjust the assertion based on expected response content

    def test_query_groq_real(self):
        context = "Context information"
        prompt = "Explain quantum computing."
        response = self.llm_groq.query_groq(context, prompt)
        self.assertIn("quantum", response)  # Adjust the assertion based on expected response content

if __name__ == '__main__':
    unittest.main()
