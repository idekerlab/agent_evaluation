"""
NDEx Utilities Module

This module provides functions for interacting with NDEx networks
using the ndex2 Python client.
"""

import os
import logging
import json
from ndex2.cx2 import CX2Network
from ndex2.cx2 import RawCX2NetworkFactory
import ndex2.client as nc2

# Configure logging
logger = logging.getLogger(__name__)

def load_ndex_credentials():
    """
    Load NDEx credentials from environment variables.
    For public networks, credentials are not required.
    
    Returns:
        Tuple of (username, password)
    """
    username = os.environ.get("NDEX_USERNAME", "")
    password = os.environ.get("NDEX_PASSWORD", "")
    return username, password

def get_ndex_client():
    """
    Create an NDEx client instance.
    
    Returns:
        ndex2.client.Ndex2 instance
    """
    username, password = load_ndex_credentials()
    
    # Public endpoint, no auth needed for public networks
    if not username or not password:
        logger.info("Using NDEx client without authentication (public access only)")
        client = nc2.Ndex2("http://public.ndexbio.org")
    else:
        logger.info(f"Using NDEx client with authentication for user: {username}")
        client = nc2.Ndex2(
            "http://public.ndexbio.org",
            username=username,
            password=password
        )
    
    return client

def get_network_summary(uuid):
    """
    Get network summary from NDEx
    
    Args:
        uuid: NDEx network UUID
        
    Returns:
        Dictionary with network summary
    """
    try:
        client = get_ndex_client()
        
        # Get network summary
        logger.info(f"Fetching network summary for UUID: {uuid}")
        summary = client.get_network_summary(uuid)
        
        # Return as dictionary
        return summary
    except Exception as e:
        logger.error(f"Error getting network summary: {str(e)}", exc_info=True)
        raise

def get_complete_network(uuid):
    """
    Get complete network from NDEx with nodes and edges
    
    Args:
        uuid: NDEx network UUID
        
    Returns:
        Dictionary with complete network data including nodes and edges
    """
    try:
        client = get_ndex_client()
        
        # Download from NDEx as CX2 stream
        logger.info(f"Fetching complete network for UUID: {uuid}")
        response = client.get_network_as_cx2_stream(uuid)
        
        # Parse CX2 network
        factory = RawCX2NetworkFactory()
        cx2_network = factory.get_cx2network(response.json())
        
        # Get network name
        network_attrs = cx2_network.get_network_attributes()
        network_name = cx2_network.get_name()
        if not network_name:
            # Fallback to network attributes
            network_name = network_attrs.get('name', f"network-{uuid[:8]}")
        network_description = network_attrs.get('description', "object_list imported from NDEx")
            
        # Convert to JSON-compatible dictionary
        nodes = []
        for node_id, node_attrs in cx2_network.get_nodes().items():
            # Create a node dict with ID
            node = {"id": node_id}
            
            # Add name if available
            if 'n' in node_attrs:
                node["name"] = node_attrs['n']
            
            # Add all other attributes from the 'v' dict
            if 'v' in node_attrs and isinstance(node_attrs['v'], dict):
                for key, value in node_attrs['v'].items():
                    node[key] = value
            
            nodes.append(node)
            
        # Get edges
        edges = []
        for edge_id, edge_attrs in cx2_network.get_edges().items():
            # Create an edge dict with ID and source/target
            edge = {
                "id": edge_id,
                "source": edge_attrs.get('s'),
                "target": edge_attrs.get('t')
            }
            
            # Add interaction type if available
            if 'i' in edge_attrs:
                edge["interaction"] = edge_attrs['i']
            
            # Add all other attributes from the 'v' dict
            if 'v' in edge_attrs and isinstance(edge_attrs['v'], dict):
                for key, value in edge_attrs['v'].items():
                    edge[key] = value
            
            edges.append(edge)
        
        # Combine into a single result dict
        result = {
            "name": network_name,
            "description": network_description,
            "nodeCount": len(nodes),
            "edgeCount": len(edges),
            "externalId": uuid,
            "nodes": nodes,
            "edges": edges,
        }
        
        # Add network properties
        properties = []
        for attr_name, attr_value in cx2_network.get_network_attributes().items():
            properties.append({
                "predicateString": attr_name,
                "value": attr_value
            })
        result["properties"] = properties
        
        return result
    except Exception as e:
        logger.error(f"Error getting complete network: {str(e)}", exc_info=True)
        raise
