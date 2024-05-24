from models.analysis_run import AnalysisRun

class AnalysisPlan:
    def __init__(self, db, analyst_ids=None, dataset_id=None, 
                 n_hypotheses_per_analyst=0, description=None, 
                 object_id=None, created=None):
        self.db = db
        self.analyst_ids = analyst_ids if analyst_ids is not None else []
        self.dataset_id = dataset_id
        self.n_hypotheses_per_analyst = n_hypotheses_per_analyst
        self.description = description
        self.object_id = object_id
        self.created = created

    @classmethod
    def create(cls, db, analyst_ids, dataset_id, n_hypotheses_per_analyst, description=''):
        properties = {
            "analyst_ids": analyst_ids,
            "dataset_id": dataset_id,
            "n_hypotheses_per_analyst": n_hypotheses_per_analyst,
            "description": description
        }
        object_id, created, _ = db.add(object_id=None, properties=properties, object_type="analysis_plan")
        return cls(db, analyst_ids, dataset_id, n_hypotheses_per_analyst, 
                   description, object_id=object_id, created=created)

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

    def generate_analysis_run(self):
            """ Generate a new AnalysisRun instance based on this AnalysisPlan. """
            if not self.analyst_ids or not self.dataset_id:
                raise ValueError("AnalysisPlan is not properly configured.")
            return AnalysisRun.create(
                db=self.db,
                analysis_plan_id=self.object_id,
                analyst_ids=self.analyst_ids,
                dataset_id=self.dataset_id,
                n_hypotheses_per_analyst=self.n_hypotheses_per_analyst,
                description=self.description
            )