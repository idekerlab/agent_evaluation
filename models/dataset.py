class Dataset:
    def __init__(self, db, 
                 name=None, data=None, 
                 experiment_description=None, 
                 description=None, object_id=None, created=None):
        self.db = db
        self.name = name
        self.data = data
        self.experiment_description = experiment_description
        self.description = description
        self.object_id = object_id
        self.created = created

    @classmethod
    def create(cls, db, name, data, experiment_description, description=""):
        properties = {
            "name": name,
            "data": data,
            "experiment_description": experiment_description,
            "description": description
        }
        object_id, created, _ = db.add(object_id=None, properties=properties, object_type="dataset")
        return cls(db, name, data, experiment_description, description, 
                   object_id=object_id, created=created)

    @classmethod
    def load(cls, db, object_id):
        properties, _ = db.load(object_id)
        if properties:
            return cls(db, **properties)
        return None

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.db.update(self.object_id, kwargs)

    def delete(self):
        self.db.remove(self.object_id)

