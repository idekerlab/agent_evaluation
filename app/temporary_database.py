import datetime
import uuid

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

    def add(self, properties, label="Node", db_unique_id=None):
        """
        Adds an object to the database

        :param obj: The object to be added, expected to be a dictionary with at least an 'id'.
        :type obj: dict

        """
        obj = {"properties": properties}
        if db_unique_id is None:
            properties["created"] = datetime.datetime.now().strftime("%m.%d.%Y %H:%M:%S")
            obj["id"] = f"{label}_{str(uuid.uuid4())}"
            obj["label"] = label
        if 'properties' not in obj:
            raise ValueError("Object must include a 'properties' key.")
        self.database[obj['id']] = obj
        return obj['id']

    def load(self, id):
        """
        Retrieves an object from the database by its ID.

        :param id: The ID of the object to retrieve.
        :type id: str
        :returns: The requested object if found, otherwise `None`.
        """
        if id in self.database:
            return self.database[id]
        else:
            return None

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
