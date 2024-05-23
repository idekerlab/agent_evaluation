import configparser
import os

def load_neo4j_config():
    # Create a ConfigParser object
    config = configparser.ConfigParser()
    
    # Define the path to the configuration file
    config_file_path = os.path.expanduser('~/ae_config/config.ini')
    
    # Read the configuration file
    config.read(config_file_path)
    
    # Access the Neo4j connection details
    uri = config.get('NEO4J', 'URI', fallback=None)
    user = config.get('NEO4J', 'USER', fallback=None)
    password = config.get('NEO4J', 'PASSWORD', fallback=None)
    
    return uri, user, password

def load_database_config(path='~/ae_config/config.ini'):
    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Define the path to the configuration file
    config_file_path = os.path.expanduser(path)

    # Read the configuration file
    config.read(config_file_path)

    # Access the database connection details
    db_type = config.get('DATABASE', 'TYPE', fallback=None)

    if db_type == 'neo4j':
        uri = config.get('NEO4J', 'URI', fallback=None)
        user = config.get('NEO4J', 'USER', fallback=None)
        password = config.get('NEO4J', 'PASSWORD', fallback=None)
        return db_type, uri, user, password
    elif db_type == 'sqlite':
        uri = config.get('SQLITE', 'URI', fallback=None)
        return db_type, uri, None, None
    elif db_type in ['postgresql', 'mysql']:
        uri = config.get(db_type.upper(), 'URI', fallback=None)
        user = config.get(db_type.upper(), 'USER', fallback=None)
        password = config.get(db_type.upper(), 'PASSWORD', fallback=None)
        return db_type, uri, user, password
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
    
def load_api_key(key_name):
    # Create a ConfigParser object
    config = configparser.ConfigParser()
    
    # Define the path to the configuration file
    config_file_path = os.path.expanduser('~/ae_config/config.ini')
    
    # Read the configuration file
    config.read(config_file_path)
    
    # Access the API key
    api_key = config.get('API_KEYS', key_name, fallback=None)
    return api_key

def load_api_keys():
    # Create a ConfigParser object
    config = configparser.ConfigParser()
    
    # Define the path to the configuration file
    config_file_path = os.path.expanduser('~/ae_config/config.ini')
    
    # Read the configuration file
    config.read(config_file_path)
    
    # Access the API keys
    openai_api_key = config.get('API_KEYS', 'OPENAI_API_KEY', fallback=None)
    groq_api_key = config.get('API_KEYS', 'GROQ_API_KEY', fallback=None)
    anthropic_api_key = config.get('API_KEYS', 'ANTHROPIC_API_KEY', fallback=None)  
    
    return openai_api_key, groq_api_key, anthropic_api_key


# Example usage
# openai_key, groq_key = load_api_keys()
# print("OpenAI API Key:", openai_key)
# print("Groq API Key:", groq_key)
