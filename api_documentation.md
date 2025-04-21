# Deckard API Documentation

This document outlines the API endpoints provided by the Deckard system, focusing on those actively used by the frontend interfaces.

## Object Routes

### List Objects

```
GET /objects/{object_type}
```

**Description**: Returns a list of objects of the specified type.

**Parameters**:
- `object_type`: Type of objects to list (e.g., object_list, review)
- `limit` (optional): Maximum number of objects to return
- `properties_filter` (optional): JSON object with property filters

**Example Response**:
```json
{
  "object_type": "object_list",
  "objects": [
    {
      "object_id": "object_list_123",
      "properties": {
        "name": "Network Review 1",
        "description": "Review of protein interactions",
        "object_ids": ["obj1", "obj2", "obj3"],
        "_criteria": [...]
      }
    },
    ...
  ],
  "object_spec": {...},
  "total_count": 10
}
```

### Get Object Details

```
GET /objects/{object_type}/{object_id}
```

**Description**: Returns details of a specific object.

**Parameters**:
- `object_type`: Type of the object
- `object_id`: ID of the object to retrieve

**Example Response**:
```json
{
  "object_type": "object_list",
  "object": {
    "object_id": "object_list_123",
    "name": "Network Review 1",
    "description": "Review of protein interactions",
    "object_ids": ["obj1", "obj2", "obj3"],
    "_criteria": [...]
  },
  "object_spec": {...},
  "link_names": {...}
}
```

### Create Object

```
POST /objects/{object_type}/create
```

**Description**: Creates a new object of the specified type.

**Parameters**:
- `object_type`: Type of object to create

**Request Body**: JSON object with the properties of the new object

**Example Request**:
```json
{
  "name": "New Object List",
  "description": "A list of objects to review",
  "object_ids": ["obj1", "obj2", "obj3"],
  "_criteria": [...]
}
```

**Example Response**:
```json
{
  "object_id": "object_list_456",
  "name": "New Object List",
  "description": "A list of objects to review",
  "created": "04.14.2025 17:00:00",
  "object_ids": ["obj1", "obj2", "obj3"],
  "_criteria": [...]
}
```

### Update Object

```
POST /objects/{object_type}/{object_id}/edit
```

**Description**: Updates an existing object.

**Parameters**:
- `object_type`: Type of the object
- `object_id`: ID of the object to update

**Request Body**: JSON object with the properties to update

**Example Request**:
```json
{
  "name": "Updated Object List",
  "description": "Updated description"
}
```

**Response**: Redirects to the object details page

### Delete Object

```
DELETE /objects/{object_type}/{object_id}
```

**Description**: Deletes an object.

**Parameters**:
- `object_type`: Type of the object
- `object_id`: ID of the object to delete

**Example Response**:
```json
{
  "success": true,
  "message": "Object object_list_456 deleted successfully"
}
```

Alternative endpoint (used by forms):
```
POST /objects/{object_type}/{object_id}/delete
```

### Clone Object

```
GET /objects/{object_type}/{object_id}/clone
```

**Description**: Creates a copy of an existing object.

**Parameters**:
- `object_type`: Type of the object
- `object_id`: ID of the object to clone

**Example Response**:
```json
{
  "object_id": "object_list_789"
}
```

## Knowledge Graph Routes

### Execute SQL Query

```
POST /query_knowledge_graph_database
```

**Description**: Executes a SQL query against the database.

**Request Body**:
```json
{
  "sql": "SELECT * FROM nodes WHERE object_type = 'object_list' LIMIT 10"
}
```

**Example Response**:
```json
[
  {
    "object_id": "object_list_123",
    "object_type": "object_list",
    "properties": "{\"name\":\"Network Review 1\",\"description\":\"Review of protein interactions\",\"object_ids\":[\"obj1\",\"obj2\",\"obj3\"],\"_criteria\":[]}"
  },
  ...
]
```

### Get Relationships

```
POST /get_relationships
```

**Description**: Gets relationships between objects.

**Request Body**:
```json
{
  "source_id": "obj1"
}
```
OR
```json
{
  "target_id": "obj1"
}
```

**Example Response**:
```json
[
  {
    "id": 1,
    "source_id": "obj1",
    "target_id": "object_list_123",
    "type": "referenced_by_object_ids"
  },
  ...
]
```

## NDEx Integration

### NDEx Proxy

```
GET /ndex-proxy/{path}
```

**Description**: Proxies requests to the NDEx API.

**Parameters**:
- `path`: Path to forward to the NDEx API

**Example**:
```
GET /ndex-proxy/network/search?start=0&size=10&query=dengue
```

### Get NDEx Network

```
GET /ndex-client/{uuid}
```

**Description**: Gets a network from NDEx.

**Parameters**:
- `uuid`: NDEx network UUID
- `summary_only` (optional): If true, only fetch summary information

**Example Response**:
```json
{
  "networkName": "Dengue Network",
  "nodes": [...],
  "edges": [...]
}
```

## Review API

### Create Review List

```
POST /objects/review_list/create
```

**Description**: Creates a new review list.

**Request Body**:
```json
{
  "object_list_id": "object_list_123",
  "object_ids": ["obj1", "obj2", "obj3"],
  "reviewer": "John Doe",
  "_criteria": [...],  // Copied from object_list
  "scores": [],
  "status": "open"
}
```

**Example Response**:
```json
{
  "object_id": "review_list_456",
  "object_list_id": "object_list_123",
  "object_ids": ["obj1", "obj2", "obj3"],
  "reviewer": "John Doe",
  "_criteria": [...],
  "scores": [],
  "status": "open",
  "created": "04.14.2025 17:00:00"
}
```

### Update Review List

```
POST /objects/review_list/{review_list_id}/edit
```

**Description**: Updates an existing review list.

**Parameters**:
- `review_list_id`: ID of the review list to update

**Request Body**:
```json
{
  "scores": [
    {
      "reviewed_object": "obj1",
      "scores": {
        "comments": "Updated comment",
        "evaluation": "great!"
      }
    },
    ...
  ],
  "status": "submitted",
  "submit_date": "04.14.2025 17:30:00"
}
```

**Example Response**:
```json
{
  "success": true
}
```

## UI Routes

### Browser Interface

```
GET /browser
```

**Description**: Serves the main browser interface.

### Reviewer Interface

```
GET /reviewer
```

**Description**: Serves the reviewer interface.

**Query Parameters**:
- `object_list_id` (optional): ID of the object list to review

### NDEx Import Interface

```
GET /ndex-import
```

**Description**: Serves the NDEx import interface.

## Debugging Routes

### Debug Paths

```
GET /debug/paths
```

**Description**: Returns information about file paths and static files.

### Test NDEx Connection

```
GET /test-ndex/{uuid}
```

**Description**: Tests connection to NDEx by fetching a network summary.

**Parameters**:
- `uuid`: NDEx network UUID

## Notes on Usage

1. **Browser Interface** primarily uses:
   - `GET /objects/{object_type}` to list objects
   - `GET /objects/{object_type}/{object_id}` to view object details
   - `POST /query_knowledge_graph_database` for SQL queries
   - `POST /get_relationships` to view object relationships
   - `DELETE /objects/{object_type}/{object_id}` to delete objects

2. **Reviewer Interface** primarily uses:
   - `GET /objects/object_list/{object_id}` to fetch the object list
   - `GET /objects/objects/{object_id}` to fetch individual objects
   - `POST /objects/review/create` to create a new review
   - `POST /objects/review/{review_id}/edit` to update review scores

3. **NDEx Import Interface** primarily uses:
   - `GET /ndex-proxy/{path}` and `GET /ndex-client/{uuid}` to communicate with NDEx
   - `POST /objects/{object_type}/create` to create object lists and objects

## Legacy Endpoints

The following endpoints appear to be related to legacy functionality and are not actively used by the current frontend interfaces:

- `POST /{agent_id}/start_run` - Agent execution
- `GET /agent_task/{task_id}` - Agent task status
- `POST /{agent_id}/run` - Synchronous agent execution
- `POST /objects/{object_type}/{object_id}/execute` - Execute analysis or review plans
