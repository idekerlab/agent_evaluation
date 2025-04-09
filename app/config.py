import configparser
import os

def load_config(config_path=None):
    # Create a ConfigParser object
    config = configparser.ConfigParser()
    config_path = config_path
    # we can explicitly pass in the config_path, such as in test scripts
    if config_path is None:
            # try to get the configuration file location from the environment variable
        try:
            config_path = os.environ['DATABASE_CONFIG_PATH']
        except KeyError:
            config_path = os.path.expanduser('~/ae_config/config.ini')

    config_files = config.read(config_path)
    if config_files is None or len(config_files) == 0:
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    return config

def load_database_uri(config_path=None):
    config = load_config(config_path=config_path)
    uri = config.get('SQLITE', 'URI', fallback=None)
    return uri
 
def load_api_key(key_name, config_path=None):
    config = load_config(config_path=config_path)
    # Access the API key
    api_key = config.get('API_KEYS', key_name, fallback=None)
    return api_key

def load_api_keys(config_path=None):
    config = load_config(config_path=config_path)
    # Access the API keys
    openai_api_key = config.get('API_KEYS', 'OPENAI_API_KEY', fallback=None)
    groq_api_key = config.get('API_KEYS', 'GROQ_API_KEY', fallback=None)
    anthropic_api_key = config.get('API_KEYS', 'ANTHROPIC_API_KEY', fallback=None) 
    google_api_key = config.get('API_KEYS', 'GOOGLEAI_KEY', fallback=None)   
    return openai_api_key, groq_api_key, anthropic_api_key, google_api_key

def load_local_server_url(config_path=None):
    config = load_config(config_path=config_path)
    # Access the local server URL
    local_server_url = config.get('API_KEYS', 'LOCAL_MODEL_HOST', fallback=None)
    return local_server_url


def load_constant_from_config(keys):
    '''
    keys: list of keys to be read from the config file
    '''
    # Create a ConfigParser object
    config = configparser.ConfigParser()
    
    # Define the path to the configuration file
    config_file_path = os.path.expanduser('~/ae_config/config.ini')
    
    # Read the configuration file
    config.read(config_file_path)
    if len(keys) == 1:
        return config.get('CONSTANT VAR', keys[0], fallback=None)
    else:
        return [config.get('CONSTANT VAR', key, fallback=None) for key in keys]
    
# Example usage
# openai_key, groq_key = load_api_keys()
# print("OpenAI API Key:", openai_key)
# print("Groq API Key:", groq_key)
