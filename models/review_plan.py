from models.review_set import ReviewSet

class ReviewPlan:
    def __init__(self, db, name=None, agent_ids=None, analysis_run_id=None, 
                 description=None, object_id=None, created=None):
        self.db = db
        self.name = name
        self.agent_ids = agent_ids if agent_ids is not None else []
        self.analysis_run_id = analysis_run_id
        self.description = description
        self.object_id = object_id
        self.created = created

    @classmethod
    def create(cls, db, name, agent_ids, analysis_run_id, description=''):
        properties = {
            "name": name,
            "agent_ids": agent_ids,
            "analysis_run_id": analysis_run_id,
            "description": description
        }
        object_id, created, _ = db.add(object_id=None, properties=properties, object_type="review_plan")
        return cls(db, name = name, agent_ids = agent_ids, analysis_run_id = analysis_run_id, description = description, object_id=object_id, created=created)

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

    def generate_review_set(self, review_set_name=None):
            """ Generate a new ReviewSet instance based on this ReviewPlan. """
            if not self.agent_ids or not self.analysis_run_id:
                raise ValueError("ReviewPlan is not properly configured.")
            return ReviewSet.create(
                db=self.db,
                review_plan_id=self.object_id,
                agent_ids=self.agent_ids,
                analysis_run_id=self.analysis_run_id,
                description=self.description,
                name=review_set_name if review_set_name else f"{self.name} - Set {self.number_of_sets()}"
            )
    
    def number_of_sets(self):
        review_sets = self.db.find("review_set")
        num_sets = 0
        for review_set in review_sets:
            if review_set["properties"]["review_plan_id"] == self.object_id:
                num_sets += 1
        return num_sets + 1