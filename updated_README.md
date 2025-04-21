# Deckard

Deckard is a system for reviewing lists of objects in a database. It consists of both a user interface for reviewing objects and a backend service for managing and storing those objects.

## System Overview

Deckard consists of two main components:

1. **Deckard Review System**: A system for managing and reviewing lists of objects in a database, with:
   - Web-based browser interface for exploring and managing objects
   - Reviewer interface for scoring and evaluating objects
   - NDEx import functionality for importing network files
   - FastAPI backend for data management
   - MCP server for programmatic access

2. **Dengue Fever Analysis Project**: A separate project that uses Deckard for reviewing its output
   - Located in the `scripts/` directory
   - Creates CX2 network files and interacts with NDEx
   - Uses Deckard for reviewing generated networks

## Main Components

### Backend

- **FastAPI Service**: Runs on port 3000
- **SQLite Database**: Flexible schema for storing objects
- **MCP Server**: Provides programmatic access to Deckard

### Frontend

- **Browser Interface**: For managing and viewing objects
- **Reviewer Interface**: For scoring objects in an object list
- **NDEx Import Interface**: For importing CX2 networks

## Key Concepts

- **Object Lists**: Collections of objects that can be reviewed together
- **Review Lists**: Scores and evaluations for collections of objects in an object list
- **Flexible Object Model**: Objects are stored with a flexible schema, not rigid types

## Getting Started

### Prerequisites

- Python 3.11+
- Modern web browser

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/deckard.git
cd deckard

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# Start the server
python main.py
```

The application will be available at:
- Browser interface: http://localhost:3000/browser
- Reviewer interface: http://localhost:3000/reviewer
- NDEx import interface: http://localhost:3000/ndex-import

## Main Workflows

### Importing and Reviewing Networks

1. Import a CX2 file using the NDEx import interface
2. View the created object list in the browser interface
3. Review the objects using the reviewer interface
4. Export the review results

### Managing Objects

1. Browse objects in the browser interface
2. View object details, relationships, and properties
3. Edit properties or delete objects as needed
4. Execute custom SQL queries for advanced searches

## API Access

Deckard provides a REST API for programmatic access:

- Object management: `/objects/{object_type}/...`
- SQL queries: `/query_knowledge_graph_database`
- Relationship queries: `/get_relationships`

Additionally, the MCP server (`mcp-deckhard.py`) provides Model Context Protocol access for AI systems.

## System Documentation

For more detailed documentation:

- [System Documentation](./system_documentation.md): Overall system architecture
- [API Documentation](./api_documentation.md): REST API endpoints
- [Flexible Object Model](./flexible_object_model.md): How objects are stored and managed

## Repository Status

This repository is currently undergoing cleanup to remove legacy code while preserving active functionality. Key areas being addressed:

1. Removing rigid schema model definitions
2. Removing agent execution framework
3. Removing analysis & review frameworks
4. Standardizing on flexible object models

The Dengue Fever analysis code in the scripts directory is a separate project that will be maintained.

## License

[MIT License](LICENSE)
