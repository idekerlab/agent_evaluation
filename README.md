# agent_evaluation
Supports a paper on the development and evaluation of reviewer agents that, in turn, evaluate mechanistic hypotheses derived from datasets.

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

