
import os
import sys
import openai
import time
import requests
# import genai
import subprocess
import logging
import subprocess
import os


logger = logging.getLogger(__name__)


class LLM:
    def __init__(self, model_name, temperature=0, max_tokens=1000, seed=42):
        """
        Initializes a new LLM instance.

        :param model: The model to query
        :param temperature: The temperature to use when querying the model
        :param max_tokens: The maximum number of tokens to generate
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.seed = seed

        print(f"Model: {self.model_name}, Temperature: {self.temperature}, Max Tokens: {self.max_tokens}, Seed: {self.seed}")
        
    def query(self, context, prompt):
        """
        Queries the model with the given prompt.
        :param context: The context to use when querying the model
        :param prompt: The prompt to use when querying the model
        :return: The model's response to the prompt
        """
        return None
        
class OpenAI_LLM (LLM):
    def __init__(self, model_name, temperature=0, max_tokens=2048, seed=42):
        """
        Initializes a new OpenAI instance.

        :param model: The model to query
        :param temperature: The temperature to use when querying the model
        :param max_tokens: The maximum number of tokens to generate
        """
        super().__init__(model_name, temperature, max_tokens, seed)
        
    def query(self, context="you are a helpful assistant", prompt="What number is the meaning of life?"):
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
                response = openai.ChatCompletion.create(
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
            
            except openai.OpenAIError as e:
                print(f"An API error occurred: {e}")
                return None, None
            except openai.InternalServerError as e:
                print(f"Server issue detected, retrying in {backoff_time} seconds...")
                time.sleep(backoff_time)
                retries += 1
                backoff_time *= 2 # Double the backoff time for the next retry
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

class GenAI_LMM (LLM):
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


class ServerModel_LLM (LLM):
    def __init__(self, model_name, temperature=0, max_tokens=1000, seed=42, url=None, key=None):
        """
        Initializes a new server model instance.

        :param model: The model to query
        :param temperature: The temperature to use when querying the model
        :param max_tokens: The maximum number of tokens to generate
        :param seed: The seed to use when querying the model, controls randomness
        """
        super().__init__(model_name, temperature, max_tokens, seed)
        self.url=url
        self.key=key


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
        messages = [{"role": "system", "content": context}, {"role": "user", "content": prompt}]
        print('messages: ' + str(messages))
        # Set up the data for the POST request
        data = {
            "model": self.model_name,
            "prompt": 'Tell me a joke',
            "stream": False,
            "options": {
                "seed": self.seed,
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        }
        headers = None
        # headers = {
        #    "authorization": f'Basic {self.key}'
        # }
        
        while retries < max_retries: ## allow a max of 5 retries if the server is busy or overloaded
            try:
                response = requests.post(self.url, headers=headers, json=data,
                                         timeout=120)

                # Check if the request was successful
                if response.status_code == 200:
                    # return the response
                    return response.json()
                elif response.status_code in [500, 502, 503, 504]:
                    print(response.text)
                    print(f'Encountering server issue {response.status_code}. Retrying in ', backoff_time, ' seconds')                    
                    time.sleep(backoff_time)
                    retries += 1
                    backoff_time *= 2                
                else:
                    print(response.text)
                    error_message = f'The request failed with status code: {response.status_code}'
                    print(error_message)
                    return None, error_message
            except requests.exceptions.RequestException as e:
                print(response.text)
                print('status code: ' + str(response.status_code))
                print('The request failed with an exception: ', e, ' Retrying in ', backoff_time, ' seconds')
                time.sleep(backoff_time)
                retries += 1 
                backoff_time *= 2 # Double the backoff time for the next retry
            except Exception as e:
                print('An unexpected error occurred: ' + str(e))
                return None, str(e)
        return None, "Error: Max retries exceeded, last response error was: " + str(response.status_code)
    

class LocalOllama_LLM(LLM):
    def __init__(self, model_name, temperature, max_tokens, seed=42,
                 ollama_binary='/usr/local/bin/ollama'):
        """
        Initializes a new local model instance.

        :param model: The model to query
        :param temperature: The temperature to use when querying the model
        :param max_tokens: The maximum number of tokens to generate
        :param seed: The seed to use when querying the model, controls randomness
        """
        super().__init__(model_name, temperature, max_tokens, seed=seed)
        self.ollama_binary = ollama_binary

    def _run_cmd(self, cmd, cwd=None, timeout=360):
        """
        Runs command as a command line process

        :param cmd: command to run
        :type cmd: list
        :param cwd: current working directory
        :type cwd: str
        :param timeout: timeout in seconds before killing process
        :type timeout: int or float
        :raises CellMapsProvenanceError: If **raise_on_error** passed
                                         into constructor is ``True`` and
                                         process times out before completing
        :return: (return code, standard out, standard error)
        :rtype: tuple
        """
        logger.debug('Running command under ' + str(cwd) +
                     ' path: ' + str(cmd))
        print('Running command under ' + str(cwd) +
                     ' path: ' + str(cmd))
        p = subprocess.Popen(cmd, cwd=cwd,
                             text=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        try:
            out, err = p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            logger.warning('Timeout reached. Killing process')
            p.kill()
            out, err = p.communicate()
            raise Exception('Process timed out. '
                                             'exit code: ' +
                                             str(p.returncode) +
                                             ' stdout: ' + str(out) +
                                             ' stderr: ' + str(err))

        # Removing ending new line if value is not None
        if out is not None:
            out = out.rstrip()
        return p.returncode, out, err
    
    def query(self, context, prompt):
        """
        Queries the model with the given prompt.


        """
        updated_prompt = context + " " + prompt
        cwd = os.getcwd()

        cmd = [self.ollama_binary, 'run', self.model_name,
               updated_prompt, '--nowordwrap']
        logger.debug('Running: ' + str(cmd))
        print('Running: ' + str(cmd))
        e_code, out, err = self._run_cmd(cmd=cmd, cwd=cwd, timeout=45)

        return out, str(e_code) + ' ' + str(err)


def main(args):
    print('Hello world')
    testmodel = LocalOllama_LLM('llama2:latest', 0, 1000, ollama_binary='/usr/local/bin/ollama')
    print(str(testmodel.query('You are a researcher', 'Tell me a joke')))

    servertestmodel = ServerModel_LLM('llama2', 0, 1000,
                                      url=os.environ.get("LOCAL_MODEL_HOST"))

    print(str(servertestmodel.query('You are a researcher', 'Tell me a joke')))

    return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))

