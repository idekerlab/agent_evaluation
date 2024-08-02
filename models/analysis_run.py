
class AnalysisRun:
    def __init__(self, db, analysis_plan_id, analyst_ids=None, dataset_id=None, 
                 n_hypotheses_per_analyst=0, hypothesis_ids=None, biological_context=None,
                 description=None, run_log=None, attempts=None, status='pending', 
                 object_id=None, created=None, name=None, user_ids=None):
        self.db = db
        self.analysis_plan_id = analysis_plan_id
        self.analyst_ids = analyst_ids if analyst_ids else []
        self.dataset_id = dataset_id
        self.n_hypotheses_per_analyst = n_hypotheses_per_analyst
        self.hypothesis_ids = hypothesis_ids if hypothesis_ids else []
        self.biological_context = biological_context
        self.description = description
        self.run_log = run_log
        self.attempts = attempts if attempts is not None else {analyst: [] for analyst in analyst_ids}
        self.status = status
        self.object_id = object_id
        self.name = name if name else "none"
        self.user_ids = user_ids if user_ids else []
        self.created = created

    @classmethod
    def create(cls, db, analysis_plan_id, analyst_ids, dataset_id, 
               n_hypotheses_per_analyst, biological_context, description, name):
        properties = {
            "analysis_plan_id": analysis_plan_id,
            "analyst_ids": analyst_ids,
            "dataset_id": dataset_id,
            "n_hypotheses_per_analyst": n_hypotheses_per_analyst,
            "hypothesis_ids": [],
            "biological_context": biological_context, 
            "description": description,
            "attempts": {analyst: [] for analyst in analyst_ids},
            "name": name,
            "user_ids": [],
            "status": "pending"
        }
        object_id, created, _ = db.add(object_id=None, properties=properties, object_type="analysis_run")
        return cls(db, analysis_plan_id, analyst_ids, dataset_id, n_hypotheses_per_analyst, [],
                   biological_context, description, "", properties['attempts'], 'pending', object_id, name, [], created)

    @classmethod
    def load(cls, db, object_id):
        properties, _ = db.load(object_id)
        if properties:
            return cls(db, **properties)
        return None

    def update(self):
        properties = {
            "hypothesis_ids": self.hypothesis_ids,
            "attempts": self.attempts,
            "status": self.status,
            "run_log": self.run_log
        }
        self.db.update(self.object_id, properties)

    def update_properties(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.db.update(self.object_id, kwargs)

    def delete(self):
        self.db.remove(self.object_id)

    def add_hypothesis(self, hypothesis_id, analyst_id):
        if self.status == 'done':
            return "AnalysisRun is already completed."
        
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
            
    def update_run_log(self, run_log):
        self.run_log = run_log
        self.update()
