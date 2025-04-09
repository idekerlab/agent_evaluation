import logging
import sqlite3
import json
from typing import Dict, List, Optional, Any, Union

from fastapi import APIRouter, Request, HTTPException, Body
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["knowledge_graph"])

class SQLQuery(BaseModel):
    sql: str

class Relationship(BaseModel):
    source_id: Optional[int] = None
    target_id: Optional[int] = None
    type: Optional[str] = None

@router.post("/query_knowledge_graph_database")
async def query_knowledge_graph_database(request: Request, query: SQLQuery):
    """Execute a SQL query against the knowledge graph database."""
    logger.info(f"Executing SQL query: {query.sql}")
    
    try:
        db = request.app.state.db
        with db._get_connection() as conn:
            # Execute the query
            cursor = conn.cursor()
            cursor.execute(query.sql)
            
            # Check if the query returned any results
            if cursor.description is None:
                # This was a non-SELECT query (like INSERT, UPDATE, etc.)
                conn.commit()
                return {"message": "Query executed successfully", "rowcount": cursor.rowcount}
            
            # Get column names
            columns = [description[0] for description in cursor.description]
            
            # Fetch all results
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            results = []
            for row in rows:
                result = {}
                for i, column in enumerate(columns):
                    result[column] = row[i]
                results.append(result)
            
            return results
    except sqlite3.Error as e:
        logger.error(f"SQL error: {e}")
        raise HTTPException(status_code=400, detail=f"SQL error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

@router.post("/get_relationships")
async def get_relationships(request: Request, relationship_filter: Optional[Dict[str, Any]] = None):
    """Get relationships with optional filters."""
    if relationship_filter is None:
        relationship_filter = {}
    
    logger.info(f"Getting relationships with filter: {relationship_filter}")
    
    # Try to extract source_id, target_id, and type from the filter
    source_id = relationship_filter.get("source_id")
    target_id = relationship_filter.get("target_id")
    rel_type = relationship_filter.get("type")
    
    try:
        # Since we're likely using the nodes table for both entities and relationships,
        # we'll query the nodes table and return any objects that match the filter
        db = request.app.state.db
        
        # We'll fake relationships for now by looking at list_of_object_ids properties
        # in objects that reference other objects
        with db._get_connection() as conn:
            cursor = conn.cursor()
            
            if source_id:
                # Find all objects that reference this ID
                cursor.execute("""
                    SELECT object_id, object_type, properties 
                    FROM nodes 
                    WHERE properties LIKE ?
                """, (f'%{source_id}%',))
                
                rows = cursor.fetchall()
                results = []
                
                for row in rows:
                    obj_id, obj_type, properties_json = row
                    try:
                        properties = json.loads(properties_json)
                        
                        # Look for properties that are lists of object IDs
                        for prop_name, prop_value in properties.items():
                            if isinstance(prop_value, list) and prop_value and source_id in prop_value:
                                results.append({
                                    "id": len(results) + 1,  # Fake ID
                                    "source_id": int(source_id),
                                    "target_id": obj_id,
                                    "type": f"referenced_by_{prop_name}"
                                })
                            elif prop_value == source_id:
                                results.append({
                                    "id": len(results) + 1,  # Fake ID
                                    "source_id": int(source_id),
                                    "target_id": obj_id,
                                    "type": f"referenced_by_{prop_name}"
                                })
                    except (json.JSONDecodeError, TypeError):
                        continue
                
                return results
            
            elif target_id:
                # Find all objects referenced by this ID
                cursor.execute("""
                    SELECT object_id, object_type, properties 
                    FROM nodes 
                    WHERE object_id = ?
                """, (target_id,))
                
                row = cursor.fetchone()
                if not row:
                    return []
                
                obj_id, obj_type, properties_json = row
                results = []
                
                try:
                    properties = json.loads(properties_json)
                    
                    # Look for properties that are lists of object IDs or single object IDs
                    for prop_name, prop_value in properties.items():
                        if isinstance(prop_value, list) and prop_value:
                            for ref_id in prop_value:
                                if isinstance(ref_id, str) and ref_id:
                                    results.append({
                                        "id": len(results) + 1,  # Fake ID
                                        "source_id": obj_id,
                                        "target_id": int(ref_id),
                                        "type": f"references_{prop_name}"
                                    })
                        elif isinstance(prop_value, str) and prop_value and prop_name.endswith('_id'):
                            results.append({
                                "id": len(results) + 1,  # Fake ID
                                "source_id": obj_id,
                                "target_id": int(prop_value),
                                "type": f"references_{prop_name}"
                            })
                except (json.JSONDecodeError, TypeError):
                    return []
                
                return results
            
            else:
                # Without a specific source or target, return an empty list
                return []
                
    except sqlite3.Error as e:
        logger.error(f"SQL error: {e}")
        raise HTTPException(status_code=400, detail=f"SQL error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

# Helper routes for debugging
@router.get("/tables")
async def list_tables(request: Request):
    """Get a list of all tables in the database."""
    try:
        db = request.app.state.db
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            return {"tables": tables}
    except Exception as e:
        logger.error(f"Error listing tables: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing tables: {e}")

@router.get("/describe/{table_name}")
async def describe_table(request: Request, table_name: str):
    """Get details about a specific table."""
    try:
        db = request.app.state.db
        with db._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Table {table_name} not found")
                
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [{
                "cid": row[0],
                "name": row[1],
                "type": row[2],
                "notnull": row[3],
                "default_value": row[4],
                "pk": row[5]
            } for row in cursor.fetchall()]
            
            # Get first few rows for preview
            try:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                sample_rows = []
                for row in cursor.fetchall():
                    sample_rows.append({columns[i]["name"]: row[i] for i in range(len(columns))})
            except:
                sample_rows = ["Error fetching sample rows"]
                
            return {
                "table_name": table_name,
                "columns": columns,
                "sample_rows": sample_rows
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error describing table: {e}")
        raise HTTPException(status_code=500, detail=f"Error describing table: {e}")
