/**
 * NDEx Client Module
 * 
 * This module provides functionality to interact with the NDEx API
 * for fetching network data.
 */

const ndexClient = {
    // Direct test using the test-ndex endpoint (for backward compatibility)
    async testFetchNetwork(uuid) {
        try {
            console.log("Testing direct fetch with UUID:", uuid);
            const response = await fetch(`/test-ndex/${uuid}`);
            
            if (!response.ok) {
                throw new Error(`Test API error (${response.status}): ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log("Test endpoint response:", data);
            
            // Validate the network data structure
            this.validateNetworkData(data);
            
            return data;
        } catch (error) {
            console.error("Test fetch error:", error);
            throw error;
        }
    },
    
    // Fetch network summary using the server-side ndex2 client
    async fetchNetworkSummary(uuid) {
        try {
            console.log("Fetching network summary for UUID:", uuid);
            const response = await fetch(`/ndex-client/${uuid}?summary_only=true`);
            
            if (!response.ok) {
                throw new Error(`Network API error (${response.status}): ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log("Network summary received");
            
            // Validate the network data structure
            this.validateNetworkData(data);
            
            return data;
        } catch (error) {
            console.error("Fetch network summary error:", error);
            throw error;
        }
    },
    
    // Fetch the complete network data with nodes and edges
    async fetchCompleteNetwork(uuid) {
        try {
            console.log("Fetching complete network with UUID:", uuid);
            const response = await fetch(`/ndex-client/${uuid}`);
            
            if (!response.ok) {
                throw new Error(`Network API error (${response.status}): ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log("Complete network response received");
            
            // Validate the network data structure
            this.validateNetworkData(data);
            
            return data;
        } catch (error) {
            console.error("Fetch complete network error:", error);
            throw error;
        }
    },
    
    // Test proxy endpoint directly for summary (for backward compatibility)
    async testProxyFetch(uuid) {
        try {
            console.log("Testing proxy fetch with UUID:", uuid);
            const url = `/ndex-proxy/network/${uuid}/summary`;
            console.log("Proxy URL:", url);
            
            const response = await fetch(url);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error("Error response text:", errorText);
                throw new Error(`Proxy API error (${response.status}): ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log("Proxy endpoint response:", data);
            return data;
        } catch (error) {
            console.error("Proxy fetch error:", error);
            throw error;
        }
    },
    
    /**
     * Validate that the network data has the necessary structure
     * @param {Object} data - Network data
     */
    validateNetworkData(data) {
        console.log("Validating network data structure");
        
        if (!data) {
            throw new Error("Network data is empty");
        }
        
        // Ensure we have a valid network object
        if (!data.name) {
            console.warn("Network doesn't have a name property");
            // Set a default name if missing
            data.name = "Unnamed Network";
        }
        
        // Check for nodes
        if (data.nodes) {
            console.log(`Network has ${data.nodes.length} nodes`);
            
            // Verify nodes structure by checking the first node
            if (data.nodes.length > 0) {
                console.log("Example node structure:", JSON.stringify(data.nodes[0]));
            }
        } else if (data.nodeList) {
            console.log(`Network has ${data.nodeList.length} nodes (using nodeList)`);
            // Copy nodeList to nodes for consistency
            data.nodes = data.nodeList;
        } else {
            console.warn("Network doesn't have nodes or nodeList property");
            // Create an empty nodes array to prevent errors
            data.nodes = [];
        }
        
        // Check for edges
        if (data.edges) {
            console.log(`Network has ${data.edges.length} edges`);
            
            // Verify edges structure by checking the first edge
            if (data.edges.length > 0) {
                console.log("Example edge structure:", JSON.stringify(data.edges[0]));
            }
        } else if (data.edgeList) {
            console.log(`Network has ${data.edgeList.length} edges (using edgeList)`);
            // Copy edgeList to edges for consistency
            data.edges = data.edgeList;
        } else {
            console.warn("Network doesn't have edges or edgeList property");
            // Create an empty edges array to prevent errors
            data.edges = [];
        }
        
        return true;
    },
    
    // Get network summary via server-side ndex2 client
    async getNetworkSummary(uuid) {
        try {
            console.log("Getting network summary for UUID:", uuid);
            // Use the server-side ndex2 client endpoint
            return await this.fetchNetworkSummary(uuid);
        } catch (error) {
            console.error("Get network summary error:", error);
            throw error;
        }
    },
    
    // Get full network with nodes and edges
    async getFullNetwork(uuid) {
        try {
            console.log("Getting full network data for UUID:", uuid);
            // Use the server-side ndex2 client endpoint
            return await this.fetchCompleteNetwork(uuid);
        } catch (error) {
            console.error("Get full network error:", error);
            throw error;
        }
    },
    
    // Get network nodes
    async getNetworkNodes(uuid, limit = 100) {
        try {
            console.log("Fetching network nodes for UUID:", uuid);
            // Get the complete network
            const networkData = await this.getFullNetwork(uuid);
            
            // Get nodes from either nodes or nodeList property
            const nodes = networkData.nodes || networkData.nodeList || [];
            
            if (!nodes || !Array.isArray(nodes)) {
                console.warn("No nodes found in network data");
                return [];
            }
            
            // Limit the number of nodes to return
            return nodes.slice(0, limit);
        } catch (error) {
            console.error("Get network nodes error:", error);
            throw error;
        }
    },
    
    // Get network edges
    async getNetworkEdges(uuid, limit = 100) {
        try {
            console.log("Fetching network edges for UUID:", uuid);
            // Get the complete network
            const networkData = await this.getFullNetwork(uuid);
            
            // Get edges from either edges or edgeList property
            const edges = networkData.edges || networkData.edgeList || [];
            
            if (!edges || !Array.isArray(edges)) {
                console.warn("No edges found in network data");
                return [];
            }
            
            // Limit the number of edges to return
            return edges.slice(0, limit);
        } catch (error) {
            console.error("Get network edges error:", error);
            throw error;
        }
    },
    
    // Get node attributes
    async getNodeAttributes(uuid) {
        try {
            console.log("Fetching node attributes for UUID:", uuid);
            // Get the complete network
            const networkData = await this.getFullNetwork(uuid);
            
            if (!networkData.nodeAttributes || !Array.isArray(networkData.nodeAttributes)) {
                console.warn("No node attributes found in network data");
                return [];
            }
            
            return networkData.nodeAttributes;
        } catch (error) {
            console.error("Get node attributes error:", error);
            throw error;
        }
    },
    
    // Get edge attributes
    async getEdgeAttributes(uuid) {
        try {
            console.log("Fetching edge attributes for UUID:", uuid);
            // Get the complete network
            const networkData = await this.getFullNetwork(uuid);
            
            if (!networkData.edgeAttributes || !Array.isArray(networkData.edgeAttributes)) {
                console.warn("No edge attributes found in network data");
                return [];
            }
            
            return networkData.edgeAttributes;
        } catch (error) {
            console.error("Get edge attributes error:", error);
            throw error;
        }
    },
    
    // Get complete network data (nodes, edges, attributes)
    async getNetworkData(uuid) {
        try {
            console.log("Fetching complete network data for UUID:", uuid);
            // Use the complete network endpoint
            return await this.getFullNetwork(uuid);
        } catch (error) {
            console.error("Get network data error:", error);
            throw error;
        }
    },
    
    // Extract network properties
    extractNetworkProperties(summary) {
        console.log("Extracting network properties");
        
        const properties = {};
        
        // Basic properties
        properties.name = summary.name || 'Unnamed Network';
        properties.description = summary.description || '';
        properties.nodeCount = summary.nodeCount || (summary.nodes?.length || summary.nodeList?.length || 0);
        properties.edgeCount = summary.edgeCount || (summary.edges?.length || summary.edgeList?.length || 0);
        properties.owner = summary.owner || '';
        properties.creationTime = summary.creationTime || '';
        properties.modificationTime = summary.modificationTime || '';
        
        // Extended properties
        if (summary.properties && Array.isArray(summary.properties)) {
            properties.ndexProperties = {};
            summary.properties.forEach(prop => {
                if (prop.predicateString && prop.value !== undefined) {
                    properties.ndexProperties[prop.predicateString] = prop.value;
                }
            });
        }
        
        console.log("Extracted properties:", properties);
        return properties;
    },
    
    // Get scoring criteria if available
    getScoringCriteria(summary) {
        console.log("Checking for scoring criteria");
        
        if (!summary.properties || !Array.isArray(summary.properties)) {
            console.warn("No properties array found in network summary");
            return null;
        }
        
        const criteriaProp = summary.properties.find(
            prop => prop.predicateString === 'scoring_criteria'
        );
        
        if (!criteriaProp || criteriaProp.value === undefined) {
            console.warn("No scoring_criteria property found in network properties");
            return null;
        }
        
        try {
            // Handle the case where the value might already be an object
            const criteria = typeof criteriaProp.value === 'string' ? 
                             JSON.parse(criteriaProp.value) : criteriaProp.value;
                             
            console.log("Found scoring criteria:", criteria);
            return criteria;
        } catch (error) {
            console.error('Failed to parse scoring criteria:', error);
            throw new Error('Invalid scoring_criteria format: ' + error.message);
        }
    }
};

// Make ndexClient globally available
window.ndexClient = ndexClient;
