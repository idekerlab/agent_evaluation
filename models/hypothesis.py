 

class Hypothesis:
    def __init__(self, db, name=None, hypothesis_text=None, data=None, biological_context=None, analyst_id=None, 
                 dataset_id=None, description=None, analysis_run_id=None, 
                 object_id=None, created=None):
        self.db = db
        self.hypothesis_text = hypothesis_text
        self.data = data
        self.biological_context=biological_context
        self.analyst_id = analyst_id
        self.dataset_id = dataset_id
        self.description = description
        self.analysis_run_id = analysis_run_id
        self.object_id = object_id
        self.created = created
        self.name = name

    @classmethod
    def create(cls, db, hypothesis_text, data, biological_context, analyst_id, dataset_id, description, analysis_run_id, name=None):
        properties = {
            "name": name,
            "hypothesis_text": hypothesis_text,
            "data": data,
            "biological_context": biological_context,
            "analyst_id": analyst_id,
            "dataset_id": dataset_id,
            "description": description,
            "analysis_run_id": analysis_run_id
        }
        object_id, created, _ = db.add(object_id=None, properties=properties, object_type="hypothesis")
        hypothesis = cls(db, name, hypothesis_text, data, biological_context, analyst_id, dataset_id, 
                   description, analysis_run_id, object_id=object_id, created=created)
        if not name:
            analyst_properties, analyst_type = db.load(analyst_id)
            hypothesis.update(name=f"hypothesis - {analyst_properties['name']} - {biological_context}")

        return hypothesis

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
