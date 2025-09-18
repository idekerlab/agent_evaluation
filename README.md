# agent_evaluation
This repo is about two things:

1. a system called deckard (in some places, accidently called "deckhard") for reviewing lists of objects in the database.
 - deckard (and its database) is accessible programatically by both its REST api and as an MCP server.
2. analysis code for a dengue fever omics data modeling and hypothesis generation project. It is one of the projects using deckard.

It has a great deal of legacy code from when the deckard system had (1) internal hypothesis generation and review generation features and (2) a rigid schema of objects implemented in the "models" directory

An earlier react-based interface has been superseded by a simpler interface found in the static directory. It uses the same fastAPI service but the front end is based on three one page web apps in plain javascript

Goals:
We want the fast api service and interface to only use localhost:3000  And simplify startup.
We want to remove the legacy code step by step, testing as we go, to be sure we don't remove something important. 

Everything past this point in the file is obsolete:

# Install requirements 

```
conda create -n agent_eval python==3.11
conda activate agent_eval
pip install -r requirements.txt
```

# Repo Structure

```
/your_project
│
├── app/                    # Main application code
│   ├── __init__.py
│   ├── main.py             # Core Flask/FastAPI application
│   └── dependencies.py     # Database connections, etc.
│
├── models/                 # Data models
│   ├── __init__.py
│   ├── llm.py
│   ├── dataset.py
│   ├── test_plan.py
│   └── review.py
│
├── services/               # Business logic
│   ├── __init__.py
│   ├── hypothesis_generation.py
│   └── review_generation.py
│
├── tasks/                  # Asynchronous tasks
│   ├── __init__.py
│   ├── celery_config.py
│   ├── test_plan_tasks.py
│   ├── hypothesis_tasks.py
│   └── review_tasks.py
│
├── templates/              # HTML templates for the web interface
│   └── ...
│
├── static/                 # CSS, JavaScript files
│   └── ...
│
└── tests/                  # Unit and integration tests
    ├── __init__.py
    ├── test_services.py
    └── test_tasks.py


```

Given your preference for simplicity and keeping the business logic in a single `ae.py` file, here's a proposed repository structure:

```
your_project/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── dependencies.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── tests.py
│   │   └── hypotheses.py
│   ├── ae.py
│   ├── database.py
│   ├── temporary_database.py
│   └── templates/
│       ├── home.html
│       └── test_details.html
│
├── tests/
│   ├── __init__.py
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
├── README.md
├── requirements.txt
└── pytest.ini
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

