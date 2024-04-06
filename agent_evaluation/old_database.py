from neo4j import GraphDatabase

"""
This database.py module is used by the agent_evaluation framework to persist the objects created 
by the researchers performing evaluations and the objects created by the system in the course of 
importing datasets and generating hypotheses and reviews. It is queried to create reports. 
It serves as the back end for interfaces implemented in other modules, which are used by humans 
to perform various tasks such as creating and editing objects (e.g., Reviewer, Analyst, TestPlan, ReviewPlan), 
running TestPlan and ReviewPlan objects, finding and displaying objects (especially Hypotheses in specific 
Tests and Comparisons in specific reviews), and enabling humans to act as reviewers or analysts.

"""

class Database: # pylint: disable=too-few-public-methods
    class Database:
        """
        This class is used to persist objects created by the researchers performing evaluations and the objects created by the system in the course of importing datasets and generating hypotheses and reviews. It is queried to create reports. It serves as the back end for interfaces implemented in other modules, which are used by humans to perform various tasks such as creating and editing objects (e.g., Reviewer, Analyst, TestPlan, ReviewPlan), running TestPlan and ReviewPlan objects, finding and displaying objects (especially Hypotheses in specific Tests and Comparisons in specific reviews), and enabling humans to act as reviewers or analysts.
        """
        def __init__(self, uri, user, password):
            """
            This method initializes the Database class with the Neo4j database backend.
            """
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
        def close(self):
            """
            This method closes the connection to the database.
            """
            self.driver.close()
        def add(self, obj):
            """
            This method adds an object to the database.
            """
            with self.driver.session() as session:
                session.write_transaction(self._create_node, obj)
        def get(self, id):
            """
            This method retrieves an object from the database.
            """
            with self.driver.session() as session:
                return session.read_transaction(self._get_node, id)
        def remove(self, id):
            """
            This method removes an object from the database.
            """
            with self.driver.session() as session:
                session.write_transaction(self._delete_node, id)
        def query(self, query):
            """
            This method queries the database.
            """
            with self.driver.session() as session:
                return session.read_transaction(self._execute_query, query)
        def __str__(self):
            """
            This method returns a string representation of the database.
            """
            return str(self.objects)
        @staticmethod
        def _create_node(tx, obj):
            """
            This method creates a node in the database.
            """
            # Neo4j create node query
            query = "CREATE (n:Node {id: $id, properties: $properties}) RETURN n"
            tx.run(query, id=obj.id, properties=obj.properties)
        @staticmethod
        def _get_node(tx, id):
            """
            This method retrieves a node from the database.
            """
            # Neo4j get node query
            query = "MATCH (n:Node {id: $id}) RETURN n"
            result = tx.run(query, id=id)
            return result.single()[0]
        @staticmethod
        def _delete_node(tx, id):
            """
            This method deletes a node from the database.
            """
            # Neo4j delete node query
            query = "MATCH (n:Node {id: $id}) DELETE n"
            tx.run(query, id=id)
        @staticmethod
        def _execute_query(tx, query):
            """
            This method executes a query on the database.
            """
            # Neo4j custom query
            result = tx.run(query)
            return [record[0] for record in result]
        def search(self, name, type="exact"):
            """
            This method searches for objects in the database by name.
            By default, it performs an exact match search.
            The optional argument "type" can be set to "exact" for exact match search or "contains" for partial match search.
            """
            with self.driver.session() as session:
                if type == "exact":
                    query = "MATCH (n:Node {name: $name}) RETURN n"
                elif type == "contains":
                    query = "MATCH (n:Node) WHERE n.name CONTAINS $name RETURN n"
                else:
                    raise ValueError("Invalid search type. Must be 'exact' or 'contains'.")
                result = session.run(query, name=name)
                return [record[0] for record in result]
        def search_by_type_and_date(self, obj_type, from_date="any", to_date="now", time_range="all", time_units="days", max_results=1):
            """
            This method searches for objects in the database by type and date.
            It allows filtering by a range of dates specified by "from_date" and "to_date".
            The "from_date" defaults to "any" and the "to_date" defaults to "now".
            The "time_range" parameter specifies the range of time to consider, with "all" being the default.
            The "time_units" parameter specifies the units of the time range, with "days" being the default.
            The "max_results" parameter specifies the maximum number of results to return, with 1 being the default.
            The results are ordered by the most recent first.
            """
            with self.driver.session() as session:
                if from_date == "any":
                    from_date_query = ""
                else:
                    from_date_query = f"AND n.date >= datetime({{epochMillis: datetime({from_date}).timestamp() * 1000}})"
                if to_date == "now":
                    to_date_query = ""
                else:
                    to_date_query = f"AND n.date <= datetime({{epochMillis: datetime({to_date}).timestamp() * 1000}})"
                if time_range == "all":
                    time_range_query = ""
                else:
                    if time_units == "days":
                        time_range_query = f"AND duration.between(n.date, datetime({{epochMillis: datetime('now').timestamp() * 1000}})).days <= {time_range}"
                    elif time_units == "hours":
                        time_range_query = f"AND duration.between(n.date, datetime({{epochMillis: datetime('now').timestamp() * 1000}})).hours <= {time_range}"
                    elif time_units == "minutes":
                        time_range_query = f"AND duration.between(n.date, datetime({{epochMillis: datetime('now').timestamp() * 1000}})).minutes <= {time_range}"
                    elif time_units == "seconds":
                        time_range_query = f"AND duration.between(n.date, datetime({{epochMillis: datetime('now').timestamp() * 1000}})).seconds <= {time_range}"
                    else:
                        raise ValueError("Invalid time units. Must be 'days', 'hours', 'minutes', or 'seconds'.")
                query = f"MATCH (n:Node {{type: $type}}) WHERE 1=1 {from_date_query} {to_date_query} {time_range_query} RETURN n ORDER BY n.date DESC LIMIT {max_results}"
                result = session.run(query, type=obj_type)
                return [record[0] for record in result]
                
                