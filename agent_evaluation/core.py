from agent_evaluation.db_object import DB_Object 
from openai import OpenAI, APIError
import os
import requests

def load_dataset(db, dataset_id):
    dataset = db.get(dataset_id)
    return dataset

def create_llm(db, type, model_name, max_tokens=None, seed=None, temperature=None, persist=False):
    llm = {"label": "LLM",
           "type": type,
           "model_name": model_name,
           "max_tokens": max_tokens,
           "seed": seed,
           "temperature": temperature}
    llm_id = db.add(llm)
    return llm_id

def query_llm(db, llm_id, context, prompt):
    llm = db.load(llm_id)
    type = llm.get('type')
    if type == 'OpenAI':
        result_text = query_openai(db, llm, context, prompt)
    elif type == 'Ollama':
        pass
    return result_text

def query_openai(llm, context, prompt):
    
        """
        Queries the OpenAI model with the given context and prompt.

        :param context: The context to use when querying the model.
        :param prompt: The prompt to use when querying the model.
        :return: A tuple containing the model's response, system fingerprint, and tokens used.
        """
        key = os.environ.get('OPENAI_API_KEY')
        if not key:
            raise EnvironmentError("OPENAI_API_KEY environment variable not set.")
        client = OpenAI()
        client.api_key = key
        model_name = llm.get('model_name')
        max_tokens = llm.get('max_tokens') or 2048
        seed = llm.get('seed') or None
        temperature = llm.get('temperature') or 0.5

        try:
            response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": context},
                        {"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    n=1,
                    stop=None,
                    seed=seed,
                    temperature=temperature,
                )
            response_content = response.choices[0].message.content.strip()
            tokens_used = response.usage.total_tokens
            return response_content, tokens_used
        except APIError as e:
            raise Exception(f"API error occurred: {e}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed with an exception: {e}")


def create_analyst(db, llm_id, context, prompt_template, name, persist=False):
    analyst = {"label": "Analyst",
               "llm_id": llm_id,
               "context": context,
               "prompt_template": prompt_template,
               "name": name}
    analyst_id = db.add(analyst)
    return analyst_id

def create_dataset(db, data, experiment_description, persist=False):
    dataset = {"label": "Dataset",
               "data": data,
               "experiment_description": experiment_description}
    dataset_id = db.add(dataset)
    return dataset_id

def create_test_plan(db, analysts, dataset_id, n_hypotheses, persist=False):
    test_plan = {"label": "TestPlan",
                 "analysts": analysts,
                 "dataset_id": dataset_id,
                 "n_hypotheses": n_hypotheses}
    test_plan_id = db.add(test_plan)
    return test_plan_id

def create_test(db, analysts, dataset_id, n_hypotheses, persist=False):
    test = {"label": "Test",
            "analysts": analysts,
            "dataset_id": dataset_id,
            "n_hypotheses": n_hypotheses,
            "hypotheses": []}
    test_id = db.add(test)
    for _ in range(n_hypotheses):
        for analyst_id in analysts:
            hypothesis_id = generate_hypothesis(db, analyst_id, dataset_id)
            test["hypotheses"].append(hypothesis_id)
    db.update(test_id, test)
    return test_id

def generate_hypothesis(db, analyst_id, dataset_id):
    dataset = load_dataset(dataset_id)   
    data = dataset.get('data')
    analyst = load_analyst(analyst_id)
    prompt = analyst.get('prompt_template').format(data=data, experiment_description=dataset.get('experiment_description'))
    llm_id = analyst.get('llm_id')
    llm = db.load(llm_id)  
    hypothesis_text = query_llm(llm, analyst.get("context"), prompt)  
    hypothesis = {"label": "Hypothesis",
                    "data": hypothesis_text,
                    "analyst_id": analyst_id,
                    "dataset_id": dataset_id}
    hypothesis_id = db.add(hypothesis) # add the hypothesis to the database, return the id
    return hypothesis_id

def create_reviewer(db, llm_id, context, prompt_template, name, persist=False):
    reviewer = {"label": "Reviewer",
                "llm_id": llm_id,
                "context": context,
                "prompt_template": prompt_template,
                "name": name}
    reviewer_id = db.add(reviewer)
    return reviewer_id

def create_review_plan(db, reviewers, test_id, persist=False):
    review_plan = {"label": "ReviewPlan",
                   "reviewers": reviewers,
                   "test_id": test_id}
    review_plan_id = db.add(review_plan)
    return review_plan_id

# The reviewer composes an LLM prompt from the hypotheses in the test,
# The LLM generates a result that ranks the hypotheses and provides a rationale for the ranking
def execute_review(db, reviewer_id, test_id):
    test = db.load(db, test_id)
    reviewer = db.load(reviewer_id)
    hypotheses = []  
    for hypothesis_id in test.get('hypotheses'):
        hypothesis = db.load(hypothesis_id)
        hypotheses.append(hypothesis.get('hypothesis_text'))
    data = test.get("dataset").get("data")
    prompt = reviewer.get('prompt_template').format(hypotheses=hypotheses, data=data) # TODO: implement the prompt template
    result = query_llm(reviewer.get('llm_id'), reviewer.get("context"), prompt)
    review = {"label": "Review",
              "result": result,
              "reviewer_id": reviewer.get('id'),
              "test_id": test_id}
    db.add(review)
    return review

def execute_review_plan(db, review_plan_id):
    review_plan = db.load(review_plan_id)
    review_set = {"label": "ReviewSet",
              "review_plan_id": review_plan_id,
              "reviews": [],}
    for reviewer_id in review_plan.get('reviewers'):
        review = execute_review(db, reviewer_id, review_plan.get("test_id"))
        review_set.get('reviews').append(review)
    review_set_id = db.add(review_set)
    return review_set_id

