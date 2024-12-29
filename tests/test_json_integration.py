import unittest
import sys
import os
sys.path.append(os.path.abspath('..'))
from models.json_object import Json
from app.sqlite_database import SqliteDatabase
from app.config import load_database_uri

class TestJsonIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Establish a connection to the database
        uri = load_database_uri()
        cls.db = SqliteDatabase(uri)

    @classmethod
    def tearDownClass(cls):
        # Close the database connection
        cls.db.close()

    def test_json_integration(self):
        # Test the integration of creating, loading, and deleting a JSON object
        
        # Create a test JSON object
        test_json = {
            "name": "Test Structure",
            "levels": {
                "level1": {
                    "data": [1, 2, 3],
                    "nested": {"key": "value"}
                }
            }
        }
        
        json_obj = Json(name="Test JSON Object", json_data=test_json)
        
        # Add to database
        object_id, _, _ = self.db.add(None, json_obj.to_dict(), "json")
        
        # Load from database
        loaded_properties, loaded_type = self.db.load(object_id)
        
        # Verify the loaded object
        self.assertEqual(loaded_type, "json")
        self.assertEqual(loaded_properties["name"], "Test JSON Object")
        self.assertEqual(loaded_properties["json"], test_json)
        
        # Clean up
        self.db.remove(object_id)

if __name__ == '__main__':
    unittest.main() 