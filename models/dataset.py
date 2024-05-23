class Dataset:
    def __init__(self, db, name=None, data=None, experiment_description=None, description=None, id=None, created=None):
        self.db = db
        self.name = name
        self.data = data
        self.experiment_description = experiment_description
        self.description = description
        self.id = id
        self.created = created

    @classmethod
    def create(cls, db, name, data, experiment_description, description=""):
        properties = {
            "name": name,
            "data": data,
            "experiment_description": experiment_description,
            "description": description
        }
        id, created = db.add(properties, object_type="Dataset")
        return cls(db, name, data, experiment_description, description, id=id, created=created)

    @classmethod
    def load(cls, db, id):
        data = db.load(id)
        if data:
            return cls(db, **data)
        return None

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.db.update(self.id, kwargs)

    def delete(self):
        self.db.remove(self.id)

