#!/usr/bin/env python3

"""
Dengue-specific hypothesis generation module.
"""

import sys
import os
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
import networkx as nx
from ndex2.cx2 import CX2Network, RawCX2NetworkFactory

# Add parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.network_utils import cx2_to_networkx
from analysis.hypothesis_gen import (
    LLMWrapper,
    analyze_network,
    generate_hypotheses,
    create_hypothesis_network
)

# Import app utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app.ndex_utils import get_ndex_client, get_complete_network
from app.config import load_api_keys

def extract_uuid(input_str):
    """Extract just the UUID from a string that might be a full NDEx URL"""
    # Match pattern for UUIDs in NDEx URLs
    uuid_pattern = r'(?:https?://(?:www\.)?ndexbio\.org/(?:v3/)?networks/)?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
    match = re.search(uuid_pattern, input_str)
    if match:
        return match.group(1)
    return input_str  # Return original if no UUID pattern found

def create_llm_wrapper_with_api_keys(
    llm_type: str,
    model_name: str,
    max_tokens: int = 4000,
    seed: int = 42,
    temperature: float = 0.7
) -> LLMWrapper:
    """
    Create an LLM wrapper with API keys from config
    
    Args:
        llm_type: Type of LLM (OpenAI, Anthropic, Groq, GoogleAI, LocalModel)
        model_name: Name of the model to use
        max_tokens: Maximum number of tokens for LLM response
        seed: Random seed for reproducibility
        temperature: Temperature for LLM generation
        
    Returns:
        LLMWrapper instance with API keys
    """
    # Load API keys from config
    openai_key, groq_key, anthropic_key, google_key = load_api_keys()
    
    # Create API keys dictionary
    api_keys = {
        'OpenAI': openai_key,
        'Anthropic': anthropic_key,
        'Groq': groq_key,
        'GoogleAI': google_key
    }
    
    # Create and return LLM wrapper
    return LLMWrapper(
        llm_type=llm_type,
        model_name=model_name,
        api_keys=api_keys,
        max_tokens=max_tokens,
        seed=seed,
        temperature=temperature
    )

def generate_dengue_hypotheses(
    ndex_uuids: List[str],
    output_dir: str = '.',
    n_hypotheses: int = 2,
    llm_type: str = 'Anthropic',
    model_name: str = 'claude-3-7-sonnet-20250219',
    max_tokens: int = 4000, 
    temperature: float = 0.7,
    seed: int = 42,
    upload_network: bool = True
) -> List[Dict[str, Any]]:
    """
    Generate hypotheses for dengue viral protein networks
    
    Args:
        ndex_uuids: List of NDEx UUIDs for propagation networks
        output_dir: Output directory for results
        n_hypotheses: Number of hypotheses per viral protein
        llm_type: Type of LLM to use
        model_name: Name of the model to use
        max_tokens: Maximum tokens for LLM response
        temperature: Temperature for LLM generation
        seed: Random seed for reproducibility
        upload_network: Whether to upload the hypothesis network to NDEx
        
    Returns:
        List of all generated hypotheses
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Clean UUIDs by extracting them from any URLs
    uuids = [extract_uuid(uuid) for uuid in ndex_uuids]
    print(f"Using UUIDs: {uuids}")
    
    # Create timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create LLM wrapper with API keys
    llm_wrapper = create_llm_wrapper_with_api_keys(
        llm_type=llm_type,
        model_name=model_name,
        max_tokens=max_tokens,
        seed=seed,
        temperature=temperature
    )
    
    # Store all hypotheses from all viral proteins
    all_hypotheses = []
    all_network_stats = {}
    
    # Get NDEx client
    client = get_ndex_client()
    
    # Process each viral protein network
    for i, uuid in enumerate(uuids):
        print(f"\nProcessing network {i+1}/{len(uuids)}: {uuid}")
        
        try:
            # Get network as CX2
            response = client.get_network_as_cx2_stream(uuid)
            factory = RawCX2NetworkFactory()
            cx2_network = factory.get_cx2network(response.json())
            
            # Get network name and attributes
            network_name = cx2_network.get_name()
            network_attrs = cx2_network.get_network_attributes()
            if not network_name:
                # Fallback to network attributes
                network_name = network_attrs.get('name', f"network-{uuid[:8]}")
            
            print(f"Loaded network '{network_name}'")
            
            # Convert to NetworkX for analysis
            G = cx2_to_networkx(cx2_network)
            print(f"Converted to NetworkX graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
            
            # Adapt network attributes for dengue-specific context
            # Check if this is a viral protein propagation network
            viral_protein_name = network_attrs.get('viral_protein_name', None)
            viral_protein_id = network_attrs.get('viral_protein_id', None)
            
            if viral_protein_name and viral_protein_id:
                # This is a viral protein network, update attributes
                network_attrs['source_node_name'] = viral_protein_name
                network_attrs['source_node_id'] = viral_protein_id
            
            # Analyze network
            print("Analyzing network...")
            network_stats = analyze_network(G, network_attrs)
            
            # Store network stats for later reference
            if 'source_node' in network_stats and network_stats['source_node']['name']:
                viral_protein = network_stats['source_node']['name']
                all_network_stats[viral_protein] = network_stats
            else:
                print("Warning: No source node (viral protein) found in network")
                continue
            
            # Generate hypotheses for this viral protein with dengue-specific context
            print(f"Generating {n_hypotheses} hypotheses for {viral_protein}...")
            
            # Custom context for dengue virus
            dengue_context = """
You are a virology and systems biology expert specializing in dengue virus research. 
Your task is to generate scientifically plausible, falsifiable hypotheses based on protein interaction network analysis and experimental data.
Each hypothesis should be formally defined with null (H0) and alternative (H1) hypotheses.
Focus on molecular mechanisms of dengue virus pathogenesis and host-pathogen interactions.
Return your response in valid JSON format only.
"""
            
            hypotheses = generate_hypotheses(
                network_stats, 
                llm_wrapper, 
                n_hypotheses,
                domain_name="dengue virus",
                system_context=dengue_context
            )
            
            # Add hypotheses to the overall list
            all_hypotheses.extend(hypotheses)
            
            # Save individual protein hypotheses to file
            protein_filename = f"hypotheses_{viral_protein}_{timestamp}.json"
            protein_filepath = os.path.join(output_dir, protein_filename.replace(" ", "_"))
            
            with open(protein_filepath, 'w') as f:
                json.dump(hypotheses, f, indent=2)
            
            print(f"Saved {len(hypotheses)} hypotheses for {viral_protein} to {protein_filepath}")
            
        except Exception as e:
            print(f"Error processing network {uuid}: {str(e)}")
    
    # Save all hypotheses to file
    all_hypotheses_filename = f"all_hypotheses_{timestamp}.json"
    all_hypotheses_filepath = os.path.join(output_dir, all_hypotheses_filename)
    
    with open(all_hypotheses_filepath, 'w') as f:
        json.dump(all_hypotheses, f, indent=2)
    
    print(f"\nSaved {len(all_hypotheses)} total hypotheses to {all_hypotheses_filepath}")
    
    # Create hypothesis network
    if all_hypotheses:
        print("\nCreating hypothesis network...")
        network_name = f"Dengue Virus Protein Hypotheses - {timestamp}"
        hypothesis_network = create_hypothesis_network(all_hypotheses, network_name)
        
        # Save network to file
        network_filename = f"hypothesis_network_{timestamp}.cx2"
        network_filepath = os.path.join(output_dir, network_filename)
        with open(network_filepath, 'w') as f:
            json.dump(hypothesis_network.to_cx2(), f, indent=2)
        print(f"Saved hypothesis network to {network_filepath}")
        
        # Upload to NDEx if requested
        if upload_network:
            print("Uploading hypothesis network to NDEx...")
            client = get_ndex_client()
            cx2_data = hypothesis_network.to_cx2()
            uuid = client.save_new_cx2_network(cx2_data)
            print(f"Upload successful. Network UUID: {uuid}")
            
            # Save UUID to file
            uuid_file = os.path.join(output_dir, f"hypothesis_network_uuid_{timestamp}.txt")
            with open(uuid_file, 'w') as f:
                f.write(uuid)
            print(f"Saved network UUID to {uuid_file}")
    else:
        print("No hypotheses were generated, skipping network creation")
    
    # Display summary of generated hypotheses
    print("\nGenerated Hypotheses Summary:")
    for viral_protein, stats in all_network_stats.items():
        protein_hypotheses = [h for h in all_hypotheses if h['source_node'] == viral_protein]
        print(f"\n{viral_protein}: {len(protein_hypotheses)} hypotheses")
        
        for h in protein_hypotheses:
            print(f"  [{h['id']}] {h['title']} (Confidence: {h['confidence']}/5)")
    
    print(f"\nTotal hypotheses: {len(all_hypotheses)}")
    
    return all_hypotheses

if __name__ == "__main__":
    # This module is not meant to be run directly
    print("This module provides dengue hypothesis generation functions for use in generate_hypotheses.py")
