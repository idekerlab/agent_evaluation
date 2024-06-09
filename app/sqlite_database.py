import json
import sqlite3
import datetime
import uuid

class SqliteDatabase:
    def __init__(self, uri):
        self.conn = sqlite3.connect(uri)
        self._create_tables()

    def close(self):
        self.conn.close()

    def serialize_properties(self, properties):
        """ Serialize the entire properties dictionary to a JSON string before storing in the database. """
        return json.dumps(properties)

    def deserialize_properties(self, properties):
        """ Deserialize the properties JSON string back into a dictionary. """
        return json.loads(properties)

    def _create_tables(self):
        """ Create the nodes table if it doesn't exist """
        query = """
            CREATE TABLE IF NOT EXISTS nodes (
                object_id TEXT PRIMARY KEY,
                properties TEXT,
                object_type TEXT
            )
        """  # Remove the closing parenthesis at the end of the query
        with self.conn:
            self.conn.execute(query)

    def add(self, object_id=None, properties=None, object_type="node"):
        """ Add a new node to the database """
        if properties is None:
            properties = {}
        properties["created"] = datetime.datetime.now().strftime("%m.%d.%Y %H:%M:%S")
        if object_id is None:   
            object_id = f"{object_type}_{str(uuid.uuid4())}"
        else:
            object_id = object_id

        properties_json = self.serialize_properties(properties)
        try:
            with self.conn:
                self._create_node_sql(object_id, properties_json, object_type)
            return object_id, self.deserialize_properties(properties_json), object_type
        except Exception as e:
            raise Exception(f"Database_Object: Failed to add object to the SQL database. {e}")

    def load(self, object_id):
        """ Load a node from the database by its ID """
        try:
            with self.conn:
                properties_string, object_type = self._get_node_sql(object_id)
                properties = self.deserialize_properties(properties_string) if properties_string else None
                if properties is None:
                    return None
                properties["object_id"] = object_id   
                return properties, object_type
        except Exception as e:
            raise Exception(f"Database_Object: Failed to retrieve object from the SQL database. {e}")

    def remove(self, object_id):
        """ Remove a node from the database by its object_id """
        try:
            with self.conn:
                self._delete_node_sql(object_id)
        except Exception as e:
            raise Exception(f"Database_Object: Failed to remove object from the SQL database. {e}")

    def update(self, object_id, properties):
        """ Update a node's properties in the database """
        # Fetch the existing properties
        existing_properties, _ = self.load(object_id)
        if not existing_properties:
            raise ValueError(f"Object with object_id {object_id} not found.")

        # remove the object_id from existing properties
        existing_properties.pop("object_id")
        # Merge existing properties with new properties
        updated_properties = {**existing_properties, **properties}
        properties_json = self.serialize_properties(updated_properties)
        try:
            with self.conn:
                self._update_node_sql(object_id, properties_json)
        except Exception as e:
            raise Exception(f"Database_Object: Failed to update object in the SQL database. {e}")

    def find(self, object_type):
        """ Find all nodes of a given object type """
        try:
            with self.conn:
                return self._find_nodes_sql(object_type)
        except Exception as e:
            raise Exception(f"Database_Object: Failed to find objects in the SQL database. {e}")

    def _create_node_sql(self, object_id, properties_json, object_type="node"):
        """ Insert a new node into the nodes table """
        query = "INSERT INTO nodes (object_id, properties, object_type) VALUES (?, ?, ?)"
        self.conn.execute(query, (object_id, properties_json, object_type))

    def _get_node_sql(self, object_id):
        """ Retrieve a node's properties from the nodes table by its object_id """
        query = "SELECT properties, object_type FROM nodes WHERE object_id = ?"
        result = self.conn.execute(query, (object_id,)).fetchone()
        return result[0], result[1] if result else None

    def _delete_node_sql(self, object_id):
        """ Delete a node from the nodes table by its object_id """
        query = "DELETE FROM nodes WHERE object_id = ?"
        self.conn.execute(query, (object_id,))

    def _update_node_sql(self, object_id, properties):
        """ Update a node's properties in the nodes table """
        query = "UPDATE nodes SET properties = ? WHERE object_id = ?"
        self.conn.execute(query, (properties, object_id))

    def _find_nodes_sql(self, object_type):
        """ Find all nodes of a given object type """
        query = "SELECT object_id, properties FROM nodes WHERE object_type = ?"
        result = self.conn.execute(query, (object_type,))
        
        valid_results = []
        for row in result:
            try:
                properties = self.deserialize_properties(row[1])
                valid_results.append({"object_id": row[0], "properties": properties})
            except json.JSONDecodeError:
                print(f"Skipping malformed JSON for object_id: {row[0]}")

        return valid_results
    
    def name_is_unique(self, name):
        """ Check if the name is unique in the database """
        query = "SELECT object_id, properties FROM nodes"
        result = self.conn.execute(query).fetchall()
        for row in result:
            properties = json.loads(row[1])
            if properties.get('name') == name:
                return False
        return True

