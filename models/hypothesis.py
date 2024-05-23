 

class Hypothesis:
    def __init__(self, db, data=None, hypothesis_text=None, analyst_id=None, dataset_id=None, description=None, test_id=None, id=None, created=None):
        self.db = db
        self.data = data
        self.hypothesis_text = hypothesis_text
        self.analyst_id = analyst_id
        self.dataset_id = dataset_id
        self.description = description
        self.test_id = test_id
        self.id = id
        self.created = created

    @classmethod
    def create(cls, db, data, hypothesis_text, analyst_id, dataset_id, description, test_id):
        properties = {
            "data": data,
            "hypothesis_text": hypothesis_text,
            "analyst_id": analyst_id,
            "dataset_id": dataset_id,
            "description": description,
            "test_id": test_id
        }
        id, created = db.add(properties, object_type="Hypothesis")
        return cls(db, data, hypothesis_text, analyst_id, dataset_id, description, test_id, id=id, created=created)

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
