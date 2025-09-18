# Testing Port 3000 Change

This document provides steps to test the Deckard system after changing the port from 8000 to 3000.

## Prerequisites

- Conda environment: `ae2` (currently active)
- Port 3000 availability on your machine

## Testing Procedure

### 1. Start the FastAPI Server

```bash
# Make sure you're in the project root directory
python main.py
```

You should see output indicating the server is running on port 3000, similar to:
```
INFO:     Started server process [xxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:3000 (Press CTRL+C to quit)
```

### 2. Test Basic API Endpoints

Open a new terminal window (leave the server running) and run:

```bash
# Test basic endpoint
curl http://localhost:3000/browser

# Test object endpoint
curl http://localhost:3000/objects/object_list

# Test knowledge graph endpoint
curl -X POST http://localhost:3000/query_knowledge_graph_database \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT * FROM nodes LIMIT 1"}'
```

### 3. Test Web Interfaces

Open a web browser and verify these URLs work:

- Browser interface: http://localhost:3000/browser
- Reviewer interface: http://localhost:3000/reviewer
- NDEx import interface: http://localhost:3000/ndex-import

### 4. Test MCP Server (in a new terminal)

```bash
# Start the MCP server
python mcp-deckhard.py
```

Verify in the logs that it connects to http://localhost:3000

### 5. Verify Documentation

Check that these files correctly reference port 3000 instead of 8000:
- system_documentation.md
- updated_README.md
- Any other relevant docs

## Troubleshooting

If the server fails to start on port 3000:

1. Check if another process is using port 3000:
   ```bash
   lsof -i :3000
   ```

2. If port 3000 is in use, you can temporarily change to a different port in main.py

3. Verify the conda environment has all required packages:
   ```bash
   conda list -n ae2 | grep -E "fastapi|uvicorn|httpx|fastmcp"
   ```

## Next Steps

If all tests pass, proceed with Phase 3 of the cleanup plan: incremental removal of legacy code.
