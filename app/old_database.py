import json
from neo4j.exceptions import Neo4jError, ServiceUnavailable
from neo4j import GraphDatabase
from sqlalchemy import create_engine, text
import datetime
import uuid

class Database:
    def __init__(self, uri, db_type=None, user=None, password=None):
        self.db_type = db_type
        if db_type == 'neo4j':
            try:
                self.driver = GraphDatabase.driver(uri, auth=(user, password))
            except ServiceUnavailable as e:
                raise ServiceUnavailable("Database_Object: Neo4j database connection could not be established.") from e
        elif db_type == 'sqlite':
            self.engine = create_engine(f"sqlite:///{uri}")
        elif db_type in ['postgresql', 'mysql']:
            self.engine = create_engine(uri)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        if db_type != 'neo4j':
            self._create_tables()

    def close(self):
        if self.db_type == 'neo4j':
            self.driver.close()
        else:
            self.engine.dispose()

    def serialize_properties(self, properties):
        """ Serialize dictionaries and lists to JSON strings before storing in the database. """
        return {k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in properties.items()}

    def deserialize_properties(self, properties):
        """ Deserialize properties that are stored as JSON strings back to dictionaries or lists. """
        return {k: json.loads(v) if (isinstance(v, str) and (v.startswith('{') or v.startswith('['))) else v for k, v in properties.items()}

    def _create_tables(self):
        with self.engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS nodes (
                    id TEXT PRIMARY KEY,
                    properties TEXT
                )
            """))

            
    def add(self, properties, label="Node", db_unique_id=None):
        properties = self.serialize_properties(properties)
        obj = {"properties": properties}
        if db_unique_id is None:
            properties["created"] = datetime.datetime.now().strftime("%m.%d.%Y %H:%M:%S")
            obj["id"] = f"{label}_{str(uuid.uuid4())}"
            obj["label"] = label
        try:
            with self.driver.session() as session:
                session.write_transaction(self._create_node, obj, label)
            return obj["id"], self.deserialize_properties(obj["properties"])
        except Neo4jError as e:
            raise Neo4jError(f"Database_Object: Failed to add object to the database. {e}")

    def load(self, id):
        try:
            with self.driver.session() as session:
                node = session.read_transaction(self._get_node, id)
                return self.deserialize_properties(node) if node else None
        except Neo4jError as e:
            raise Neo4jError(f"Database_Object: Failed to retrieve object from the database. {e}")

    def remove(self, id):
        try:
            with self.driver.session() as session:
                session.write_transaction(self._delete_node, id)
        except Neo4jError as e:
            raise Neo4jError("Database_Object: Failed to remove object from the database.")

    def update(self, id, properties):
        properties = self.serialize_properties(properties)
        try:
            with self.driver.session() as session:
                session.write_transaction(self._update_node, id, properties)
        except Neo4jError as e:
            raise Neo4jError(f"Database_Object: Failed to update object in the database. {e}")


    def find(self, object_type, filters):
        try:
            with self.driver.session() as session:
                return session.read_transaction(self._find_nodes, object_type, filters)
        except Neo4jError as e:
            raise Neo4jError(f"Database_Object: Failed to find objects in the database. {e}")

    @staticmethod
    def _find_nodes(tx, object_type, filters):
        query = f"MATCH (n:{object_type}) WHERE "
        query_filters = []
        query_params = {}
        
        for key, value in filters.items():
            query_filters.append(f"n.{key} = ${key}")
            query_params[key] = value
        
        if query_filters:
            query += " AND ".join(query_filters)
        else:
            query = query.rstrip(" WHERE ")
        
        query += " RETURN n.id as id, n.created as created, n as properties"
        
        result = tx.run(query, **query_params)
        return [
            {"id": record["id"], "created": record["created"], "properties": record["properties"]}
            for record in result
        ]


    @staticmethod
    def _create_node(tx, obj, label):
        query = f"CREATE (n:{label} {{id: $id}}) SET n += $properties RETURN n"
        tx.run(query, id=obj["id"], properties=obj["properties"])

    @staticmethod
    def _get_node(tx, id):
        query = "MATCH (n {id: $id}) RETURN properties(n) AS properties"
        result = tx.run(query, id=id)
        record = result.single()
        return record['properties'] if record else None

    @staticmethod
    def _delete_node(tx, id):
        query = "MATCH (n {id: $id}) DELETE n"
        tx.run(query, id=id)

    @staticmethod
    def _update_node(tx, id, properties):
        query = "MATCH (n {id: $id}) SET n += $properties RETURN n"
        return tx.run(query, id=id, properties=properties)

    @staticmethod
    def _execute_query(tx, query):
        result = tx.run(query)
        return [record[0] for record in result]
