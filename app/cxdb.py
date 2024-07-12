import pandas as pd

class CXDB:
    def __init__(self):
        self.nodes = pd.DataFrame(columns=['id', 'name', 'type', 'properties'])
        self.edges = pd.DataFrame(columns=['source', 'target', 'relationship', 'properties'])
        self.next_node_id = 1
        self.node_names = set()

    def add_node(self, name, type, properties=None):
        if name in self.node_names:
            raise ValueError("Node name must be unique")
        if properties is None:
            properties = {}
        node_id = self.next_node_id
        self.next_node_id += 1
        new_node = pd.DataFrame([[node_id, name, type, properties]], columns=self.nodes.columns)
        self.nodes = pd.concat([self.nodes, new_node], ignore_index=True)
        self.node_names.add(name)
        return node_id

    def delete_node(self, node_id):
        node_name = self.nodes.loc[self.nodes['id'] == node_id, 'name'].values[0]
        self.node_names.remove(node_name)
        self.nodes = self.nodes[self.nodes['id'] != node_id]
        self.edges = self.edges[(self.edges['source'] != node_id) & (self.edges['target'] != node_id)]

    def update_node(self, node_id, name=None, type=None, properties=None):
        node_index = self.nodes[self.nodes['id'] == node_id].index
        
        if node_index.empty:
            raise ValueError("Node not found")
        
        if name:
            if name in self.node_names:
                raise ValueError("Node name must be unique")
            old_name = self.nodes.at[node_index[0], 'name']
            self.node_names.remove(old_name)
            self.nodes.at[node_index[0], 'name'] = name
            self.node_names.add(name)
        
        if type:
            self.nodes.at[node_index[0], 'type'] = type
        
        if properties:
            current_properties = self.nodes.at[node_index[0], 'properties']
            for key, value in properties.items():
                if value is None:
                    current_properties.pop(key, None)
                else:
                    current_properties[key] = value
            self.nodes.at[node_index[0], 'properties'] = current_properties
        
        return node_id

    def add_edge(self, source, target, relationship, properties=None):
        if properties is None:
            properties = {}
        new_edge = pd.DataFrame([[source, target, relationship, properties]], columns=self.edges.columns)
        self.edges = pd.concat([self.edges, new_edge], ignore_index=True)

    def delete_edge(self, source, target, relationship):
        self.edges = self.edges[~((self.edges['source'] == source) & (self.edges['target'] == target) & (self.edges['relationship'] == relationship))]

    def update_edge(self, source, target, relationship, properties=None):
        if properties:
            edge_index = self.edges[(self.edges['source'] == source) & 
                                    (self.edges['target'] == target) & 
                                    (self.edges['relationship'] == relationship)].index
            
            if edge_index.empty:
                raise ValueError("Edge not found")

            # Get the current properties
            current_properties = self.edges.at[edge_index[0], 'properties']

            # Update properties
            for key, value in properties.items():
                if value is None:
                    current_properties.pop(key, None)
                else:
                    current_properties[key] = value

            # Assign the updated properties back to the DataFrame
            self.edges.at[edge_index[0], 'properties'] = current_properties


    def get_edge(self, source, target, relationship):
        edge = self.edges[(self.edges['source'] == source) & 
                        (self.edges['target'] == target) & 
                        (self.edges['relationship'] == relationship)]
        if not edge.empty:
            return edge.iloc[0]
        return None

    def query(self, cypher):
        tokens = cypher.strip().split()
        if tokens[0].upper() == "MATCH":
            pattern = tokens[1]
            if pattern.startswith("(") and pattern.endswith(")"):
                node_type = pattern[1:-1]
                result_nodes = self.nodes[self.nodes['type'] == node_type]
                return result_nodes
            elif pattern.startswith("(") and ")-[" in pattern and "]->(" in pattern:
                source_type = pattern.split(")-[")[0][1:]
                relationship = pattern.split("]-[")[1].split("]->")[0]
                target_type = pattern.split("]->(")[1][:-1]
                
                matched_edges = self.edges[self.edges['relationship'] == relationship]
                
                matched_edges = matched_edges.merge(self.nodes[self.nodes['type'] == source_type], left_on='source', right_on='id', suffixes=('', '_source'))
                matched_edges = matched_edges.merge(self.nodes[self.nodes['type'] == target_type], left_on='target', right_on='id', suffixes=('', '_target'))
                
                return matched_edges[['source', 'target', 'relationship', 'properties']]
        return pd.DataFrame() # Return an empty DataFrame if the query is not supported

# # Example usage
# cxdb = CXDB()
# node_id_1 = cxdb.add_node('Alice', 'Person', {'age': 30})
# node_id_2 = cxdb.add_node('Bob', 'Person', {'age': 25})
# cxdb.add_edge(node_id_1, node_id_2, 'KNOWS', {'since': 2020})

# # Query nodes
# print(cxdb.query("MATCH (Person)"))

# # Query edges
# print(cxdb.query("MATCH (Person)-[KNOWS]->(Person)"))

# # Update node
# cxdb.update_node(node_id_1, properties={'age': 31})

# # Delete edge
# cxdb.delete_edge(node_id_1, node_id_2, 'KNOWS')

# # Delete node
# cxdb.delete_node(node_id_2)