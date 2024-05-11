import unittest
from app.database import Database
from neo4j.exceptions import Neo4jError, ServiceUnavailable
from unittest.mock import MagicMock, patch
import re


class TestDatabase(unittest.TestCase):
    @patch('app.database.GraphDatabase.driver')
    def setUp(self, mock_driver):
        # Setup a mock database connection
        self.uri = "bolt://localhost:7687"
        self.user = "neo4j"
        self.password = "password"
        self.db = Database(self.uri, self.user, self.password)
        self.db.driver = MagicMock()  # Mock the driver object
        self.session = self.db.driver.session.return_value.__enter__.return_value

    def test_add(self):
    # Test adding a new node
        node_id, _ = self.db.add({"name": "test"}, label="TestNode")
        self.assertTrue(re.match(r"TestNode_[0-9a-f-]+", node_id))
        self.session.write_transaction.assert_called_once()

    def test_load(self):
        # Test loading a node
        self.session.read_transaction.return_value = {"name": "test"}
        node = self.db.load("node_id")
        self.session.read_transaction.assert_called_once()
        self.assertEqual(node, {"name": "test"})

    def test_update(self):
        # Test updating a node
        self.session.write_transaction.return_value = None
        result = self.db.update("node_id", {"name": "updated"})
        self.session.write_transaction.assert_called_once()

    def test_remove(self):
        # Test removing a node
        self.session.write_transaction.return_value = None
        self.db.remove("node_id")
        self.session.write_transaction.assert_called_once()

    def test_query(self):
        # Test executing a query
        self.session.read_transaction.return_value = ["result"]
        results = self.db.query("MATCH (n) RETURN n")
        self.session.read_transaction.assert_called_once()
        self.assertEqual(results, ["result"])

if __name__ == '__main__':
    unittest.main()
