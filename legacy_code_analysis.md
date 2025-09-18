# Legacy Code Analysis

This document identifies components of the Deckard system that appear to be legacy code and analyzes their dependencies with active components.

## Database Structure

The SQLite database uses a simple, flexible schema:

```
Table: nodes
- object_id TEXT PRIMARY KEY     # Unique identifier for each object
- properties TEXT                # JSON string containing all object properties
- object_type TEXT               # Type of object (e.g., object_list, review, etc.)
```

This flexible schema allows for storing any type of object without rigid structure requirements.

## Legacy Components

### 1. Rigid Schema Model Definitions

**Description**: The system originally used rigid, predefined schemas for object types.

**Files/Locations**:
- `app/view_edit_specs.py` - Contains detailed specifications for legacy object types
- `models/` directory - Contains class definitions for various object types

**Legacy Object Types**:
- `llm` - Large Language Model configurations
- `agent` - Agent configurations for running LLMs
- `dataset` - Dataset objects with experiment descriptions
- `analysis_plan` - Plans for automated hypothesis generation
- `analysis_run` - Execution instances of analysis plans
- `hypothesis` - Generated hypothesis objects
- `review_plan` - Plans for automated review generation
- `review_set` - Execution instances of review plans
- `judgment_space` - For comparing reviews

**Dependencies**:
- `app/routes/object_routes.py` checks `object_specifications` to determine if an object type has a rigid schema
- `app/handlers/form_handlers.py` likely processes forms based on these specifications
- `app/handlers/file_handlers.py` referenced in object_routes.py for preprocessing properties

### 2. Agent Execution Framework

**Description**: Code for executing agents against objects to generate hypotheses and reviews.

**Files/Locations**:
- `app/routes/agent_routes.py` - API endpoints for agent execution
- `app/task_management.py` - Background task management
- `models/agent.py` - Agent model definition
- `models/json_object.py` - Used for storing agent results

**Dependencies**:
- Referenced in `app/routes/__init__.py`
- `app/app.py` imports and includes these routes

### 3. Analysis & Review Frameworks

**Description**: Code for managing analysis plans, running analyses, and generating reviews.

**Files/Locations**:
- `services/analysisrunner.py` - Analysis execution code
- `services/reviewrunner.py` - Review generation code
- `models/analysis_plan.py` - Analysis plan model
- `models/review_plan.py` - Review plan model

**Dependencies**:
- Referenced in `app/routes/object_routes.py` in the `/execute_object` endpoint
- May be imported in other route handlers

### 4. Old React Frontend

**Description**: A React-based frontend has been superseded by the static JavaScript interfaces.

**Files/Locations**:
- `react-app/` directory - Contains the React application code

**Dependencies**:
- There's a catch-all route in `app/app.py` that attempts to serve index.html from this directory
- No critical dependencies on active components

## Active Components & Their Dependency Risk

### 1. Browser Interface

**Dependency Risk: Low**
- Main dependency is on the API endpoints in `object_routes.py` and `knowledge_graph_routes.py`
- Uses a flexible approach to object types, not relying on rigid schemas
- No direct dependency on agent execution code

### 2. Reviewer Interface

**Dependency Risk: Low to Medium**
- Depends on specific object types (`object_list`, `review`) but these appear to be part of the active system
- May have some presentation logic that relies on object specifications
- No apparent dependency on agent execution code

### 3. NDEx Import Interface

**Dependency Risk: Low**
- Uses API endpoints to create objects and object lists
- Doesn't appear to depend on rigid schema validation
- No dependency on agent execution code

### 4. Object Routes API

**Dependency Risk: Medium to High**
- Has code paths for both strictly typed objects (checking `object_specifications`) and flexibly typed objects
- Imports handlers from `app/handlers/` that may depend on legacy models
- Imports specific model classes from the `models/` directory
- Contains endpoints for executing analysis_plan and review_plan objects

### 5. Knowledge Graph Routes API

**Dependency Risk: Low**
- Provides general SQL query interface to database
- Doesn't appear to depend on specific model classes
- Relationship handling is generic

### 6. MCP Server

**Dependency Risk: Low to Medium**
- Provides tools to interact with the database
- No direct dependency on agent execution
- May have some assumptions about object types but appears flexible

## Separation Strategy

To safely remove legacy code while preserving active functionality:

1. **Preserve Core Database Operations**:
   - Keep `app/sqlite_database.py` untouched - it has a flexible design
   - Ensure all CRUD operations continue to work with the flexible schema

2. **Simplify Object Routes**:
   - Remove specific model imports
   - Remove or simplify code paths that handle rigid schema validation
   - Maintain endpoints that are used by active interfaces

3. **Remove Agent Routes First**:
   - These appear to be completely unused by active components
   - Update `app/routes/__init__.py` and `app/app.py` accordingly

4. **Remove or Simplify Task Management**:
   - If only used for agent execution, can be removed
   - If used elsewhere, simplify to essential functionality

5. **Remove Analysis/Review Code**:
   - Remove execution endpoints from object_routes.py
   - Remove services/analysisrunner.py and services/reviewrunner.py
   - Remove related model imports

6. **Update Frontend Code**:
   - Ensure frontend JavaScript doesn't reference removed endpoints
   - Update any client-side code that expects rigid schemas

7. **Clean up Models Directory**:
   - Gradually remove model classes that are no longer referenced
   - Start with those that have minimal dependencies (e.g., LLM, agent)
