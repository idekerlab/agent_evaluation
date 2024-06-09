 

class Hypothesis:
    def __init__(self, db, data=None, hypothesis_text=None, analyst_id=None, 
                 dataset_id=None, description=None, analysis_run_id=None, 
                 object_id=None, created=None):
        self.db = db
        self.data = data
        self.hypothesis_text = hypothesis_text
        self.analyst_id = analyst_id
        self.dataset_id = dataset_id
        self.description = description
        self.analysis_run_id = analysis_run_id
        self.object_id = object_id
        self.created = created

    @classmethod
    def create(cls, db, data, hypothesis_text, analyst_id, dataset_id, description, analysis_run_id):
        properties = {
            "data": data,
            "hypothesis_text": hypothesis_text,
            "analyst_id": analyst_id,
            "dataset_id": dataset_id,
            "description": description,
            "analysis_run_id": analysis_run_id
        }
        object_id, created, _ = db.add(object_id=None, properties=properties, object_type="hypothesis")
        return cls(db, data, hypothesis_text, analyst_id, dataset_id, 
                   description, analysis_run_id, object_id=object_id, created=created)

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
