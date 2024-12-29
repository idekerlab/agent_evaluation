from datetime import datetime
import uuid

class Json:
    """
    A model class for storing and displaying JSON data in a hierarchical format.
    """
    def __init__(self, name=None, json_data=None):
        self.object_id = str(uuid.uuid4())
        self.name = name or "Unnamed JSON"
        self.created = datetime.now().isoformat()
        self.json = json_data or {}

    def to_dict(self):
        """
        Convert the object to a dictionary for serialization.
        """
        return {
            "object_id": self.object_id,
            "name": self.name,
            "created": self.created,
            "json": self.json
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create an instance from a dictionary.
        """
        instance = cls()
        instance.object_id = data.get("object_id")
        instance.name = data.get("name")
        instance.created = data.get("created")
        instance.json = data.get("json", {})
        return instance 