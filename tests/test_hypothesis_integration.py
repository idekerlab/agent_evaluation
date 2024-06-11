import unittest

import os 
import sys
sys.path.append(os.path.abspath('..'))
from app.sqlite_database import SqliteDatabase
from app.config import load_database_config
from models.hypothesis import Hypothesis

class TestHypothesisIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db_type, uri, user, password = load_database_config(path='~/ae_config/config.ini')
    
        cls.db = SqliteDatabase(uri)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_hypothesis_lifecycle(self):
        hypothesis = Hypothesis.create(self.db, "data.csv", "Hypothesis text", "analyst123", "dataset123", "Description of the hypothesis", "test123")
        self.assertIsNotNone(hypothesis.id)

        loaded_hypothesis = Hypothesis.load(self.db, hypothesis.id)
        self.assertEqual(loaded_hypothesis.description, "Description of the hypothesis")

        loaded_hypothesis.update(description="Updated description")
        updated_hypothesis = Hypothesis.load(self.db, hypothesis.id)
        self.assertEqual(updated_hypothesis.description, "Updated description")

        loaded_hypothesis.delete()
        self.assertIsNone(Hypothesis.load(self.db, hypothesis.id))

if __name__ == '__main__':
    unittest.main()
