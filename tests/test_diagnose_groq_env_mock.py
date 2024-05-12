import unittest
from unittest.mock import patch, MagicMock
from models.llm import LLM

class TestLLM(unittest.TestCase):
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'fakekey', 'GROQ_API_KEY': 'fakekey'})
    def setUp(self):
        self.db = MagicMock()
        self.llm_openai = LLM(self.db, type="OpenAI", model_name="gpt-3.5-turbo", max_tokens=100, seed=42, temperature=0.5)
        self.llm_groq = LLM(self.db, type="Groq", model_name="groq-model-v1", max_tokens=100, seed=42, temperature=0.5)

    def test_query_groq_no_api_key(self):
        with patch.dict('os.environ', {'GROQ_API_KEY': 'oh_come_on_now'}):
            with self.assertRaises(EnvironmentError):
                self.llm_groq.query_groq("Test context", "Test prompt")

if __name__ == '__main__':
    unittest.main()


#
