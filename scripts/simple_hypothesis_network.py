#!/usr/bin/env python3

import os
import json
import random
import math
from datetime import datetime
from ndex2.cx2 import CX2Network

# List of UUIDs to process
uuids = [
    "faa974fc-ff5f-11ef-b81d-005056ae3c32",
    # Add more UUIDs here as needed
]

# Example hypotheses (since we can't load from NDEx)
example_hypotheses = [
    {
        "id": "H1",
        "title": "NS3 Inhibits STAT1 Phosphorylation",
        "null_hypothesis": "NS3 does not inhibit STAT1 phosphorylation during infection",
        "alternative_hypothesis": "NS3 inhibits STAT1 phosphorylation during infection",
        "rationale": "STAT1 shows significant propagation weight in the network analysis. This suggests NS3 may interfere with JAK-STAT signaling to suppress antiviral responses.",
        "proteins_involved": ["STAT1", "JAK1", "IFNAR1"],
        "experimental_data_used": "Phosphorylation levels and propagation weights",
        "experimental_validation": "Western blot for phospho-STAT1; Co-IP of NS3 with STAT1; siRNA knockdown of NS3",
        "confidence": 4,
        "viral_protein": "DENV2 NS3"
    },
    {
        "id": "H2",
        "title": "NS3 Upregulates A2M Expression",
        "null_hypothesis": "NS3 does not alter A2M expression in host cells",
        "alternative_hypothesis": "NS3 increases A2M expression in host cells",
        "rationale": "A2M showed the highest propagation weight, suggesting a strong connection with NS3. A2M is involved in immune regulation and could be manipulated by the virus.",
        "proteins_involved": ["A2M", "NS3"],
        "experimental_data_used": "Propagation weights and gene expression data",
        "experimental_validation": "qPCR for A2M expression; Reporter assay for A2M promoter; ChIP-seq",
        "confidence": 3,
        "viral_protein": "DENV2 NS3"
    }
]

def create_hypothesis_network(hypotheses):
    """
    Create a CX2 network containing hypotheses as nodes
    
    Args:
        hypotheses: List of hypothesis dictionaries
        
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
            'n': {'d': 'string'},
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
    for hypothesis in hypotheses:
        viral_protein = hypothesis['viral_protein']
        if viral_protein not in hypotheses_by_protein:
            hypotheses_by_protein[viral_protein] = []
        hypotheses_by_protein[viral_protein].append(hypothesis)
    
    # Add hypotheses as nodes
    node_id = 1
    
    for viral_protein, protein_hypotheses in hypotheses_by_protein.items():
        # Calculate positions for this group of hypotheses
        base_angle = random.uniform(0, 2 * math.pi)  # Random starting angle for this protein
        radius = 500
        
        for i, hypothesis in enumerate(protein_hypotheses):
            # Calculate position in a circle section
            angle = base_angle + (2 * math.pi / len(protein_hypotheses)) * i
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
            
            # Add node to network (without name parameter)
            cx2_network.add_node(node_id)
            
            # Add node name as 'n' attribute (this is what CX2 expects)
            cx2_network.add_node_attribute(node_id, 'n', node_name)
            
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

def main():
    print(f"Using UUID: {uuids[0]} (as example)")
    
    # Create timestamp for output filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save all hypotheses to file
    all_hypotheses_filename = f"all_hypotheses_{timestamp}.json"
    all_hypotheses_filepath = os.path.join(os.path.dirname(__file__), all_hypotheses_filename)
    
    with open(all_hypotheses_filepath, 'w') as f:
        json.dump(example_hypotheses, f, indent=2)
    
    print(f"\nSaved {len(example_hypotheses)} hypotheses to {all_hypotheses_filepath}")
    
    # Create hypothesis network
    print("\nCreating hypothesis network...")
    hypothesis_network = create_hypothesis_network(example_hypotheses)
    
    # Save CX2 network to file
    cx2_network_filename = f"hypothesis_network_{timestamp}.cx2"
    cx2_network_filepath = os.path.join(os.path.dirname(__file__), cx2_network_filename)
    
    with open(cx2_network_filepath, 'w') as f:
        json.dump(hypothesis_network.to_cx2(), f, indent=2)
    
    print(f"Saved hypothesis network to {cx2_network_filepath}")
    
    # Display summary of generated hypotheses
    print("\nGenerated Hypotheses Summary:")
    hypotheses_by_protein = {}
    for hypothesis in example_hypotheses:
        viral_protein = hypothesis['viral_protein']
        if viral_protein not in hypotheses_by_protein:
            hypotheses_by_protein[viral_protein] = []
        hypotheses_by_protein[viral_protein].append(hypothesis)
    
    for viral_protein, protein_hypotheses in hypotheses_by_protein.items():
        print(f"\n{viral_protein}: {len(protein_hypotheses)} hypotheses")
        
        for h in protein_hypotheses:
            print(f"  [{h['id']}] {h['title']} (Confidence: {h['confidence']}/5)")
    
    print(f"\nTotal hypotheses: {len(example_hypotheses)}")

if __name__ == "__main__":
    main()
