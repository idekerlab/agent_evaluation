from models.review_set import ReviewSet

class ReviewPlan:
    def __init__(self, db, name=None, analyst_ids=None, analysis_run_id=None, 
                 description=None, object_id=None, created=None):
        self.db = db
        self.name = name
        self.analyst_ids = analyst_ids if analyst_ids is not None else []
        self.analysis_run_id = analysis_run_id
        self.description = description
        self.object_id = object_id
        self.created = created

    @classmethod
    def create(cls, db, name, analyst_ids, analysis_run_id, description=''):
        properties = {
            "name": name,
            "analyst_ids": analyst_ids,
            "analysis_run_id": analysis_run_id,
            "description": description
        }
        object_id, created, _ = db.add(object_id=None, properties=properties, object_type="review_plan")
        return cls(db, name = name, analyst_ids = analyst_ids, analysis_run_id = analysis_run_id, description = description, object_id=object_id, created=created)

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
            if not self.analyst_ids or not self.analysis_run_id:
                raise ValueError("ReviewPlan is not properly configured.")
            return ReviewSet.create(
                db=self.db,
                review_plan_id=self.object_id,
                analyst_ids=self.analyst_ids,
                analysis_run_id=self.analysis_run_id,
                description=self.description,
                name=review_set_name
            )