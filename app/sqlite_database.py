import json
from sqlalchemy import create_engine, text
import datetime
import uuid

class SqliteDatabase:
    def __init__(self, uri):
        self.engine = create_engine(f"sqlite:///{uri}")
        self._create_tables()

    def close(self):
        self.engine.dispose()

    def serialize_properties(self, properties):
        """ Serialize the entire properties dictionary to a JSON string before storing in the database. """
        return json.dumps(properties)

    def deserialize_properties(self, properties):
        """ Deserialize the properties JSON string back into a dictionary. """
        return json.loads(properties)

    def _create_tables(self):
        with self.engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS nodes (
                    id TEXT PRIMARY KEY,
                    properties TEXT
                )
            """))

    def add(self, properties, object_type="Node", db_unique_id=None):
        properties_json = self.serialize_properties(properties)
        obj = {"properties": properties_json}
        
        if db_unique_id is None:
            properties["created"] = datetime.datetime.now().strftime("%m.%d.%Y %H:%M:%S")
            obj["id"] = f"{object_type}_{str(uuid.uuid4())}"
            obj["object_type"] = object_type
            obj["properties"] = self.serialize_properties(properties)  # Ensure created field is included

        try:
            with self.engine.begin() as conn:
                self._create_node_sql(conn, obj)
            return obj["id"], self.deserialize_properties(obj["properties"])
        except Exception as e:
            raise Exception(f"Database_Object: Failed to add object to the SQL database. {e}")

    def load(self, id):
        try:
            with self.engine.connect() as conn:
                node = self._get_node_sql(conn, id)
                properties = self.deserialize_properties(node) if node else None
                if properties is None:
                    return None
                properties["id"] = id   
                return properties
        except Exception as e:
            raise Exception(f"Database_Object: Failed to retrieve object from the SQL database. {e}")

    def remove(self, id):
        try:
            with self.engine.begin() as conn:
                self._delete_node_sql(conn, id)
        except Exception as e:
            raise Exception(f"Database_Object: Failed to remove object from the SQL database. {e}")

    def update(self, id, properties):
        # Fetch the existing properties
        existing_properties = self.load(id)
        if not existing_properties:
            raise ValueError(f"Object with id {id} not found.")

        # Merge existing properties with new properties
        updated_properties = {**existing_properties, **properties}
        properties_json = self.serialize_properties(updated_properties)
        try:
            with self.engine.begin() as conn:
                self._update_node_sql(conn, id, properties_json)
        except Exception as e:
            raise Exception(f"Database_Object: Failed to update object in the SQL database. {e}")

    def find(self, object_type):
        try:
            with self.engine.connect() as conn:
                return self._find_nodes_sql(conn, object_type)
        except Exception as e:
            raise Exception(f"Database_Object: Failed to find objects in the SQL database. {e}")

    def _create_node_sql(self, conn, obj):
        query = "INSERT INTO nodes (id, properties) VALUES (:id, :properties)"
        conn.execute(text(query), {"id": obj["id"], "properties": obj["properties"]})

    def _get_node_sql(self, conn, id):
        query = "SELECT properties FROM nodes WHERE id = :id"
        result = conn.execute(text(query), {"id": id}).fetchone()
        return result[0] if result else None

    def _delete_node_sql(self, conn, id):
        query = "DELETE FROM nodes WHERE id = :id"
        conn.execute(text(query), {"id": id})

    def _update_node_sql(self, conn, id, properties):
        query = "UPDATE nodes SET properties = :properties WHERE id = :id"
        conn.execute(text(query), {"id": id, "properties": properties})

    def _find_nodes_sql(self, conn, object_type):
        query = "SELECT id, properties FROM nodes WHERE json_extract(properties, '$.object_type') = :object_type"
        query_params = {"object_type": object_type}

        result = conn.execute(text(query), query_params)
        
        valid_results = []
        for row in result:
            try:
                properties = self.deserialize_properties(row[1])
                valid_results.append({"id": row[0], "properties": properties})
            except json.JSONDecodeError:
                print(f"Skipping malformed JSON for id: {row[0]}")

        return valid_results
