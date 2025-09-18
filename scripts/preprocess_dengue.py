#!/usr/bin/env python3

import os
import sys
import argparse
import numpy as np
from datetime import datetime
from ndex2.cx2 import CX2Network
from ndex2.cx2 import RawCX2NetworkFactory
import ndex2.client as nc2

def load_ndex_credentials():
    """Load NDEx credentials from environment variables"""
    username = os.environ.get("NDEX_USERNAME")
    password = os.environ.get("NDEX_PASSWORD")
    return username, password

def load_from_ndex(uuid):
    """
    Load a CX2 network from NDEx
    
    Args:
        uuid: NDEx network UUID
        
    Returns:
        Tuple of (CX2Network, network_name)
    """
    username, password = load_ndex_credentials()
    
    if not username or not password:
        raise EnvironmentError("NDEX_USERNAME and NDEX_PASSWORD environment variables must be set")
        
    client = nc2.Ndex2(
        "http://public.ndexbio.org",
        username=username,
        password=password
    )
    
    # Download from NDEx
    response = client.get_network_as_cx2_stream(uuid)
    factory = RawCX2NetworkFactory()
    cx2_network = factory.get_cx2network(response.json())
    
    # Get network name
    network_name = cx2_network.get_name()
    if not network_name:
        # Fallback to network attributes
        network_attrs = cx2_network.get_network_attributes()
        network_name = network_attrs.get('name', f"network-{uuid[:8]}")
    
    return cx2_network, network_name

def upload_to_ndex(cx2_network, network_name):
    """
    Upload a CX2 network to NDEx
    
    Args:
        cx2_network: CX2Network object
        network_name: Name for the network
        
    Returns:
        UUID of the uploaded network
    """
    username, password = load_ndex_credentials()
    
    if not username or not password:
        raise EnvironmentError("NDEX_USERNAME and NDEX_PASSWORD environment variables must be set")
        
    client = nc2.Ndex2(
        "http://public.ndexbio.org",
        username=username,
        password=password
    )
    
    # Update network name and timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cx2_network.set_name(f"{network_name} - Typed {timestamp}")
    cx2_network.add_network_attribute('description', f"Network with node types added based on Z-scores. Original network: {network_name}")
    
    # Convert to CX2 format
    cx2_data = cx2_network.to_cx2()
    
    # Upload to NDEx
    response = client.save_new_cx2_network(cx2_data)
    return response

def add_node_types(cx2_network):
    """
    Process the CX2 network to add node types based on Z-scores
    
    Args:
        cx2_network: CX2Network object
        
    Returns:
        Modified CX2Network object
    """
    # First, check if "type" is already declared in attribute declarations
    attr_declarations = cx2_network.get_attribute_declarations()
    if 'nodes' not in attr_declarations:
        attr_declarations['nodes'] = {}
    if 'type' not in attr_declarations['nodes']:
        attr_declarations['nodes']['type'] = {'d': 'string'}
        cx2_network.set_attribute_declarations(attr_declarations)
    
    # Collect Z-scores from nodes
    z_scores = []
    has_z_nodes = []
    
    # Check for nodes with Z-scores
    for node_id, node_attrs in cx2_network.get_nodes().items():
        # Extract attributes from 'v' if present
        if 'v' in node_attrs and isinstance(node_attrs['v'], dict):
            # Check for Average_Zscore field
            if 'Average_Zscore' in node_attrs['v']:
                z_score = node_attrs['v']['Average_Zscore']
                if isinstance(z_score, (int, float)):
                    z_scores.append(z_score)
                    has_z_nodes.append(node_id)
    
    if not z_scores:
        print("Warning: No nodes with Z-scores found. Check node attribute names.")
        return cx2_network
    
    # Calculate Z-score thresholds (dividing into thirds)
    z_scores = np.array(z_scores)
    thresholds = [
        np.percentile(z_scores, 33.33),
        np.percentile(z_scores, 66.67)
    ]
    
    print(f"Z-score thresholds: {thresholds}")
    
    # Process all nodes
    modified_count = 0
    for node_id, node_attrs in cx2_network.get_nodes().items():
        # Default type is undefined
        node_type = "undefined"
        
        # Extract attributes from 'v' if present
        v_attrs = {}
        if 'v' in node_attrs and isinstance(node_attrs['v'], dict):
            v_attrs = node_attrs['v']
        
        # Check for viral protein
        if 'viral_protein' in v_attrs and v_attrs['viral_protein'] == True:
            node_type = "viral"
        # Check for Z-score
        elif 'Average_Zscore' in v_attrs:
            z_score = v_attrs['Average_Zscore']
            if isinstance(z_score, (int, float)):
                if z_score >= thresholds[1]:
                    node_type = "high_z"
                elif z_score >= thresholds[0]:
                    node_type = "med_z"
                else:
                    node_type = "low_z"
        
        # Update node type
        if node_type != "undefined":
            modified_count += 1
            # If v_attrs exists, update it
            if 'v' in node_attrs:
                node_attrs['v']['type'] = node_type
            # Otherwise create it
            else:
                node_attrs['v'] = {'type': node_type}
    
    print(f"Modified {modified_count} nodes with type information")
    return cx2_network

def analyze_network(cx2_network):
    """
    Analyze the network to get Z-score statistics and node type counts
    
    Args:
        cx2_network: CX2Network object
    """
    # Count nodes by type
    type_counts = {
        'viral': 0,
        'high_z': 0,
        'med_z': 0,
        'low_z': 0,
        'undefined': 0
    }
    
    z_scores = []
    viral_count = 0
    
    # Analyze nodes
    for node_id, node_attrs in cx2_network.get_nodes().items():
        # Extract attributes from 'v' if present
        v_attrs = {}
        if 'v' in node_attrs and isinstance(node_attrs['v'], dict):
            v_attrs = node_attrs['v']
        
        # Count by type
        node_type = v_attrs.get('type', 'undefined')
        if node_type in type_counts:
            type_counts[node_type] += 1
        else:
            type_counts['undefined'] += 1
        
        # Count viral nodes
        if 'viral_protein' in v_attrs and v_attrs['viral_protein'] == True:
            viral_count += 1
        
        # Collect Z-scores
        if 'Average_Zscore' in v_attrs:
            z_score = v_attrs['Average_Zscore']
            if isinstance(z_score, (int, float)):
                z_scores.append(z_score)
    
    # Print statistics
    print("\nNetwork Statistics:")
    print("-------------------")
    print(f"Total nodes: {len(cx2_network.get_nodes())}")
    print(f"Total edges: {len(cx2_network.get_edges())}")
    print(f"Viral nodes: {viral_count}")
    print(f"Nodes with Z-scores: {len(z_scores)}")
    
    print("\nNode types:")
    for node_type, count in type_counts.items():
        print(f"  {node_type}: {count}")
    
    if z_scores:
        print("\nZ-score statistics:")
        print(f"  Min: {min(z_scores):.4f}")
        print(f"  Max: {max(z_scores):.4f}")
        print(f"  Mean: {np.mean(z_scores):.4f}")
        print(f"  Median: {np.median(z_scores):.4f}")
        print(f"  Std Dev: {np.std(z_scores):.4f}")
        print(f"  33% threshold: {np.percentile(z_scores, 33.33):.4f}")
        print(f"  67% threshold: {np.percentile(z_scores, 66.67):.4f}")

def main():
    parser = argparse.ArgumentParser(description='Add node types to an NDEx network based on Z-scores')
    
    parser.add_argument('--uuid', type=str, default="0fb9bf21-fa25-11ef-b81d-005056ae3c32", help='NDEx network UUID')
    parser.add_argument('--analyze-only', action='store_true', help='Only analyze the network, don\'t modify')
    parser.add_argument('--dont-upload', action='store_true', help='Don\'t upload the modified network to NDEx')
    
    args = parser.parse_args()
    
    # Load network from NDEx
    print(f"Loading network {args.uuid} from NDEx...")
    cx2_network, network_name = load_from_ndex(args.uuid)
    print(f"Loaded network '{network_name}' with {len(cx2_network.get_nodes())} nodes and {len(cx2_network.get_edges())} edges")
    
    # Analyze the network
    print("\nAnalyzing original network:")
    analyze_network(cx2_network)
    
    if args.analyze_only:
        return
    
    # Add node types based on Z-scores
    print("\nAdding node types based on Z-scores...")
    modified_network = add_node_types(cx2_network)
    
    # Analyze the modified network
    print("\nAnalyzing modified network:")
    analyze_network(modified_network)
    
    # Upload to NDEx if requested
    if not args.dont_upload:
        print("\nUploading modified network to NDEx...")
        uuid = upload_to_ndex(modified_network, network_name)
        print(f"Upload successful. New network UUID: {uuid}")
    
if __name__ == "__main__":
    main()
