# Deckard System Documentation

## Overview

Deckard is a system for managing and reviewing lists of objects in a database. It provides:

1. **Object Storage and Management**: Store, query, and manipulate objects with flexible schemas
2. **Review Workflow**: Review and score objects based on custom criteria
3. **Network Import**: Import network data from CX2 files or NDEx
4. **API Access**: Both REST API and MCP server interfaces

## System Architecture

```
┌─────────────────┐     ┌─────────────────┐
│  Web Interface  │     │    MCP Server   │
│  (Browser UI)   │←───→│ (mcp-deckhard.py)│
└────────┬────────┘     └─────────────────┘
         │                      │
         ▼                      ▼
┌─────────────────────────────────────────┐
│           FastAPI Service               │
│           (app.py @ :3000)              │
├─────────────────────────────────────────┤
│ Routes:                                 │
│ - object_routes.py     - task_routes.py │
│ - knowledge_graph_*    - etc.           │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│           SQLite Database               │
│     (Flexible object storage)           │
└─────────────────────────────────────────┘
```

## Core Components

### 1. Web Interface

The web interface consists of three main pages:

#### Browser Interface
- **File**: `app/static/browser.html`, `app/static/js/browser.js`
- **Purpose**: Browse, search, and view objects in the database
- **Features**:
  - Execute SQL queries
  - Text search across objects
  - View object details
  - Navigate object relationships
  - Delete objects

#### Reviewer Interface
- **File**: `app/static/reviewer.html`, `app/static/js/reviewer-*.js`
- **Purpose**: Review and score objects in an object list
- **Features**:
  - Navigate through objects in a list
  - Score objects based on custom criteria
  - Save and export reviews
  - Track review progress

#### NDEx Import Interface
- **File**: `app/static/js/ndex-import/ndex-import.html`
- **Purpose**: Import network data from CX2 files
- **Features**:
  - Import networks from CX2 files
  - Preview network data
  - Create object lists from networks

### 2. FastAPI Service

The core backend service runs on FastAPI and provides:

#### Object Routes (`app/routes/object_routes.py`)
- **Purpose**: CRUD operations for all object types
- **Key Endpoints**:
  - `GET /objects/{object_type}` - List objects
  - `GET /objects/{object_type}/{object_id}` - Get object details
  - `POST /objects/{object_type}/create` - Create object
  - `POST /objects/{object_type}/{object_id}/edit` - Update object
  - `DELETE /objects/{object_type}/{object_id}` - Delete object

#### Knowledge Graph Routes (`app/routes/knowledge_graph_routes.py`)
- **Purpose**: SQL queries and relationship management
- **Key Endpoints**:
  - `POST /query_knowledge_graph_database` - Execute SQL
  - `POST /get_relationships` - Get object relationships

#### Other Active Routes
- **NDEx Proxy Endpoints**: Proxy requests to NDEx API
- **Static File Serving**: Serve HTML, JS, CSS files

### 3. MCP Server

The Model Context Protocol server (`mcp-deckhard.py`) provides programmatic access to Deckard:

- **Purpose**: Allow external LLM systems to use Deckard
- **Tools**:
  - `get_deckhard_object_specs` - Get object specifications
  - `list_deckhard_objects` - List objects with filtering
  - `create_deckhard_object` - Create new objects
  - Other utility tools

### 4. Database Structure

The SQLite database uses a flexible schema with the following structure:

#### Main Table: `nodes`
- **Columns**:
  - `object_id` - Unique identifier
  - `object_type` - Type of object (e.g., object_list, review, etc.)
  - `properties` - JSON blob containing all object properties

## Core Object Types

While the system now uses a flexible schema, several object types have special significance:

### 1. object_list
- **Purpose**: Collection of objects to be reviewed
- **Key Properties**:
  - `object_ids` - List of object IDs to review
  - `_criteria` - Array of scoring criteria
  - `_order` - Optional property order

### 2. review_list
- **Purpose**: Store review scores for an object list
- **Key Properties**:
  - `object_list_id` - ID of the reviewed list
  - `object_ids` - Array of object IDs being reviewed
  - `reviewer` - Name of the reviewer
  - `_criteria` - Array of scoring criteria copied from the object_list
  - `scores` - Array of score objects, each with a reviewed_object ID and scores
  - `status` - Status of the review (open, submitted)
  - `submit_date` - Timestamp when the review was submitted

**Note**: While "review" is used as a general concept, the actual object type is `review_list`

## Workflows

### Object List Creation Workflow
1. User imports a CX2 file or network from NDEx
2. System processes the file and creates an object_list
3. System creates objects for each node/edge in the network
4. User can view the object_list in the browser

### Review Workflow
1. User opens an object_list in the reviewer interface
2. User navigates through objects and scores each one
3. System saves the review_list data automatically
4. User can submit and export the completed review_list when finished

### Object Management Workflow
1. User searches or browses objects in the browser interface
2. User can view details, relationships, and properties
3. User can edit properties or delete objects
4. User can execute custom SQL queries

## API Usage Examples

### Creating an Object

```javascript
// POST to /objects/object_list/create
const response = await fetch('/objects/object_list/create', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'My Object List',
    description: 'A list of objects to review',
    object_ids: ['123', '456', '789'],
    _criteria: [
      {
        label: 'Quality',
        property_name: 'quality_score',
        input_type: 'menu',
        display_type: 'text',
        data_type: 'str',
        options: ['High', 'Medium', 'Low']
      }
    ]
  })
});
```

### Querying Objects with SQL

```javascript
// POST to /query_knowledge_graph_database
const response = await fetch('/query_knowledge_graph_database', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    sql: "SELECT * FROM nodes WHERE object_type = 'object_list' LIMIT 10"
  })
});
