 

class Review:
    def __init__(self, db, data=None, hypotheses_text=None, review_text=None, 
                 ranking_data=None, summary_review=None,
                 agent_id=None,  ##### May have to add a hypotheses section
                description=None, review_set_id=None, 
                 object_id=None, name="unnamed", created=None):
        self.db = db
        self.data = data
        self.hypotheses_text = hypotheses_text
        self.review_text = review_text
        self.ranking_data = ranking_data
        self.summary_review = summary_review
        self.agent_id = agent_id
        # self.analysis_run_id = analysis_run_id
        self.description = description
        self.review_set_id = review_set_id
        self.object_id = object_id
        self.name = name
        self.created = created

    @classmethod
    def create(cls, db, data, hypotheses_text, review_text, ranking_data, summary_review, agent_id, description, review_set_id, name=None):
        properties = {
            "data": data,
            "hypotheses_text": hypotheses_text,
            "review_text": review_text,
            "ranking_data": ranking_data,
            "summary_review": summary_review,
            "agent_id": agent_id,
            # "analysis_run_id": analysis_run_id,
            "description": description,
            "review_set_id": review_set_id,
            "name": name
        }
        object_id, created, _ = db.add(object_id=None, properties=properties, object_type="review")
        return cls(db, data, review_text, ranking_data, summary_review, agent_id,
                   description, review_set_id, object_id=object_id, name=name, created=created)

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
