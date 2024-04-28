from neo4j.exceptions import Neo4jError, ServiceUnavailable 
from neo4j import GraphDatabase

class Database:
    """
    Provides methods to interact with a Neo4j database, enabling the addition, retrieval,
    deletion, and querying of nodes. This class is designed to support a range of database
    operations needed for managing research data, including complex queries for data analysis.

    :param uri: The URI for connecting to the Neo4j database.
    :type uri: str
    :param user: Username for database authentication.
    :type user: str
    :param password: Password for database authentication.
    :type password: str
    """
    
    def __init__(self, uri, user, password):
        """
        Initializes the database connection using provided credentials.

        :raises ServiceUnavailable: If the database connection cannot be established.
        """
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
        except ServiceUnavailable as e:
            raise ServiceUnavailable("Database_Object: Database connection could not be established.") from e

    def close(self):
        """
        Closes the connection to the database.
        """
        self.driver.close()

    def add(self, obj, label="Node"):
        """
        Adds an object to the database as a new node.

        :param obj: The object to be added, expected to be a dictionary with at least an 'id'.
        :type obj: dict
        :raises Neo4jError: If the node cannot be created.
        """
        if 'id' not in obj:
            raise ValueError("Object must include an 'id' key.")
        if 'properties' not in obj:
            raise ValueError("Object must include a 'properties' key.")
        try:
            with self.driver.session() as session:
                session.write_transaction(self._create_node, obj, label)
        except Neo4jError as e:
            raise Neo4jError(f"Database_Object: Failed to add object to the database. {e}") from e

    def load(self, id):
        """
        Retrieves an object from the database by its ID.

        :param id: The ID of the object to retrieve.
        :type id: str
        :returns: The requested node if found, otherwise `None`.
        :rtype: Optional[dict]
        :raises Neo4jError: If the query fails.
        """
        try:
            with self.driver.session() as session:
                return session.read_transaction(self._get_node, id)
        except Neo4jError as e:
            raise Neo4jError(f"Database_Object: Failed to retrieve object from the database. {e}") from e

    def remove(self, id):
        """
        Removes an object from the database by its ID.

        :param id: The ID of the object to remove.
        :type id: str
        :raises Neo4jError: If the deletion fails.
        """
        try:
            with self.driver.session() as session:
                session.write_transaction(self._delete_node, id)
        except Neo4jError as e:
            raise Neo4jError("Database_Object: Failed to remove object from the database.") from e

    def query(self, query):
        """
        Executes a custom query on the database.

        :param query: The query string to execute.
        :type query: str
        :returns: The result of the query.
        :rtype: list
        :raises Neo4jError: If the query execution fails.
        """
        try:
            with self.driver.session() as session:
                return session.read_transaction(self._execute_query, query)
        except Neo4jError as e:
            raise Neo4jError("Database_Object: Query execution failed.") from e

    # Create a node in the database based on the provided object and label,
    # where the object is a dictionary expected to have an 'id' and 'properties' dictionary.
    @staticmethod
    def _create_node(tx, obj, label):
        query = f"CREATE (n:{label} {{id: $id}}) SET n += $properties RETURN n"
        tx.run(query, id=obj["id"], properties=obj["properties"])

    # Retrieve a node from the database by its ID, does not require a label.
    @staticmethod
    def _get_node(tx, id):
        query = "MATCH (n {id: $id}) RETURN n"
        result = tx.run(query, id=id)
        node = result.single()
        if node is not None:
            return node[0]
        return None 

    # Delete a node from the database by its ID.
    @staticmethod
    def _delete_node(tx, id):
        query = "MATCH (n {id: $id}) DELETE n"
        tx.run(query, id=id)

    @staticmethod
    def _execute_query(tx, query):
        result = tx.run(query)
        return [record[0] for record in result] # Extracting the first column from the result as a list
