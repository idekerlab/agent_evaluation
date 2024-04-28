import sys
import os

cwd = os.getcwd() # Current working directory
dirname = os.path.dirname(cwd) # Parent directory
# print("================")
# print(cwd)
# print(dirname)
sys.path.append(cwd)# Add the parent directory to the Python path
# print("================")
# print(sys.path)
# print("================")

from app.database import Database
from agent_evaluation.llm import OpenAI_LLM

# Define the database connection details
uri = "bolt://localhost:7687"
user = "neo4j"
password = "fredfred"

# Initialize the Database object
db = Database(uri, user, password)

try:
    # Instantiating the LLM with 'persist=True' and gpt-3.5-turbo-1106
    the_llm = OpenAI_LLM(
        db=db,
        model_name="gpt-3.5-turbo-1106",
        persist=True)
    
    print(f'llm = {the_llm.model_name} persisted={the_llm.persisted} db_unique_id={the_llm.db_unique_id}')

    context = "you are a helpful assistant. "
    prompt = "What is the captial of France? Answer in one sentence."   

    completion = the_llm.client.chat.completions.create(
        model=the_llm.model_name,
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": prompt}
            ]
    )
    print(f'#1 simple: {completion.choices[0].message.content}')

    completion = the_llm.client.chat.completions.create(
                    model=the_llm.model_name,
                    messages=[
                        {"role": "system", "content": context},
                        {"role": "user", "content": prompt}],
                    max_tokens=the_llm.max_tokens,
                    n=1,
                    stop=None,
                    seed=the_llm.seed,
                    temperature=the_llm.temperature,
                )
    print(f'#2 with more args: {completion.choices[0].message.content}')

    response, tokens_used = the_llm.query(context, prompt)
    print(f"#3 using the LLM object: {response}")
    print(f"tokens: {tokens_used}")


except Exception as e:
    print("hello_llm: An error occurred:", e)

finally:
    # remove the LLM object from the database
    if the_llm.persisted is True:
        db.remove(the_llm.db_unique_id)
        print(f"LLM object {the_llm.db_unique_id} removed from the database.")  

    # Close the database session
    db.close()
    print("Database session closed.")
