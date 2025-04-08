#!/usr/bin/env python3

import os
import sys
import argparse
import json
import time
import re
from datetime import datetime
import networkx as nx
import ndex2.client as nc2
from ndex2.cx2 import CX2Network
from ndex2.cx2 import RawCX2NetworkFactory
from typing import List, Dict, Any, Tuple, Set
import random
import math

# Add the parent directory to the path so we can import the models/llm.py module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.llm import LLM

def extract_uuid(input_str):
    """Extract just the UUID from a string that might be a full NDEx URL"""
    # Match pattern for UUIDs in NDEx URLs
    uuid_pattern = r'(?:https?://(?:www\.)?ndexbio\.org/(?:v3/)?networks/)?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
    match = re.search(uuid_pattern, input_str)
    if match:
        return match.group(1)
    return input_str  # Return original if no UUID pattern found

class LLMWrapper:
    """
    Simplified wrapper around the LLM class that doesn't require database operations.
    """
    def __init__(self, llm_type, model_name, max_tokens=2048, seed=42, temperature=0.7):
        """
        Initialize the LLM wrapper with the given parameters.
        
        Args:
            llm_type: Type of LLM (OpenAI, Anthropic, Groq, GoogleAI, LocalModel)
            model_name: Name of the model to use
            max_tokens: Maximum number of tokens to generate
            seed: Random seed for reproducibility
            temperature: Temperature for generation
        """
        self.llm = LLM(
            type=llm_type,
            model_name=model_name,
            max_tokens=max_tokens,
            seed=seed,
            temperature=temperature
        )
    
    def query(self, context, prompt):
        """
        Query the LLM with the given context and prompt.
        
        Args:
            context: System context/instructions
            prompt: User query/prompt
            
        Returns:
            The model's response
        """
        return self.llm.query(context, prompt)


def load_ndex_credentials() -> Tuple[str, str]:
    """Load NDEx credentials from environment variables"""
    username = os.environ.get("NDEX_ACCOUNT")
    password = os.environ.get("NDEX_PASSWORD")
    return username, password


def load_from_ndex(uuid: str) -> Tuple[nx.Graph, str, Dict[str, Any]]:
    """Load network from NDEx and convert to NetworkX
    
    Args:
        uuid: NDEx network UUID
        
    Returns:
        Tuple of (NetworkX graph, network name, network attributes)
    """
    # Extract just the UUID if a full URL was provided
    uuid = extract_uuid(uuid)
    
    username, password = load_ndex_credentials()
    
    if not username or not password:
        raise EnvironmentError("NDEX_ACCOUNT and NDEX_PASSWORD environment variables must be set")
        
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
    
    # Get network attributes
    network_attrs = cx2_network.get_network_attributes()
    
    # Convert CX2 to NetworkX
    G = cx2_to_networkx(cx2_network)
    
    return G, network_name, network_attrs


def cx2_to_networkx(cx2_network: CX2Network) -> nx.Graph:
    """Convert CX2 network to NetworkX graph
    
    Args:
        cx2_network: CX2 network object
        
    Returns:
        NetworkX graph
    """
    # Create empty graph
    G = nx.Graph()
    
    # Add network attributes
    G.graph['name'] = cx2_network.get_name()
    for attr_name, attr_value in cx2_network.get_network_attributes().items():
        G.graph[attr_name] = attr_value
    
    # Add nodes with attributes
    for node_id, node_attrs in cx2_network.get_nodes().items():
        # Use numeric ID as the node identifier in NetworkX
        node_id_str = str(node_id)
        
        # Get node name
        node_name = node_attrs.get('n', '')
        
        # Extract attributes from 'v' if present
        v_attrs = {}
        if 'v' in node_attrs and isinstance(node_attrs['v'], dict):
            v_attrs = node_attrs['v']
        
        # Prepare node attributes dict
        attrs = {
            'id': node_id,
            'name': node_name,
            'x': node_attrs.get('x', 0),
            'y': node_attrs.get('y', 0)
        }
        
        # Add all attributes from 'v'
        for k, v in v_attrs.items():
            attrs[k] = v
        
        # Add node to graph with all attributes
        G.add_node(node_id_str, **attrs)
    
    # Add edges with attributes
    for edge_id, edge_attrs in cx2_network.get_edges().items():
        source_id = str(edge_attrs.get('s'))
        target_id = str(edge_attrs.get('t'))
        
        # Extract attributes from 'v' if present
        v_attrs = {}
        if 'v' in edge_attrs and isinstance(edge_attrs['v'], dict):
            v_attrs = edge_attrs['v']
        
        # Prepare edge attributes
        attrs = {
            'id': edge_id
        }
        
        # Add all attributes from 'v'
        for k, v in v_attrs.items():
            attrs[k] = v
        
        # Add edge to graph
        if source_id in G and target_id in G:
            G.add_edge(source_id, target_id, **attrs)
    
    return G


def get_experimental_data_properties(G: nx.Graph) -> Dict[str, List[str]]:
    """
    Identify potential experimental data properties in the graph
    
    Args:
        G: NetworkX graph
        
    Returns:
        Dictionary of property groups and their property names
    """
    # Count occurrences of each property
    property_counts = {}
    numeric_properties = set()
    
    for node, attrs in G.nodes(data=True):
        for key, value in attrs.items():
            if key not in property_counts:
                property_counts[key] = 0
            property_counts[key] += 1
            
            # Check if property is numeric
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                numeric_properties.add(key)
    
    # Categorize properties
    common_properties = set()
    experimental_properties = set()
    
    # Define known metadata properties that are not experimental data
    metadata_properties = {
        'id', 'name', 'GeneSymbol', 'x', 'y', 'type', 'represents', 
        'viral_protein', 'propagation_weight', 'node_type'
    }
    
    # Threshold for common properties (present in >70% of nodes)
    threshold = 0.7 * G.number_of_nodes()
    
    for prop, count in property_counts.items():
        if prop in metadata_properties:
            continue
            
        if count > threshold:
            common_properties.add(prop)
            
        if prop in numeric_properties and prop not in metadata_properties:
            experimental_properties.add(prop)
    
    # Group properties
    property_groups = {
        'common': list(common_properties),
        'experimental': list(experimental_properties),
        'propagation': ['propagation_weight'] if 'propagation_weight' in property_counts else []
    }
    
    return property_groups


def analyze_network(G: nx.Graph, network_attrs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze a network to extract information for hypothesis generation
    
    Args:
        G: NetworkX graph
        network_attrs: Network attributes
        
    Returns:
        Dictionary with network analysis results
    """
    # Extract basic network statistics
    stats = {
        'name': G.graph.get('name', 'Unknown Network'),
        'node_count': G.number_of_nodes(),
        'edge_count': G.number_of_edges(),
        'avg_degree': sum(dict(G.degree()).values()) / G.number_of_nodes(),
    }
    
    # Find viral protein node (source of propagation)
    viral_protein_name = network_attrs.get('viral_protein_name', None)
    viral_protein_id = network_attrs.get('viral_protein_id', None)
    
    # If viral protein info isn't in network attributes, try to find it in the graph
    if not viral_protein_name or not viral_protein_id:
        for node, attrs in G.nodes(data=True):
            if attrs.get('viral_protein', False) or attrs.get('type', '') == 'viral':
                viral_protein_id = node
                viral_protein_name = attrs.get('name', attrs.get('GeneSymbol', node))
                break
    
    stats['viral_protein'] = {
        'name': viral_protein_name,
        'id': viral_protein_id
    }
    
    # Get nodes with propagation weights
    weighted_nodes = {}
    for node, attrs in G.nodes(data=True):
        if 'propagation_weight' in attrs:
            weight = attrs['propagation_weight']
            name = attrs.get('name', attrs.get('GeneSymbol', node))
            gene_symbol = attrs.get('GeneSymbol', name)
            
            # Extract all node attributes for experimental data
            node_data = {k: v for k, v in attrs.items() if k not in ['x', 'y', 'id']}
            
            weighted_nodes[node] = {
                'id': node,
                'name': name,
                'gene_symbol': gene_symbol,
                'weight': weight,
                'properties': node_data
            }
    
    # Sort nodes by propagation weight
    top_nodes = sorted(
        weighted_nodes.values(),
        key=lambda x: x['weight'],
        reverse=True
    )[:50]  # Get top 50 nodes by weight
    
    stats['top_nodes'] = top_nodes
    
    # Get node types distribution
    type_counts = {}
    for node, attrs in G.nodes(data=True):
        node_type = attrs.get('type', 'undefined')
        if node_type in type_counts:
            type_counts[node_type] += 1
        else:
            type_counts[node_type] = 1
    
    stats['type_distribution'] = type_counts
    
    # Identify experimental data properties
    stats['property_groups'] = get_experimental_data_properties(G)
    
    return stats


def get_top_nodes_with_experimental_data(network_stats: Dict[str, Any], max_nodes: int = 15) -> str:
    """
    Generate a formatted string of top nodes with their experimental data
    
    Args:
        network_stats: Dictionary with network analysis results
        max_nodes: Maximum number of nodes to include
        
    Returns:
        Formatted string for the prompt
    """
    top_nodes = network_stats['top_nodes'][:max_nodes]
    property_groups = network_stats['property_groups']
    
    # Select key experimental properties to display
    exp_properties = property_groups.get('experimental', [])
    
    # Limit to most informative properties if there are too many
    if len(exp_properties) > 5:
        exp_properties = exp_properties[:5]
    
    # Build the text
    lines = []
    
    for node in top_nodes:
        node_props = node['properties']
        name = node['name']
        gene_symbol = node.get('gene_symbol', '')
        weight = node['weight']
        
        # Include gene symbol if different from name
        node_name = name
        if gene_symbol and gene_symbol != name:
            node_name = f"{name} ({gene_symbol})"
            
        # Start with basic info
        line = f"- {node_name}: Weight: {weight:.4f}"
        
        # Add experimental data if available
        exp_data = []
        for prop in exp_properties:
            if prop in node_props:
                value = node_props[prop]
                if isinstance(value, float):
                    value = f"{value:.4f}"
                exp_data.append(f"{prop}: {value}")
        
        if exp_data:
            line += " | " + ", ".join(exp_data)
            
        lines.append(line)
    
    return "\n".join(lines)


def generate_hypothesis_prompt(network_stats: Dict[str, Any], n_hypotheses: int = 2) -> str:
    """
    Generate a prompt for hypothesis generation based on network analysis with experimental data
    
    Args:
        network_stats: Dictionary with network analysis results
        n_hypotheses: Number of hypotheses to generate
        
    Returns:
        Prompt for the LLM
    """
    # Extract information from network stats
    viral_protein = network_stats['viral_protein']['name'] or "Unknown viral protein"
    
    # Get formatted nodes with experimental data
    top_nodes_text = get_top_nodes_with_experimental_data(network_stats, max_nodes=15)
    
    # Get experimental properties for context
    property_groups = network_stats['property_groups']
    all_exp_properties = property_groups.get('experimental', [])
    exp_properties_text = ", ".join(all_exp_properties)
    
    # Create prompt
    prompt = f"""
Based on a dengue virus protein interaction network analysis for {viral_protein}, I need to generate {n_hypotheses} formal scientific hypotheses.

The dataset includes the following experimental data properties for proteins: {exp_properties_text}

The propagation analysis identified the following top human proteins with the highest propagation weights (most closely connected to the viral protein), along with their experimental data:

{top_nodes_text}

For each hypothesis, please:
1. Propose a specific testable hypothesis about how {viral_protein} might interact with these human proteins
2. Focus on relationships supported by the experimental data shown above
3. Format as formal null (H0) and alternative (H1) hypotheses
4. Explain the biological rationale based on the proteins and experimental data involved
5. Suggest specific experiments that could falsify the hypothesis

Format each hypothesis as a JSON object with the following fields:
- "title": A brief descriptive title for the hypothesis (5-10 words)
- "null_hypothesis": The formal null hypothesis statement (H0)
- "alternative_hypothesis": The formal alternative hypothesis statement (H1)
- "rationale": Biological reasoning behind the hypothesis, referencing the experimental data (3-5 sentences)
- "proteins_involved": List of key proteins mentioned in the hypothesis (gene symbols)
- "experimental_data_used": Brief description of which experimental data properties influenced this hypothesis
- "experimental_validation": 2-3 specific experiments that could falsify the hypothesis
- "confidence": A value from 1-5 indicating your confidence in this hypothesis (5 being highest)

Return ONLY a valid JSON array of hypothesis objects. Do not include any explanation or other text outside the JSON.
"""
    
    return prompt


def generate_hypotheses(network_stats: Dict[str, Any], llm_wrapper: LLMWrapper, n_hypotheses: int = 2) -> List[Dict[str, Any]]:
    """
    Generate hypotheses using LLM based on network analysis
    
    Args:
        network_stats: Dictionary with network analysis results
        llm_wrapper: LLMWrapper for LLM query
        n_hypotheses: Number of hypotheses to generate
        
    Returns:
        List of hypothesis dictionaries
    """
    # Generate prompt for the LLM
    prompt = generate_hypothesis_prompt(network_stats, n_hypotheses)
    
    # System context for the LLM
    context = """
You are a virology and systems biology expert specializing in dengue virus research. 
Your task is to generate scientifically plausible, falsifiable hypotheses based on protein interaction network analysis and experimental data.
Each hypothesis should be formally defined with null (H0) and alternative (H1) hypotheses.
Focus on mechanistic insights that are specifically supported by the experimental data provided.
Return your response in valid JSON format only.
"""
    
    # Query the LLM
    print(f"Generating {n_hypotheses} hypotheses with the LLM...")
    response = llm_wrapper.query(context, prompt)
    
    # Try to parse the response as JSON
    try:
        # The LLM might include additional text, so try to extract just the JSON part
        response = response.strip()
        
        # If response starts with backticks (markdown code block), remove them
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        
        # Parse JSON
        hypotheses = json.loads(response.strip())
        
        # Validate hypotheses
        for i, hypothesis in enumerate(hypotheses):
            # Ensure required fields exist
            required_fields = ['title', 'null_hypothesis', 'alternative_hypothesis', 'rationale', 
                              'proteins_involved', 'experimental_data_used', 'experimental_validation', 'confidence']
            for field in required_fields:
                if field not in hypothesis:
                    hypothesis[field] = f"Missing {field}"
            
            # Add hypothesis ID
            hypothesis['id'] = f"H{i+1}"
            
            # Add viral protein
            hypothesis['viral_protein'] = network_stats['viral_protein']['name']
        
        return hypotheses
    
    except json.JSONDecodeError as e:
        print(f"Error parsing LLM response as JSON: {e}")
        print("LLM response:")
        print(response)
        
        # Return a placeholder in case of failure
        return [{
            "id": "H1",
            "title": "Failed to generate valid hypothesis",
            "null_hypothesis": "Failed to generate valid null hypothesis",
            "alternative_hypothesis": "Failed to generate valid alternative hypothesis",
            "rationale": f"LLM response could not be parsed as JSON: {str(e)}",
            "proteins_involved": [],
            "experimental_data_used": "N/A",
            "experimental_validation": "N/A",
            "confidence": 0,
            "viral_protein": network_stats['viral_protein']['name']
        }]


def create_hypothesis_network(all_hypotheses: List[Dict[str, Any]]) -> CX2Network:
    """
    Create a CX2 network containing hypotheses as nodes
    
    Args:
        all_hypotheses: List of all hypothesis dictionaries from all viral proteins
        
    Returns:
        CX2Network object
    """
    # Create a new CX2 network
    cx2_network = CX2Network()
    
    # Set network attributes
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    network_name = f"Dengue Virus Protein Hypotheses - {timestamp}"
    
    cx2_network.set_name(network_name)
    cx2_network.add_network_attribute('description', 
                                      f"Hypotheses generated for dengue virus proteins")
    cx2_network.add_network_attribute('generation_timestamp', timestamp)
    
    # Add attribute declarations
    attr_declarations = {
        'nodes': {
            'name': {'d': 'string'},
            'title': {'d': 'string'},
            'null_hypothesis': {'d': 'string'},
            'alternative_hypothesis': {'d': 'string'},
            'rationale': {'d': 'string'},
            'proteins_involved': {'d': 'string'},
            'experimental_data_used': {'d': 'string'},
            'experimental_validation': {'d': 'string'},
            'confidence': {'d': 'integer'},
            'viral_protein': {'d': 'string'},
            'node_type': {'d': 'string'},
            'x': {'d': 'double'},
            'y': {'d': 'double'}
        }
    }
    cx2_network.set_attribute_declarations(attr_declarations)
    
    # Group hypotheses by viral protein
    hypotheses_by_protein = {}
    for hypothesis in all_hypotheses:
        viral_protein = hypothesis['viral_protein']
        if viral_protein not in hypotheses_by_protein:
            hypotheses_by_protein[viral_protein] = []
        hypotheses_by_protein[viral_protein].append(hypothesis)
    
    # Add hypotheses as nodes
    node_id = 1
    
    for viral_protein, hypotheses in hypotheses_by_protein.items():
        # Calculate positions for this group of hypotheses
        base_angle = random.uniform(0, 2 * math.pi)  # Random starting angle for this protein
        radius = 500
        
        for i, hypothesis in enumerate(hypotheses):
            # Calculate position in a circle section
            angle = base_angle + (2 * math.pi / len(hypotheses)) * i
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            
            # Format proteins involved as semicolon-separated list
            proteins_text = "; ".join(hypothesis['proteins_involved'])
            
            # Format experimental validation as semicolon-separated list if it's a list
            exp_validation = hypothesis['experimental_validation']
            if isinstance(exp_validation, list):
                exp_validation = "; ".join(exp_validation)
            
            # Create node name (will be displayed in visualization)
            node_name = f"{viral_protein} - {hypothesis['title']}"
            
            # Add node to network
            cx2_network.add_node(node_id, name=node_name)
            
            # Add node attributes
            cx2_network.add_node_attribute(node_id, 'title', hypothesis['title'])
            cx2_network.add_node_attribute(node_id, 'null_hypothesis', hypothesis['null_hypothesis'])
            cx2_network.add_node_attribute(node_id, 'alternative_hypothesis', hypothesis['alternative_hypothesis'])
            cx2_network.add_node_attribute(node_id, 'rationale', hypothesis['rationale'])
            cx2_network.add_node_attribute(node_id, 'proteins_involved', proteins_text)
            cx2_network.add_node_attribute(node_id, 'experimental_data_used', hypothesis['experimental_data_used'])
            cx2_network.add_node_attribute(node_id, 'experimental_validation', exp_validation)
            cx2_network.add_node_attribute(node_id, 'confidence', hypothesis['confidence'])
            cx2_network.add_node_attribute(node_id, 'viral_protein', viral_protein)
            cx2_network.add_node_attribute(node_id, 'node_type', 'hypothesis')
            cx2_network.add_node_attribute(node_id, 'x', x)
            cx2_network.add_node_attribute(node_id, 'y', y)
            
            node_id += 1
    
    return cx2_network


def upload_to_ndex(cx2_network: CX2Network) -> str:
    """
    Upload a CX2 network to NDEx
    
    Args:
        cx2_network: CX2Network object
        
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
    
    # Convert to CX2 format
    cx2_data = cx2_network.to_cx2()
    
    # Upload to NDEx
    response = client.save_new_cx2_network(cx2_data)
    return response


def main():
    parser = argparse.ArgumentParser(description='Generate hypotheses from viral protein propagation networks')
    
    # Required arguments
    parser.add_argument('--uuids', type=str, nargs='+', required=True, 
                       help='NDEx UUIDs of propagation networks')
    
    # Optional arguments
    parser.add_argument('--output-dir', type=str, default='.', help='Output directory for results')
    parser.add_argument('--n-hypotheses', type=int, default=2, help='Number of hypotheses per viral protein')
    parser.add_argument('--llm-type', type=str, default='Anthropic', 
                        choices=['OpenAI', 'Anthropic', 'Groq', 'GoogleAI', 'LocalModel'],
                        help='Type of LLM to use')
    parser.add_argument('--model-name', type=str, default='claude-3-7-sonnet-20250219', 
                       help='Name of the model to use')
    parser.add_argument('--max-tokens', type=int, default=4000, help='Maximum tokens for LLM response')
    parser.add_argument('--temperature', type=float, default=0.7, help='Temperature for LLM generation')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    # Clean UUIDs by extracting them from any URLs
    uuids = [extract_uuid(uuid) for uuid in args.uuids]
    print(f"Using UUIDs: {uuids}")
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Create timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create LLM wrapper
    llm_wrapper = LLMWrapper(
        llm_type=args.llm_type,
        model_name=args.model_name,
        max_tokens=args.max_tokens,
        seed=args.seed,
        temperature=args.temperature
    )
    
    # Store all hypotheses from all viral proteins
    all_hypotheses = []
    all_network_stats = {}
    
    # Process each viral protein network
    for i, uuid in enumerate(uuids):
        print(f"\nProcessing network {i+1}/{len(uuids)}: {uuid}")
        
        try:
            # Load network from NDEx
            G, network_name, network_attrs = load_from_ndex(uuid)
            print(f"Loaded network '{network_name}' with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
            
            # Analyze network
            print("Analyzing network...")
            network_stats = analyze_network(G, network_attrs)
            
            # Store network stats for later reference
            viral_protein = network_stats['viral_protein']['name']
            all_network_stats[viral_protein] = network_stats
            
            # Generate hypotheses for this viral protein
            print(f"Generating {args.n_hypotheses} hypotheses for {viral_protein}...")
            hypotheses = generate_hypotheses(network_stats, llm_wrapper, args.n_hypotheses)
            
            # Add hypotheses to the overall list
            all_hypotheses.extend(hypotheses)
            
            # Save individual protein hypotheses to file
            protein_filename = f"hypotheses_{viral_protein}_{timestamp}.json"
            protein_filepath = os.path.join(args.output_dir, protein_filename.replace(" ", "_"))
            
            with open(protein_filepath, 'w') as f:
                json.dump(hypotheses, f, indent=2)
            
            print(f"Saved {len(hypotheses)} hypotheses for {viral_protein} to {protein_filepath}")
            
        except Exception as e:
            print(f"Error processing network {uuid}: {str(e)}")
    
    # Save all hypotheses to file
    all_hypotheses_filename = f"all_hypotheses_{timestamp}.json"
    all_hypotheses_filepath = os.path.join(args.output_dir, all_hypotheses_filename)
    
    with open(all_hypotheses_filepath, 'w') as f:
        json.dump(all_hypotheses, f, indent=2)
    
    print(f"\nSaved {len(all_hypotheses)} total hypotheses to {all_hypotheses_filepath}")
    
    # Create hypothesis network
    print("\nCreating hypothesis network...")
    hypothesis_network = create_hypothesis_network(all_hypotheses)
    
    # Upload to NDEx
    print("Uploading hypothesis network to NDEx...")
    uuid = upload_to_ndex(hypothesis_network)
    print(f"Upload successful. Network UUID: {uuid}")
    
    # Save UUID to file
    uuid_file = os.path.join(args.output_dir, f"hypothesis_network_uuid_{timestamp}.txt")
    with open(uuid_file, 'w') as f:
        f.write(uuid)
    print(f"Saved network UUID to {uuid_file}")
    
    # Display summary of generated hypotheses
    print("\nGenerated Hypotheses Summary:")
    for viral_protein, stats in all_network_stats.items():
        protein_hypotheses = [h for h in all_hypotheses if h['viral_protein'] == viral_protein]
        print(f"\n{viral_protein}: {len(protein_hypotheses)} hypotheses")
        
        for h in protein_hypotheses:
            print(f"  [{h['id']}] {h['title']} (Confidence: {h['confidence']}/5)")
    
    print(f"\nTotal hypotheses: {len(all_hypotheses)}")
    print(f"Network UUID: {uuid}")
    
if __name__ == "__main__":
    main()
