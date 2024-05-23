from models.test import Test

class TestPlan:
    def __init__(self, db, analyst_ids=None, dataset_id=None, 
                 n_hypotheses_per_analyst=0, description=None, id=None, created=None):
        self.db = db
        self.analyst_ids = analyst_ids if analyst_ids is not None else []
        self.dataset_id = dataset_id
        self.n_hypotheses_per_analyst = n_hypotheses_per_analyst
        self.description = description
        self.id = id
        self.created = created

    @classmethod
    def create(cls, db, analyst_ids, dataset_id, n_hypotheses_per_analyst, description=''):
        properties = {
            "analyst_ids": analyst_ids,
            "dataset_id": dataset_id,
            "n_hypotheses_per_analyst": n_hypotheses_per_analyst,
            "description": description
        }
        id, created = db.add(properties, object_type="TestPlan")
        return cls(db, analyst_ids, dataset_id, n_hypotheses_per_analyst, description, id=id, created=created)

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

    def generate_test(self):
            """ Generate a new Test instance based on this test plan. """
            if not self.analyst_ids or not self.dataset_id:
                raise ValueError("TestPlan is not properly configured.")
            return Test.create(
                db=self.db,
                testplan_id=self.id,
                analyst_ids=self.analyst_ids,
                dataset_id=self.dataset_id,
                n_hypotheses_per_analyst=self.n_hypotheses_per_analyst,
                description=self.description
            )