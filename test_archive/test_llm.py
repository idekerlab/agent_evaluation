import unittest
from unittest.mock import MagicMock, patch
import sys
import os
sys.path.append(os.path.abspath('..'))
from models.llm import LLM
from app.sqlite_database import SqliteDatabase

class TestLLM(unittest.TestCase):
    @patch('app.sqlite_database.SqliteDatabase')
    def setUp(self, mock_db):
        # Mock the database and initialize LLM with it
        self.db = mock_db()
        self.type = 'OpenAI'
        self.model_name = 'gpt-3.5-turbo-1106'
        self.max_tokens = 2048
        self.seed = 42
        self.temperature = 0.5
        self.llm = LLM(self.db, self.type, self.model_name, self.max_tokens, self.seed, self.temperature)

    def test_create_llm(self):
        # Test creating an LLM instance
        with patch.object(LLM, 'create', return_value=self.llm) as mock_create:
            llm_instance = LLM.create(self.db, self.type, self.model_name, self.max_tokens, self.seed, self.temperature)
            mock_create.assert_called_once_with(self.db, self.type, self.model_name, self.max_tokens, self.seed, self.temperature)
            self.assertIsInstance(llm_instance, LLM)

    def test_load_llm(self):
        # Test loading an LLM instance
        with patch.object(LLM, 'load', return_value=self.llm) as mock_load:
            llm_instance = LLM.load(self.db, 'object_id')
            mock_load.assert_called_once_with(self.db, 'object_id')
            self.assertIsInstance(llm_instance, LLM)

    def test_update_llm(self):
        # Test updating an LLM instance
        new_temperature = 0.7
        with patch.object(self.db, 'update') as mock_update:
            self.llm.update(temperature=new_temperature)
            mock_update.assert_called_once_with(self.llm.object_id, {'temperature': new_temperature})

if __name__ == '__main__':
    unittest.main()
