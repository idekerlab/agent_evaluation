import unittest
from neo4j import GraphDatabase
from unittest.mock import MagicMock

from agent_evaluation.database import Database
from unittest.mock import MagicMock

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.driver = MagicMock(spec=GraphDatabase.driver)
        self.database = Database(uri="bolt://localhost:7687", user="agent_evaluation", password="agent_evaluation")
        # self.database.driver = self.driver
        

    def tearDown(self):
        self.patcher.stop()

    def test_add(self):
        obj = {"id": 1, "properties": {"name": "Test"}}
        self.database.add(obj)
        self.driver.session().write_transaction.assert_called_once_with(self.database._create_node, obj)

    def test_get(self):
        id = 1
        self.database.get(id)
        self.driver.session().read_transaction.assert_called_once_with(self.database._get_node, id)

    def test_remove(self):
        id = 1
        self.database.remove(id)
        self.driver.session().write_transaction.assert_called_once_with(self.database._delete_node, id)

    def test_query(self):
        query = "MATCH (n:Node) RETURN n"
        self.database.query(query)
        self.driver.session().read_transaction.assert_called_once_with(self.database._execute_query, query)

    def test_search_exact(self):
        name = "Test"
        self.database.search(name, type="exact")
        self.driver.session().run.assert_called_once_with("MATCH (n:Node {name: $name}) RETURN n", name=name)

    def test_search_contains(self):
        name = "Test"
        self.database.search(name, type="contains")
        self.driver.session().run.assert_called_once_with("MATCH (n:Node) WHERE n.name CONTAINS $name RETURN n", name=name)

    def test_search_invalid_type(self):
        name = "Test"
        with self.assertRaises(ValueError):
            self.database.search(name, type="invalid")

    def test_search_by_type_and_date(self):
        obj_type = "Test"
        self.database.search_by_type_and_date(obj_type)
        self.driver.session().run.assert_called_once_with("MATCH (n:Node {type: $type}) WHERE 1=1  RETURN n ORDER BY n.date DESC LIMIT 1", type=obj_type)

if __name__ == '__main__':
    unittest.main()