# Deckard Flexible Object Model

## Overview

Deckard has evolved from a system with rigid object schemas to one that uses a flexible object model. This flexible approach allows for storing and retrieving objects without being constrained by a predefined schema, making the system more adaptable.

## Core Database Structure

The system uses a single table to store all objects:

```sql
CREATE TABLE IF NOT EXISTS nodes (
    object_id TEXT PRIMARY KEY,
    properties TEXT,  -- JSON blob containing all object properties
    object_type TEXT
)
```

This design allows for:
- Storing any type of object
- Adding new properties without schema migrations
- Flexible querying using SQLite's JSON functions

## Key Object Types

While the system supports objects of any type, several types have special significance in the active codebase:

### 1. object_list

An `object_list` is a collection of objects that can be reviewed as a group.

**Key Properties:**
- `name`: Display name for the list
- `description`: Description of the list (optional)
- `object_ids`: Array of object IDs included in the list
- `_criteria`: Array of scoring criteria definitions
- `_order`: Object defining property display order (optional)

**Example _criteria Format:**
```json
"_criteria": [
  {
    "label": "Comments",
    "property_name": "comments",
    "input_type": "textarea",
    "display_type": "text",
    "data_type": "str"
  },
  {
    "label": "Evaluation",
    "property_name": "evaluation",
    "input_type": "menu",
    "display_type": "text",
    "data_type": "str",
    "options": ["great!", "good.", "ok.", "needs work.", "unacceptable"]
  }
]
```

**Example _order Format:**
```json
"_order": {
  "bel_expression": 1,
  "evidence": 2,
  "test": 3
}
```

### 2. review_list

A `review_list` represents the scores and feedback given to objects in an object_list.

**Key Properties:**
- `object_list_id`: ID of the reviewed object list
- `object_ids`: Array of object IDs being reviewed (copied from the object_list)
- `reviewer`: Name of the reviewer
- `scores`: Array of score objects for each item
- `_criteria`: Array of scoring criteria (copied from the object_list)
- `status`: Status of the review (e.g., "open", "submitted")
- `submit_date`: Timestamp when the review was submitted (if completed)

**Example scores Format:**
```json
"scores": [
  {
    "reviewed_object": "object_123",
    "scores": {
      "comments": "This appears to be a well-supported interaction.",
      "evaluation": "good."
    }
  },
  {
    "reviewed_object": "object_456",
    "scores": {
      "comments": "Insufficient evidence provided.",
      "evaluation": "needs work."
    }
  }
]
```

**Note:** While "review" is used as a general concept in documentation, the actual object type is `review_list`. This naming convention reflects that reviews in the system always operate on collections of objects, and using separate review objects for each item would unnecessarily clutter the database.

## Creating and Managing Objects

### Creating Objects

The system provides a simple API for creating objects:

```
POST /objects/{object_type}/create
```

Body:
```json
{
  "name": "Object Name",
  "description": "Object description",
  ... other properties ...
}
```

For object types not defined in `object_specifications`, the API simply stores all provided properties without validation.

### Updating Objects

```
POST /objects/{object_type}/{object_id}/edit
```

Body:
```json
{
  "name": "Updated Name",
  ... other properties to update ...
}
```

The update process merges the new properties with existing ones rather than replacing the entire object.

### Querying Objects

The system supports SQL queries through the Knowledge Graph API:

```
POST /query_knowledge_graph_database
```

Body:
```json
{
  "sql": "SELECT * FROM nodes WHERE object_type = 'object_list' LIMIT 10"
}
```

This allows for powerful queries using SQLite's JSON extraction functions:

```sql
SELECT * FROM nodes 
WHERE object_type = 'object_list' 
AND json_extract(properties, '$.name') LIKE '%Network%'
```

## Working with Object Lists and Reviews

### Creating an Object List

1. Import a CX2 file or network from NDEx
2. The system processes the network and creates individual objects for each node/edge
3. An object_list is created with references to these objects
4. Scoring criteria can be defined in the `_criteria` property

### Creating a Review

1. Navigate to an object_list in the browser
2. Click "Review Object List" to open the reviewer interface
3. Step through objects and provide scores based on criteria
4. The system saves a review object with references to the object_list and scores

### Retrieving Review Results

Reviews can be exported or queried to analyze results:

```sql
SELECT r.properties
FROM nodes r
JOIN nodes ol ON json_extract(r.properties, '$.object_list_id') = ol.object_id
WHERE r.object_type = 'review'
AND ol.object_type = 'object_list'
AND json_extract(ol.properties, '$.name') = 'My Network Review'
```

## Benefits of the Flexible Model

1. **Extensibility**: New object types can be added without schema changes
2. **Evolvability**: Existing object types can gain new properties over time
3. **Simplicity**: One table for all objects simplifies backup, migration, and code
4. **Query Power**: SQLite JSON functions provide rich query capabilities
5. **Integration**: Easy to integrate with external systems via JSON
