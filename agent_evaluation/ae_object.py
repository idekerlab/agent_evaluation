from neo4j.exceptions import Neo4jError
class AE_Object:
    """
    A superclass for handling generic persistence to a Neo4j database.
    
    :param db: The database object for persistence operations.
    :type db: Database
    """
    def __init__(self, db):
        self.db = db
    
    def save(self):
        """
        Persists the current state of the instance to the database.
        """
        obj = {
            'id': self.name,
            'label': self.__class__.__name__,  # Dynamically get the class name
            'properties': self.to_dict()
        }
        try:
            self.db.add(obj)
        except Neo4jError as e:
            raise RuntimeError(f"Failed to persist object to the database. {e}")
    
    def load(self):
        """
        Loads the instance's state from the database.
        """
        try:
            result = self.db.get(self.name)
            if result is None:
                raise ValueError(f"No entry found for {self.name}")
            self.from_dict(result['properties'])
        except Neo4jError as e:
            raise RuntimeError(f"Failed to load object from the database. {e}")
    
    def to_dict(self):
        """
        Converts instance properties to a dictionary.
        
        :returns: A dictionary representation of the instance.
        :rtype: dict
        """
        return {}
    
    def from_dict(self, properties):
        """
        Sets instance properties from a dictionary.
        
        :param properties: A dictionary of properties to set on the instance.
        :type properties: dict
        """
        pass
