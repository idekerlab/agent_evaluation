
import app.ae as ae


def load_test_data(db):
    llm_id = ae.create_llm(db, type="OpenAI", model_name="gpt-3.5-turbo-1106")

    analyst_context = "Cancer research"
    analyst_prompt_template = """
    Given the following data: 
    {data}, and the experiment description: 
    {experiment_description}
    generate a novel hypothesis providing a mechanistic explanation for some aspect of the data,
    followed by a proposal for a validation experiment.
    """

    analyst_id_1 = ae.create_analyst(db,
                                     llm_id=llm_id,
                                     context=analyst_context,
                                     prompt_template=analyst_prompt_template,
                                     name="Jane")

    analyst_id_2 = ae.create_analyst(db,
                                     llm_id=llm_id,
                                     context=analyst_context,
                                     prompt_template=analyst_prompt_template,
                                     name="John")

    data = "...."  # some data

    dataset_id = ae.create_dataset(db,
                                   data=data,
                                   experiment_description="Analysis of gene expression and mutations in cancer cells.")

    def create_fake_hypothesis(analyst_id, dataset_id, hypothesis_text):
        hypothesis = {"hypothesis_text": hypothesis_text,
                      "analyst_id": analyst_id,
                      "dataset_id": dataset_id}
        # add the hypothesis to the database, return the id
        hypothesis_id = db.add(hypothesis, label="hypothesis")
        return hypothesis_id

    hypothesis_id_1 = create_fake_hypothesis(analyst_id_1,
                                             dataset_id,
                                             "BRCA1 expression is high in cancer cells.")

    hypothesis_id_2 = create_fake_hypothesis(analyst_id_2,
                                             dataset_id,
                                             "TP53 mutation is absent in cancer cells.")

    test_plan_id = ae.create_test_plan(db,
                                       analyst_ids=[
                                           analyst_id_1, analyst_id_2],
                                       dataset_id=dataset_id,
                                       n_hypotheses_per_analyst=2)

    def create_fake_test(test_plan_id, hypothesis_ids):
        test = {"hypothesis_ids": hypothesis_ids,
                "test_plan_id": test_plan_id, }
        test_id = db.add(test, label="test")
        return test_id

    test_id = create_fake_test(
        test_plan_id, [hypothesis_id_1, hypothesis_id_2])

    reviewer_context = 'You are a scientist adept at impartially evaluating the quality of hypotheses.'

    revewer_prompt_template = """
    ...
    """

    reviewer_id = ae.create_reviewer(db,
                                     llm_id=llm_id,
                                     context=reviewer_context,
                                     prompt_template=revewer_prompt_template,
                                     name="Pasteur")

    def create_fake_review_plan(reviewer_id, test_id):
        review_plan = {"reviewer_ids": [reviewer_id],
                       "test_id": test_id}
        review_plan_id = db.add(review_plan, label="reviewplan")
        return review_plan_id

    review_plan_id = create_fake_review_plan([reviewer_id], test_id)
