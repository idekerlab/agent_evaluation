import unittest
from app.cxdb import CXDB

class TestCXDB(unittest.TestCase):
    def setUp(self):
        self.cxdb = CXDB()
        self.node_id_1 = self.cxdb.add_node('Alice', 'Person', {'age': 30})
        self.node_id_2 = self.cxdb.add_node('Bob', 'Person', {'age': 25})
        self.cxdb.add_edge(self.node_id_1, self.node_id_2, 'KNOWS', {'since': 2020})

    def test_add_node(self):
        node_id = self.cxdb.add_node('Charlie', 'Person', {'age': 35})
        self.assertEqual(len(self.cxdb.nodes), 3)
        self.assertTrue((self.cxdb.nodes['id'] == node_id).any())
        self.assertTrue((self.cxdb.nodes['name'] == 'Charlie').any())

    def test_delete_node(self):
        self.cxdb.delete_node(self.node_id_1)
        self.assertEqual(len(self.cxdb.nodes), 1)
        self.assertFalse((self.cxdb.nodes['id'] == self.node_id_1).any())
        self.assertEqual(len(self.cxdb.edges), 0)

    def test_update_node(self):
        self.cxdb.update_node(self.node_id_1, properties={'age': 31, 'city': 'New York'})
        node = self.cxdb.nodes[self.cxdb.nodes['id'] == self.node_id_1].iloc[0]
        self.assertEqual(node['properties']['age'], 31)
        self.assertEqual(node['properties']['city'], 'New York')

    def test_update_node_remove_property(self):
        self.cxdb.update_node(self.node_id_1, properties={'age': None})
        node = self.cxdb.nodes[self.cxdb.nodes['id'] == self.node_id_1].iloc[0]
        self.assertNotIn('age', node['properties'])

    def test_add_edge(self):
        self.cxdb.add_edge(self.node_id_2, self.node_id_1, 'FRIENDS', {'since': 2021})
        self.assertEqual(len(self.cxdb.edges), 2)
        self.assertTrue(((self.cxdb.edges['source'] == self.node_id_2) & (self.cxdb.edges['target'] == self.node_id_1) & (self.cxdb.edges['relationship'] == 'FRIENDS')).any())

    def test_delete_edge(self):
        self.cxdb.delete_edge(self.node_id_2, self.node_id_1, 'FRIENDS')
        self.assertEqual(len(self.cxdb.edges), 1)

    def test_update_edge(self):
        self.cxdb.update_edge(self.node_id_1, self.node_id_2, 'KNOWS', properties={'since': 2021})
        edge = self.cxdb.get_edge(self.node_id_1, self.node_id_2, 'KNOWS')
        self.assertEqual(edge['properties']['since'], 2021)

   