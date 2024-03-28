import os
import openai
import time
import json
import requests
import genai

class LLM:
    def __init__(self, model_name, temperature, max_tokens):
        """
        Initializes a new LLM instance.

        :param model: The model to query
        :param temperature: The temperature to use when querying the model
        :param max_tokens: The maximum number of tokens to generate
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
    def query(self, context, prompt):
        """
        Queries the model with the given prompt.
        :param context: The context to use when querying the model
        :param prompt: The prompt to use when querying the model
        :return: The model's response to the prompt
        """
        return None
        
class OpenAI (LLM):
    def __init__(self, model_name, temperature, max_tokens):
        """
        Initializes a new OpenAI instance.

        :param model: The model to query
        :param temperature: The temperature to use when querying the model
        :param max_tokens: The maximum number of tokens to generate
        """
        super().__init__(model_name, temperature, max_tokens)
        
    def query(self, context, prompt):
        """
        Queries the model with the given prompt.

        :param context: The context to use when querying the model
        :param prompt: The prompt to use when querying the model
        :return: The model's response to the prompt
        """
        key = os.environ.get('OPENAI_API_KEY')
        if key is None:
            print("Please set your OpenAI API key as an environment variable.")
            return None, None   
        
        openai.api_key = key
        backoff_time = 10  # Start backoff time at 10 second
        retries = 0

        while retries <= 5: ## allow a max of 5 retries if the server is busy or overloaded
            try:
                response = openai.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "system", "content": context},{"role": "user", "content": prompt}],
                    max_tokens=self.max_tokens,
                    n=1,
                    stop=None,
                    seed=self.seed,
                    temperature=self.temperature,
                )
                tokens_used = response.usage.total_tokens
                response_content = response.choices[0].message.content
                system_fingerprint = response.system_fingerprint
                return response_content, system_fingerprint, tokens_used
            
            except openai.RateLimitError as e:
                print("Rate limit exceeded. Please increate the limit before re-run.")
                return None, None
            except openai.APIConnectionError as e:
                print(f"AIP connection error, retrying in {backoff_time} seconds...")
                time.sleep(backoff_time)
                retries += 1
                backoff_time *= 2 # Double the backoff time for the next retry
            except openai.InternalServerError as e:
                print(f"Server issue detected, retrying in {backoff_time} seconds...")
                time.sleep(backoff_time)
                retries += 1
                backoff_time *= 2 # Double the backoff time for the next retry
            except openai.APIError as e:
                print(f"An API error occurred: {e}")
                return None, None
            except requests.exceptions.RequestException as e:
                print('The request failed with an exception: ', e, ' Retrying in ', backoff_time, ' seconds')
                time.sleep(backoff_time)
                retries += 1 
                backoff_time *= 2 # Double the backoff time for the next retry
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                return None, str(e)  
                 
            if retries > 5:
                print("Max retries exceeded. Please try again later.")
                return None, None

class genai (LLM):
    def __init__(self, model_name, temperature, max_tokens):
        """
        Initializes a new genai instance.

        :param model: The model to query
        :param temperature: The temperature to use when querying the model
        :param max_tokens: The maximum number of tokens to generate
        """
        super().__init__(model_name, temperature, max_tokens)
        
    def query(self, context, prompt):
        """
        Queries the model with the given prompt.

        :param context: The context to use when querying the model
        :param prompt: The prompt to use when querying the model
        :return: The model's response to the prompt
        """

        # configuration load key  
        genai.configure(api_key=os.getenv('GOOGLEAI_KEY'))

        #set up model 
        if self.model_name == None:
            model = genai.GenerativeModel('gemini-pro')
        else:
            model = genai.GenerativeModel(self.model_name)

        #define messages
        merged_prompt = context + prompt
        messages = [
            # {'role':'system',
            #  'parts': "You are an efficient and insightful assistant to a molecular biologist"},
            {'role':'user',
            'parts': merged_prompt}
            ]

        try:
            response = model.generate_content(
                messages, 
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.max_tokens, temperature=self.temperature
                )
            )
        except Exception as e:
            # Handle specific exceptions as needed
            print(f'Encountered an error: {e}')
            return None, str(e)
        
        input_tokens= model.count_tokens(prompt).total_tokens
    
        response_content = response.text
        if response_content:
            output_tokens = model.count_tokens(response_content).total_tokens
            
            total_tokens = input_tokens + output_tokens
            return response_content, None
        else:
            total_tokens = input_tokens
            return None, response._error, total_tokens      


class server_model (LLM):
    def __init__(self, model_name, temperature, max_tokens, seed=42, url=None):
        """
        Initializes a new server model instance.

        :param model: The model to query
        :param temperature: The temperature to use when querying the model
        :param max_tokens: The maximum number of tokens to generate
        :param seed: The seed to use when querying the model, controls randomness
        """
        super().__init__(model_name, temperature, max_tokens)
        self.seed=seed


    def query(self, context, prompt):
        """
        Queries the model with the given prompt.

        :param context: The context to use when querying the model
        :param prompt: The prompt to use when querying the model
        :return: The model's response to the prompt
        """
        backoff_time = 10  # Start backoff time at 10 second
        retries = 0
        max_retries = 5

        ##load messages 
        messages = [{"role": "system", "content": context},{"role": "user", "content": prompt}]
        # Set up the data for the POST request
        data = {
            "model": self.model_name,
            "stream": False,
            "messages":messages,
            "options": {
                "seed": self.seed,
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        }
        while retries < max_retries: ## allow a max of 5 retries if the server is busy or overloaded
            try:
                response = requests.post(self.url, json = data, timeout= 120)

                # Check if the request was successful
                if response.status_code == 200:
                    # return the response
                    # print(response.json())
                    output = response.json()
                    analysis = output['message']['content']                   
                    return  analysis, None # second value is error message 
                elif response.status_code in [500, 502, 503, 504]:
                    print(f'Encountering server issue {response.status_code}. Retrying in ', backoff_time, ' seconds')                    
                    time.sleep(backoff_time)
                    retries += 1
                    backoff_time *= 2                
                else:
                    error_message = f'The request failed with status code: {response.status_code}'
                    print(error_message)
                    return None, error_message
            except requests.exceptions.RequestException as e:
                print('The request failed with an exception: ', e, ' Retrying in ', backoff_time, ' seconds')
                time.sleep(backoff_time)
                retries += 1 
                backoff_time *= 2 # Double the backoff time for the next retry
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                return None, str(e)
        return None, "Error: Max retries exceeded, last response error was: " + str(response.status_code)