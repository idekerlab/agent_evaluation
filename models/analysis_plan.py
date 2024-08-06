from models.analysis_run import AnalysisRun

class AnalysisPlan:
    def __init__(self, db, name=None, agent_ids=None, dataset_id=None, 
                 n_hypotheses_per_agent=0, biological_context=None,
                 description=None, object_id=None,  created=None):
        self.db = db
        self.name = name
        self.agent_ids = agent_ids if agent_ids is not None else []
        self.dataset_id = dataset_id
        self.n_hypotheses_per_agent = n_hypotheses_per_agent
        self.biological_context = biological_context
        self.description = description
        self.object_id = object_id
        self.created = created

    @classmethod
    def create(cls, db, name, agent_ids, dataset_id, n_hypotheses_per_agent, description=''):
        properties = {
            "name": name,
            "agent_ids": agent_ids,
            "dataset_id": dataset_id,
            "n_hypotheses_per_agent": n_hypotheses_per_agent,
            "description": description
        }
        object_id, created, _ = db.add(object_id=None, properties=properties, object_type="analysis_plan")
        return cls(db, name, agent_ids, dataset_id, n_hypotheses_per_agent, 
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

    def generate_analysis_run(self, biological_context=None, analysis_run_name = None):
            """ Generate a new AnalysisRun instance based on this AnalysisPlan. """
            if not self.agent_ids or not self.dataset_id:
                raise ValueError("AnalysisPlan is not properly configured.")
            return AnalysisRun.create(
                db=self.db,
                analysis_plan_id=self.object_id,
                agent_ids=self.agent_ids,
                dataset_id=self.dataset_id,
                n_hypotheses_per_agent=self.n_hypotheses_per_agent,
                biological_context=self.biological_context if biological_context == None else biological_context,
                description=self.description,
                name=analysis_run_name if analysis_run_name else "none"
            )
