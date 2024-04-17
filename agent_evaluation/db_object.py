import logging
from neo4j import GraphDatabase

class DB_Object:
    def __init__(self, db, db_unique_id, persist=False):
        self.db = db
        self.db_unique_id = db_unique_id
        if persist:
            self.save()

    def save(self):
        obj = {
            'id': self.db_unique_id,
            'properties': self.to_dict()
        }
        self.db.add(obj)

    def load(self):
        result = self.db.get(self.db_unique_id)
        if result:
            self.from_dict(result['properties'])
        else:
            logging.error(f"No object found with unique ID {self.db_unique_id}")

    def to_dict(self):
        """
        Converts instance properties to a dictionary. 
        This method must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def from_dict(self, properties):
        """
        Populates instance properties from a dictionary.
        This method must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def delete(self):
        """
        Removes the instance from the database using its unique ID.
        """
        self.db.remove(self.db_unique_id)
