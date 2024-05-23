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
        return {k: json.loads(v) if self.is_json(v) else v for k, v in properties.items()}

    @staticmethod
    def is_json(value):
        try:
            json.loads(value)
            return True
        except (ValueError, TypeError):
            return False
        
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
        
        if self.db_type == 'neo4j':
            try:
                with self.driver.session() as session:
                    session.write_transaction(self._create_node_neo4j, obj, label)
                return obj["id"], self.deserialize_properties(obj["properties"])
            except Neo4jError as e:
                raise Neo4jError(f"Database_Object: Failed to add object to the Neo4j database. {e}")
        else:
            try:
                with self.engine.begin() as conn:
                    self._create_node_sql(conn, obj)
                return obj["id"], self.deserialize_properties(obj["properties"])
            except Exception as e:
                raise Exception(f"Database_Object: Failed to add object to the SQL database. {e}")

    def load(self, id):
        if self.db_type == 'neo4j':
            try:
                with self.driver.session() as session:
                    node = session.read_transaction(self._get_node_neo4j, id)
                    return self.deserialize_properties(node) if node else None
            except Neo4jError as e:
                raise Neo4jError(f"Database_Object: Failed to retrieve object from the Neo4j database. {e}")
        else:
            try:
                with self.engine.connect() as conn:
                    node = self._get_node_sql(conn, id)
                    if node:
                        properties = self.deserialize_properties(node)
                        properties["id"] = id
                        return properties
                    else:
                        return None 
            except Exception as e:
                raise Exception(f"Database_Object: Failed to retrieve object from the SQL database. {e}")

    def remove(self, id):
        if self.db_type == 'neo4j':
            try:
                with self.driver.session() as session:
                    session.write_transaction(self._delete_node_neo4j, id)
            except Neo4jError as e:
                raise Neo4jError(f"Database_Object: Failed to remove object from the Neo4j database. {e}")
        else:
            try:
                with self.engine.begin() as conn:
                    self._delete_node_sql(conn, id)
            except Exception as e:
                raise Exception(f"Database_Object: Failed to remove object from the SQL database. {e}")

    def update(self, id, new_properties):
        # Serialize the new properties
        new_properties = self.serialize_properties(new_properties)
        
        # Fetch the existing properties
        existing_properties = self.load(id)
        if not existing_properties:
            raise ValueError(f"Object with id {id} not found.")

        # Merge existing properties with new properties
        updated_properties = {**existing_properties, **new_properties}

        if self.db_type == 'neo4j':
            try:
                with self.driver.session() as session:
                    session.write_transaction(self._update_node_neo4j, id, updated_properties)
            except Neo4jError as e:
                raise Neo4jError(f"Database_Object: Failed to update object in the Neo4j database. {e}")
        else:
            try:
                with self.engine.begin() as conn:
                    self._update_node_sql(conn, id, updated_properties)
            except Exception as e:
                raise Exception(f"Database_Object: Failed to update object in the SQL database. {e}")

    def find(self, object_type):
        if self.db_type == 'neo4j':
            try:
                with self.driver.session() as session:
                    return session.read_transaction(self._find_nodes_neo4j, object_type)
            except Neo4jError as e:
                raise Neo4jError(f"Database_Object: Failed to find objects in the Neo4j database. {e}")
        else:
            try:
                with self.engine.connect() as conn:
                    return self._find_nodes_sql(conn, object_type)
            except Exception as e:
                raise Exception(f"Database_Object: Failed to find objects in the SQL database. {e}")


    # def find(self, object_type, filters):
    #     if self.db_type == 'neo4j':
    #         try:
    #             with self.driver.session() as session:
    #                 return session.read_transaction(self._find_nodes_neo4j, object_type, filters)
    #         except Neo4jError as e:
    #             raise Neo4jError(f"Database_Object: Failed to find objects in the Neo4j database. {e}")
    #     else:
    #         try:
    #             with self.engine.connect() as conn:
    #                 return self._find_nodes_sql(conn, object_type, filters)
    #         except Exception as e:
    #             raise Exception(f"Database_Object: Failed to find objects in the SQL database. {e}")

    @staticmethod
    def _find_nodes_neo4j(tx, object_type, filters):
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


    # def _find_nodes_sql(self, conn, object_type, filters):
    #     query = f"SELECT id, properties FROM nodes WHERE json_extract(properties, '$.object_type') = :object_type"
    #     query_params = {"object_type": object_type}
        
    #     for key, value in filters.items():
    #         query += f" AND json_extract(properties, '$.{key}') = :{key}"
    #         query_params[key] = value
        
    #     result = conn.execute(text(query), **query_params)
    #     return [
    #         {"id": row[0], "properties": self.deserialize_properties(eval(row[1]))}
    #         for row in result
    #     ]

    def _find_nodes_sql(self, conn, object_type):
        query = "SELECT id, properties FROM nodes WHERE json_extract(properties, '$.object_type') = :object_type"
        query_params = {"object_type": object_type}

        result = conn.execute(text(query), query_params)
        
        valid_results = []
        for row in result:
            try:
                properties = self.deserialize_properties(row["properties"])
                valid_results.append({"id": row["id"], "properties": properties})
            except json.JSONDecodeError:
                print(f"Skipping malformed JSON for id: {row['id']}")

        return valid_results

    # def _find_nodes_sql(self, conn, object_type):
    #     query = "SELECT id, properties FROM nodes WHERE json_extract(properties, '$.object_type') = :object_type"
    #     query_params = {"object_type": object_type}

    #     result = conn.execute(text(query), query_params)
        
    #     return [
    #         {"id": row["id"], "properties": self.deserialize_properties(row["properties"])}
    #         for row in result
    #     ]

    @staticmethod
    def _create_node_neo4j(tx, obj, label):
        query = f"CREATE (n:{label} {{id: $id}}) SET n += $properties RETURN n"
        tx.run(query, id=obj["id"], properties=obj["properties"])

    def _create_node_sql(self, conn, obj):
        query = "INSERT INTO nodes (id, properties) VALUES (:id, :properties)"
        conn.execute(text(query), {"id": obj["id"], "properties": json.dumps(obj["properties"])})

    @staticmethod
    def _get_node_neo4j(tx, id):
        query = "MATCH (n {id: $id}) RETURN properties(n) AS properties"
        result = tx.run(query, id=id)
        record = result.single()
        return record['properties'] if record else None

    def _get_node_sql(self, conn, id):
        query = "SELECT properties FROM nodes WHERE id = :id"
        result = conn.execute(text(query), {"id": id}).fetchone()
        return json.loads(result[0]) if result else None

    @staticmethod
    def _delete_node_neo4j(tx, id):
        query = "MATCH (n {id: $id}) DELETE n"
        tx.run(query, {"id": id})

    def _delete_node_sql(self, conn, id):
        query = "DELETE FROM nodes WHERE id = :id"
        conn.execute(text(query), {"id": id})

    @staticmethod
    def _update_node_neo4j(tx, id, properties):
        query = "MATCH (n {id: $id}) SET n += $properties RETURN n"
        return tx.run(query, {"id": id, "properties": properties})

    def _update_node_sql(self, conn, id, properties):
        query = "UPDATE nodes SET properties = :properties WHERE id = :id"
        conn.execute(text(query), {"id": id, "properties": json.dumps(properties)})

    @staticmethod
    def _execute_query_neo4j(tx, query):
        result = tx.run(query)
        return [record[0] for record in result]

    def _execute_query_sql(self, conn, query):
        result = conn.execute(text(query))
        return result.fetchall()