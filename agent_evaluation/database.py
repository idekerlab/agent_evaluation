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
            raise ServiceUnavailable("Database connection could not be established.") from e

    def close(self):
        """
        Closes the connection to the database.
        """
        self.driver.close()

    def add(self, obj):
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
                session.write_transaction(self._create_node, obj)
        except Neo4jError as e:
            raise Neo4jError(f"Failed to add object to the database. {e}") from e

    def get(self, id):
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
            raise Neo4jError(f"Failed to retrieve object from the database. {e}") from e

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
            raise Neo4jError("Failed to remove object from the database.") from e

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
            raise Neo4jError("Query execution failed.") from e

    # Example of a private method; not included in the Sphinx documentation
    @staticmethod
    def _create_node(tx, obj):
        # query = """
        # CREATE (n:Node {id: $id})
        # SET n += $properties
        # RETURN n
        # """
        query = f"CREATE (n:{obj['label']} {{id: $id}}) SET n += $properties RETURN n"

        # Assuming 'obj' contains an 'id' and a 'properties' dictionary
        tx.run(query, id=obj["id"], properties=obj["properties"])

    # def _create_node(tx, obj):
    # # Assuming 'obj' has an 'id' and other properties to be added to the node
    # # and 'properties' is a dictionary of these properties.
    #     query = "CREATE (n:Node {id: $id, properties})"
    #     parameters = {"id": obj["id"]}
    #     parameters.update(obj["properties"])  # Flattens the properties dictionary into the parameters
    #     print(parameters)
    #     print("------")
    #     tx.run(query, parameters)
    #def _create_node(tx, obj):
    #    query = "CREATE (n:Node {id: $id, properties: $properties}) RETURN n"
    #    tx.run(query, id=obj['id'], properties=obj.get('properties', {}))

    @staticmethod
    def _get_node(tx, id):
        query = "MATCH (n:Node {id: $id}) RETURN n"
        result = tx.run(query, id=id)
        return result.single()[0] if result.single() else None

    @staticmethod
    def _delete_node(tx, id):
        query = "MATCH (n:Node {id: $id}) DELETE n"
        tx.run(query, id=id)

    @staticmethod
    def _execute_query(tx, query):
        result = tx.run(query)
        return [record[0] for record in result]
