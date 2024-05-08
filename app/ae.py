from openai import OpenAI, APIError
from groq import Groq
import os
import requests


def get_property(obj, property_name, default=None):
    if 'properties' in obj:
        obj = obj['properties']  # get the properties dictionary
    if property_name in obj:
        return obj[property_name]
    return default


def load_dataset(db, dataset_id):
    dataset = db.load(dataset_id)
    return dataset


def create_llm(db, type="OpenAI", model_name="gpt-3.5-turbo-1106", max_tokens=2048, seed=None, temperature=0.5):
    llm = {"type": type,
           "model_name": model_name,
           "max_tokens": max_tokens,
           "seed": seed,
           "temperature": temperature}
    llm_id = db.add(llm, label="llm")
    return llm_id


def query_llm(db, llm_id, context, prompt):
    llm = db.load(llm_id)
    type = get_property(llm, 'type')
    if type == 'OpenAI':
        text, _ = query_openai(llm, context, prompt)
        return text
    elif type == 'Groq':
        text, _ = query_groq(llm, context, prompt)
        return text
    else:
        raise ValueError(f"Unsupported llm type: {type}")


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
    model_name = get_property(llm, 'model_name')
    max_tokens = get_property(llm, 'max_tokens')
    seed = get_property(llm, 'seed')
    temperature = get_property(llm, 'temperature')

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


def query_groq(llm, context, prompt):
    """
    Queries a model hosted on groq with the given context and prompt.

    :param context: The context to use when querying the model.
    :param prompt: The prompt to use when querying the model.
    :return: A tuple containing the model's response, system fingerprint, and tokens used.
    """
    key = os.environ.get('GROQ_API_KEY')
    if not key:
        raise EnvironmentError("GROQ_API_KEY environment variable not set.")
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    model_name = get_property(llm, 'model_name')
    max_tokens = get_property(llm, 'max_tokens')
    temperature = get_property(llm, 'temperature')

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            stop=None,
            temperature=temperature,
        )
        response_content = response.choices[0].message.content.strip()
        tokens_used = response.usage.total_tokens
        return response_content, tokens_used
    except Exception as e:
        raise Exception(f"groq transaction error occurred: {e}")


def create_analyst(db, llm_id, context, prompt_template, name):
    analyst = {"llm_id": llm_id,
               "context": context,
               "prompt_template": prompt_template,
               "name": name}
    analyst_id = db.add(analyst, label="analyst")
    return analyst_id


def create_dataset(db, data, experiment_description):
    dataset = {"data": data,
               "experiment_description": experiment_description}
    dataset_id = db.add(dataset, label="Dataset")
    return dataset_id


def create_test_plan(db, analyst_ids=None, dataset_id=None, n_hypotheses_per_analyst=1):
    test_plan = {"analyst_ids": analyst_ids,
                 "dataset_id": dataset_id,
                 "n_hypotheses_per_analyst": n_hypotheses_per_analyst}
    test_plan_id = db.add(test_plan, label="testplan")
    return test_plan_id


def create_test(db, test_plan_id=None):
    test_plan = db.load(test_plan_id)
    test = {"test_plan_id": test_plan_id,
            "hypothesis_ids": []}
    for _ in range(get_property(test_plan, "n_hypotheses_per_analyst")):
        for analyst_id in get_property(test_plan, "analyst_ids"):
            hypothesis_id = generate_hypothesis(
                db, analyst_id, get_property(test_plan, "dataset_id"))
            test["hypothesis_ids"].append(hypothesis_id)
    test_id = db.add(test, label="test")
    return test_id


def load_tests(db):
    return db.load_all("test")


def generate_hypothesis(db, analyst_id, dataset_id):
    dataset = load_dataset(db, dataset_id)
    data = get_property(dataset, 'data')
    analyst = db.load(analyst_id)
    prompt = get_property(analyst,'prompt_template').format(data=data,
                                                             experiment_description=get_property(dataset, 'experiment_description'))
    llm_id = get_property(analyst,'llm_id')
    hypothesis_text = query_llm(db, 
                                llm_id, 
                                get_property(analyst, "context"), 
                                prompt)
    hypothesis = {"hypothesis_text": hypothesis_text,
                  "analyst_id": analyst_id,
                  "dataset_id": dataset_id}
    # add the hypothesis to the database, return the id
    hypothesis_id = db.add(hypothesis, label="hypothesis")
    return hypothesis_id


def load_hypotheses(db, test_id):
    test = db.load(test_id)
    hypotheses = []
    for hypothesis_id in get_property(test, 'hypothesis_ids'):
        hypothesis = db.load(hypothesis_id)
        hypotheses.append(hypothesis)
    return hypotheses, test


def create_reviewer(db, llm_id, context, prompt_template, name):
    reviewer = {"llm_id": llm_id,
                "context": context,
                "prompt_template": prompt_template,
                "name": name}
    reviewer_id = db.add(reviewer, label="reviewer")
    return reviewer_id


def create_review_plan(db, reviewer_ids, test_id):
    review_plan = {"reviewer_ids": reviewer_ids,
                   "test_id": test_id}
    review_plan_id = db.add(review_plan, label="reviewplan")
    return review_plan_id

# The reviewer composes an llm prompt from the hypotheses in the test,
# The llm generates a review that ranks the hypotheses and provides a rationale for the ranking


def create_review(db, reviewer_id, test_id):
    test = db.load(test_id)
    reviewer = db.load(reviewer_id) 
    test_plan_id = get_property(test, "test_plan_id")
    test_plan = db.load(test_plan_id)
    dataset_id = get_property(test_plan, "dataset_id")
    dataset = db.load(dataset_id)
    data = get_property(dataset, "data")
    n = 0
    hypotheses_section = ""
    section_identifiers = ["MAPLE", "ASPEN", "WILLOW", "SPRUCE", "OAK", "PINE", "BIRCH", "ELM", "CEDAR", "POPLAR"]
    for hypothesis_id in get_property(test, 'hypothesis_ids'):
        hypothesis = db.load(hypothesis_id)
        id = section_identifiers[n % len(section_identifiers)]
        hypotheses_section = "===========================================\n\n".join([hypotheses_section,
                                          f'hypothesis {id}: {get_property(hypothesis, "hypothesis_text")}'])
        n += 1
    prompt = get_property(reviewer, 'prompt_template').format(hypotheses_section=hypotheses_section,
                                                              data=data)  
    result = query_llm(db,
                       get_property(reviewer, 'llm_id'),
                       get_property(reviewer, "context"), 
                       prompt)
    review = {"result": result,
              "reviewer_id": reviewer.get('id'),
              "test_id": test_id,
              "hypotheses_section": hypotheses_section}
    review_id = db.add(review, label="review")
    return review_id


def create_review_set(db, review_plan_id):
    review_plan = db.load(review_plan_id)
    review_set = {"review_plan_id": review_plan_id,
                  "review_ids": [], }
    for reviewer_id in get_property(review_plan, 'reviewer_ids'):
        review_id = create_review(db, 
                               reviewer_id, 
                               get_property(review_plan, "test_id"))
        review_set['review_ids'].append(review_id)
    review_set_id = db.add(review_set, label="reviewset")
    return review_set_id
