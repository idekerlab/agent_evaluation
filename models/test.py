
class Test:
    def __init__(self, db, analyst_ids=None, dataset_id=None, n_hypotheses_per_analyst=0, hypothesis_ids=None, description=None, id=None, created=None):
        self.db = db
        self.analyst_ids = analyst_ids if analyst_ids else []
        self.dataset_id = dataset_id
        self.n_hypotheses_per_analyst = n_hypotheses_per_analyst
        self.hypothesis_ids = hypothesis_ids if hypothesis_ids else []
        self.description = description
        self.id = id
        self.created = created

    @classmethod
    def create(cls, db, analyst_ids, dataset_id, n_hypotheses_per_analyst, hypothesis_ids, description):
        properties = {
            "analyst_ids": analyst_ids,
            "dataset_id": dataset_id,
            "n_hypotheses_per_analyst": n_hypotheses_per_analyst,
            "hypothesis_ids": hypothesis_ids,
            "description": description
        }
        id, created = db.add(properties, label="Test")
        return cls(db, analyst_ids, dataset_id, n_hypotheses_per_analyst, hypothesis_ids, description, id=id, created=created)

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
