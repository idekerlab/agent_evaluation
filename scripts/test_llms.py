import sys
import os
import time
import threading
import itertools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.sqlite_database import SqliteDatabase
from app.config import load_database_config
from app.view_edit_specs import object_specifications
from models.llm import LLM

def setup_db():
    cwd = os.getcwd()
    dirname = os.path.dirname(cwd)
    # print(cwd)
    # print(dirname)
    sys.path.append(dirname)

    # print(sys.path)
    
    _, database_uri, _, _ = load_database_config()
    db = SqliteDatabase(database_uri)
    return db


if __name__ == "__main__":
    db = setup_db()
    
    llm_props = object_specifications["llm"]["properties"]
    
    working_models_count = 0
    total_models_count = 0
    failed_models = []

    for model_type in llm_props["type"]["options"]:
        for model_name in llm_props["model_name"]["options"][model_type]:
            total_models_count += 1
            try:
                print(f"\n{model_type}: {model_name}\n")
                
                llm = LLM.create(db, model_type, model_name, seed=42)
                
                start_time = time.time()
                response = llm.query("random context", "Tell me a joke in one line")
                end_time = time.time()
                
                duration = end_time - start_time
                
                print(response.strip())
                print(f"\nduration: {duration:.4f} seconds")
                
                working_models_count += 1

            except Exception as e:
                print(f"\nFailed to query {model_type}: {model_name}\nError: {e}\n")
                failed_models.append((model_type, model_name))
  
            db.remove(llm.object_id)
            
            print("\n##########################")
                
    print("\nAnalysis complete!")
    print(f"Number of working models: {working_models_count}/{total_models_count}")
    if failed_models:
        print(f"{len(failed_models)} failed model{'s' if len(failed_models) > 1 else ''}:")
        for model_type, model_name in failed_models:
            print(f"{model_type}: {model_name}")
    else:
        print("No models failed. 🎉")
    print("")

            
    