import logging
import datetime

from neo4j import GraphDatabase

class DB_Object:
    def __init__(self, db, db_unique_id=None, persist=False):
        self.db = db
        self.persisted = False
        if db_unique_id is None:
            timestamp = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
            self.db_unique_id = f"{self.__class__.__name__}_{timestamp}"
        else:
            self.db_unique_id = db_unique_id
        if persist:
            self.save()

    def save(self):
        obj = {
            'id': self.db_unique_id,
            'label' : self.db_unique_id,
            'properties': self.to_dict()
        }
        self.persisted = True
        self.db.add(obj)

    def load(self):
        result = self.db.get(self.db_unique_id)
        if result:
            self.from_dict(result['properties'])
        else:
            logging.error(f"DB_Object loading: No object found with unique ID {self.db_unique_id}")

    def to_dict(self):
        """
        Converts instance properties to a dictionary. 
        This method must be implemented by subclasses.
        """
        raise NotImplementedError("DB_Object to_dict: Subclasses must implement this method.")

    def from_dict(self, properties):
        """
        Populates instance properties from a dictionary.
        This method must be implemented by subclasses.
        """
        raise NotImplementedError("DB_Object from_dict: Subclasses must implement this method.")

    def delete(self):
        """
        Removes the instance from the database using its unique ID.
        """
        self.db.remove(self.db_unique_id)
