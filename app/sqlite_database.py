import json
import sqlite3
import datetime
import uuid

class SqliteDatabase:
    def __init__(self, uri):
        self.uri = uri
        # Create initial connection to set up tables
        with self._get_connection() as conn:
            self._create_tables(conn)

    def _get_connection(self):
        """Get a new connection for the current thread."""
        return sqlite3.connect(self.uri)

    def close(self):
        """No-op since we don't maintain persistent connections."""
        pass

    def serialize_properties(self, properties):
        """ Serialize the entire properties dictionary to a JSON string before storing in the database. """
        return json.dumps(properties)

    def deserialize_properties(self, properties):
        """ Deserialize the properties JSON string back into a dictionary. """
        return json.loads(properties)

    def _create_tables(self, conn):
        """ Create the nodes table if it doesn't exist """
        query = """
            CREATE TABLE IF NOT EXISTS nodes (
                object_id TEXT PRIMARY KEY,
                properties TEXT,
                object_type TEXT
            )
        """
        conn.execute(query)

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
            with self._get_connection() as conn:
                self._create_node_sql(conn, object_id, properties_json, object_type)
            return object_id, self.deserialize_properties(properties_json), object_type
        except Exception as e:
            raise Exception(f"Database_Object: Failed to add object to the SQL database. {e}")

    def load(self, object_id):
        """ Load a node from the database by its ID """
        try:
            with self._get_connection() as conn:
                properties_string, object_type = self._get_node_sql(conn, object_id)
                properties = self.deserialize_properties(properties_string) if properties_string else None
                if properties is None:
                    return None, None
                properties["object_id"] = object_id   
                return properties, object_type
        except Exception as e:
            raise Exception(f"Database_Object: Failed to retrieve object from the SQL database. {e}")

    def remove(self, object_id):
        """ Remove a node from the database by its object_id """
        try:
            with self._get_connection() as conn:
                self._delete_node_sql(conn, object_id)
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
            with self._get_connection() as conn:
                self._update_node_sql(conn, object_id, properties_json)
        except Exception as e:
            raise Exception(f"Database_Object: Failed to update object in the SQL database. {e}")

    def find(self, object_type, properties_filter=None, raw_where_clause=None):
        """ Find all nodes of a given object type with optional property filtering
        
        Args:
            object_type: Type of objects to find
            properties_filter: Dictionary of property key-value pairs to filter by.
                             Values can be strings, in which case exact match is used,
                             or dictionaries with an 'operator' key ('like') and 'value' key
                             for LIKE matching.
                             Example: {'name': 'test'} - exact match
                                     {'name': {'operator': 'like', 'value': '%test%'}} - LIKE match
        """
        try:
            with self._get_connection() as conn:
                return self._find_nodes_sql(conn, object_type, properties_filter, raw_where_clause)
        except Exception as e:
            raise Exception(f"Database_Object: Failed to find objects in the SQL database. {e}")

    def _create_node_sql(self, conn, object_id, properties_json, object_type="node"):
        """ Insert a new node into the nodes table """
        query = "INSERT INTO nodes (object_id, properties, object_type) VALUES (?, ?, ?)"
        conn.execute(query, (object_id, properties_json, object_type))

    def _get_node_sql(self, conn, object_id):
        """ Retrieve a node's properties from the nodes table by its object_id """
        query = "SELECT properties, object_type FROM nodes WHERE object_id = ?"
        result = conn.execute(query, (object_id,)).fetchone()
        if result:
            return result[0], result[1]
        return None, None

    def _delete_node_sql(self, conn, object_id):
        """ Delete a node from the nodes table by its object_id """
        query = "DELETE FROM nodes WHERE object_id = ?"
        conn.execute(query, (object_id,))

    def _update_node_sql(self, conn, object_id, properties):
        """ Update a node's properties in the nodes table """
        query = "UPDATE nodes SET properties = ? WHERE object_id = ?"
        conn.execute(query, (properties, object_id))

    def _find_nodes_sql(self, conn, object_type, properties_filter=None, raw_where_clause: str = None):
        """ Find all nodes of a given object type with property filtering """
        query = "SELECT object_id, properties FROM nodes WHERE object_type = ?"
        params = [object_type]
        if raw_where_clause:
            query += f" AND {raw_where_clause}"

        if properties_filter:
            for key, value in properties_filter.items():
                if isinstance(value, dict) and 'operator' in value and value['operator'].lower() == 'like':
                    # Handle LIKE operator
                    query += f" AND json_extract(properties, '$.{key}') LIKE ?"
                    params.append(value['value'])
                else:
                    # Handle exact match
                    query += f" AND json_extract(properties, '$.{key}') = ?"
                    params.append(str(value))  # Convert to string since JSON properties are stored as strings
        
        result = conn.execute(query, params)
        
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
        with self._get_connection() as conn:
            result = conn.execute(query).fetchall()
        for row in result:
            properties = json.loads(row[1])
            if properties.get('name') == name:
                return False
        return True
