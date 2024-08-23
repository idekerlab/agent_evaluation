# agent_evaluation
Supports a paper on the development and evaluation of reviewer agents that, in turn, evaluate mechanistic hypotheses derived from datasets.

# Install requirements 

```
conda create -n agent_eval python==3.11
conda activate agent_eval
pip install -r requirements.txt
```

# Repo Structure
```

Given your preference for simplicity and keeping the business logic in a single `ae.py` file, here's a proposed repository structure:

```
agent_evaluation/
│
├── app/
│   ├── __init__.py
│   ├── analysis.py
│   ├── app.py
│   ├── chat_app.py
│   ├── config.py
│   ├── sqlite_database.py
│   ├── temporary_database.py
│   └── view_edit_specs.py
│
├── data/               # Holds many dataset files originally provided by Laura, now refactored by us
│
├── helpers/            # Has helper python files used throughout the backend
│   ├── csv_helpers.py
│   └── safe_dict.py
│
├── models/             # Contains python classes for each object type
│   ├── agent.py
│   ├── analysis_plan.py
│   └── ...
│
├── notebooks/          # Contains Jupyter notebooks that interact with the data programmatically
│
├── prompts/            # Stores LLM prompts in text files
│
├── react-app/          # Contains the react UI
│   ├── public/
│   ├── src/
│   ├── .env.development
│   ├── .env.production
│   ├── package-lock.json
│   └── package.json
│
├── results/            # Stores LLM prompts in text files
│
├── tests/
│   ├── conftest.py
│   ├── test_main.py
│   ├── test_ae.py
│   └── test_database.py
│
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── scripts.js
│   └── images/
│       └── logo.png
│
├── .gitignore 
├── deployment.md      # Contains documentation for deploying the app
├── LICENSE            # MIT License file
├── main.py            # The entry point of the application
├── README.md
└── requirements.txt   # Lists the project dependencies
```

In this structure:

- The `app/` directory contains the main FastAPI application code.
  - `main.py` is the entry point of the application.
  - `dependencies.py` contains any common dependencies or utility functions used across the application.
  - The `routers/` directory contains the route handlers, separated by resource or functionality.
  - `ae.py` contains the core business logic for the agent evaluation system.
  - `database.py` provides an abstraction layer over the database, allowing the use of either Neo4j or the temporary in-memory database.
  - `temporary_database.py` contains the implementation of the temporary in-memory database.
  - The `templates/` directory contains the HTML templates.

- The `tests/` directory contains the test code for the app, execute `pytest` from the project root directory.
  - `conftest.py` contains pytest fixtures and configuration.
  - `test_main.py` contains tests for the main application.
  - `test_ae.py` contains tests for the agent evaluation business logic.
  - `test_database.py` contains tests for the database abstraction layer.

- The `static/` directory contains static assets like CSS, JavaScript, and images.

- `.gitignore` specifies the files and directories that should be ignored by version control.

- `README.md` provides an overview and documentation for the project.

- `requirements.txt` lists the project dependencies.

- `pytest.ini` contains configuration for running tests with pytest.

