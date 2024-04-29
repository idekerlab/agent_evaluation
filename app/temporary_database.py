class TemporaryDatabase:
    """
    Provides methods to interact with a temporary in-memory dictionary database.
    """
    
    def __init__(self):
        """
        Initializes the database as an empty dictionary.
        """
        self.database = {}

    def close(self):
        """
        Closes the connection to the database.
        """
        self.database = {}

    def add(self, obj, label="Node"):
        """
        Adds an object to the database

        :param obj: The object to be added, expected to be a dictionary with at least an 'id'.
        :type obj: dict

        """
        if 'id' not in obj:
            raise ValueError("Object must include an 'id' key.")
        if 'properties' not in obj:
            raise ValueError("Object must include a 'properties' key.")
        self.database[obj['id']] = obj

    def load(self, id):
        """
        Retrieves an object from the database by its ID.

        :param id: The ID of the object to retrieve.
        :type id: str
        :returns: The requested object if found, otherwise `None`.
        """
        return self.database.get(id)
    
    def load_all(self, label):
        """
        Retrieves all objects with a given label from the database.

        :param label: The label to filter by.
        :type label: str
        :returns: A list of objects with the specified label.
        """
        return [obj for obj in self.database.values() if obj.get('label') == label] 
    

    def remove(self, id):
        """
        Removes an object from the database by its ID.

        :param id: The ID of the object to remove.
        :type id: str
        """
        self.database.pop(id, None)

    def insert_test_data(self):
        # Insert test data into the temporary database
        db.add

