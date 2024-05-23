
class Test:
    def __init__(self, db, testplan_id, analyst_ids=None, dataset_id=None, n_hypotheses_per_analyst=0, hypothesis_ids=None, description=None, attempts=None, status='pending', id=None, created=None):
        self.db = db
        self.testplan_id = testplan_id
        self.analyst_ids = analyst_ids if analyst_ids else []
        self.dataset_id = dataset_id
        self.n_hypotheses_per_analyst = n_hypotheses_per_analyst
        self.hypothesis_ids = hypothesis_ids if hypothesis_ids else []
        self.description = description
        self.attempts = attempts if attempts is not None else {analyst: [] for analyst in analyst_ids}
        self.status = status
        self.id = id
        self.created = created

    @classmethod
    def create(cls, db, testplan_id, analyst_ids, dataset_id, n_hypotheses_per_analyst, description):
        properties = {
            "testplan_id": testplan_id,
            "analyst_ids": analyst_ids,
            "dataset_id": dataset_id,
            "n_hypotheses_per_analyst": n_hypotheses_per_analyst,
            "hypothesis_ids": [],
            "description": description,
            "attempts": {analyst: [] for analyst in analyst_ids},
            "status": "pending"
        }
        id, created = db.add(properties, object_type="Test")
        return cls(db, testplan_id, analyst_ids, dataset_id, n_hypotheses_per_analyst, [], description, properties['attempts'], 'pending', id, created)

    @classmethod
    def load(cls, db, id):
        data = db.load(id)
        if data:
            return cls(db, **data)
        return None

    def update(self):
        properties = {
            "hypothesis_ids": self.hypothesis_ids,
            "attempts": self.attempts,
            "status": self.status
        }
        self.db.update(self.id, properties)

    def delete(self):
        self.db.remove(self.id)

    def add_hypothesis(self, hypothesis_id, analyst_id):
        if self.status == 'done':
            return "Test is already completed."
        
        self.hypothesis_ids.append(hypothesis_id)
        self.attempts[analyst_id].append('success')  # Assuming hypothesis generation was successful
        self.update_status()
        self.update()
        return "Hypothesis added successfully."

    def update_status(self):
        total_attempts = sum(len(attempts) for attempts in self.attempts.values())
        required_attempts = len(self.analyst_ids) * self.n_hypotheses_per_analyst
        if total_attempts >= required_attempts:
            self.status = 'done'
        else:
            self.status = 'in_progress'


# class Test:
#     def __init__(self, db, analyst_ids=None, dataset_id=None, n_hypotheses_per_analyst=0, hypothesis_ids=None, description=None, id=None, created=None):
#         self.db = db
#         self.analyst_ids = analyst_ids if analyst_ids else []
#         self.dataset_id = dataset_id
#         self.n_hypotheses_per_analyst = n_hypotheses_per_analyst
#         self.hypothesis_ids = hypothesis_ids if hypothesis_ids else []
#         self.description = description
#         self.id = id
#         self.created = created

#     @classmethod
#     def create(cls, db, analyst_ids, dataset_id, n_hypotheses_per_analyst, hypothesis_ids, description):
#         properties = {
#             "analyst_ids": analyst_ids,
#             "dataset_id": dataset_id,
#             "n_hypotheses_per_analyst": n_hypotheses_per_analyst,
#             "hypothesis_ids": hypothesis_ids,
#             "description": description
#         }
#         id, created = db.add(properties, label="Test")
#         return cls(db, analyst_ids, dataset_id, n_hypotheses_per_analyst, hypothesis_ids, description, id=id, created=created)

#     @classmethod
#     def load(cls, db, id):
#         data = db.load(id)
#         if data:
#             return cls(db, **data)
#         return None

#     def update(self, **kwargs):
#         for key, value in kwargs.items():
#             setattr(self, key, value)
#         self.db.update(self.id, kwargs)

#     def delete(self):
#         self.db.remove(self.id)
