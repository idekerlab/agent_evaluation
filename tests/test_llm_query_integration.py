import unittest
import sys
import os
sys.path.append(os.path.abspath('..'))
from models.llm import LLM
from app.sqlite_database import SqliteDatabase
from app.config import load_database_config

class TestLLMIntegration(unittest.TestCase):
    def setUp(self):
        # Establish a connection to the database
        _, database_uri, _, _ = load_database_config()
        self.db = SqliteDatabase(database_uri)
        self.llm_openai = LLM(self.db, type="OpenAI", model_name="gpt-3.5-turbo-1106", max_tokens=100, seed=42, temperature=0.5)
        self.llm_groq = LLM(self.db, type="Groq", model_name="llama3-70b-8192", max_tokens=100, seed=42, temperature=0.5)
        self.llm_google = LLM(self.db, type="GoogleAI", model_name="gemini-1.5-flash", max_tokens=100, seed=42, temperature=0.5)
        self.llm_local = LLM(self.db, type="LocalModel", model_name="mistral:7b", max_tokens=100, seed=42, temperature=0.5)

    def test_query_openai_real(self):
        context = "Context information"
        prompt = "What is machine learning?"
        response = self.llm_openai.query_openai(context, prompt)
        self.assertIn("machine learning", response.lower())  # Adjust the assertion based on expected response content

    def test_query_groq_real(self):
        context = "Context information"
        prompt = "Explain quantum computing."
        response = self.llm_groq.query_groq(context, prompt)
        self.assertIn("quantum", response.lower())  # Adjust the assertion based on expected response content
    
    def test_query_google_real(self):
        context = "Context information"
        prompt = "What is machine learning?"
        response = self.llm_google.query_google_model(context, prompt)
        self.assertIn("machine learning", response.lower())

    def test_query_local_real(self):   
        context = "Context information"
        prompt = "What is machine learning?"
        response = self.llm_local.query_local_model(context, prompt)
        self.assertIn("machine learning", response.lower())

        

if __name__ == '__main__':
    unittest.main()
