/**
 * Deckhard Client Module
 * 
 * This module provides functionality to interact with the Deckhard API
 * for creating object_lists and objects from NDEx network data.
 */

const deckhardClient = {
  /**
   * Create an object_list in Deckhard
   * @param {Object} properties - Object list properties
   * @returns {Promise} - Created object_list
   */
  createObjectList: async function(properties) {
    try {
      console.log("Creating object list with properties:", properties);
      
      const response = await fetch('/objects/object_list/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(properties)
      });
      
      if (!response.ok) {
        throw new Error(`Failed to create object_list: ${response.statusText}`);
      }
      
      const result = await response.json();
      console.log("Object list created:", result);
      return result;
    } catch (error) {
      console.error('Error creating object_list:', error);
      throw error;
    }
  },
  
  /**
   * Create a Deckhard object
   * @param {string} objectType - Object type
   * @param {Object} properties - Object properties
   * @returns {Promise} - Created object
   */
  createObject: async function(objectType, properties) {
    try {
      // Ensure all property values are strings or basic types
      const sanitizedProps = {};
      for (const [key, value] of Object.entries(properties)) {
        if (value !== null && value !== undefined) {
          // Convert non-primitive values to strings
          if (typeof value === 'object') {
            sanitizedProps[key] = JSON.stringify(value);
          } else {
            sanitizedProps[key] = value;
          }
        }
      }
      
      const response = await fetch(`/objects/${objectType}/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(sanitizedProps)
      });
      
      if (!response.ok) {
        throw new Error(`Failed to create object: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`Error creating ${objectType} object:`, error);
      throw error;
    }
  },
  
  /**
   * Create objects in batch (currently just sequential)
   * @param {string} objectType - Object type
   * @param {Array} objectsProperties - Array of object properties
   * @returns {Promise} - Array of created objects
   */
  createObjectsBatch: async function(objectType, objectsProperties) {
    const createdObjects = [];
    
    console.log(`Creating ${objectsProperties.length} objects of type ${objectType}`);
    
    for (const properties of objectsProperties) {
      try {
        const obj = await this.createObject(objectType, properties);
        createdObjects.push(obj);
      } catch (error) {
        console.error(`Error creating object:`, error);
        // Continue with other objects even if one fails
      }
    }
    
    console.log(`Successfully created ${createdObjects.length} objects`);
    return createdObjects;
  },
  
  /**
   * Transform NDEx nodes to Deckhard object properties
   * @param {Array} nodes - NDEx nodes
   * @param {Array} nodeAttributes - NDEx node attributes (optional)
   * @returns {Array} - Array of Deckhard object properties
   */
  transformNodesForDeckhard: function(nodes, nodeAttributes = []) {
    console.log("Transforming nodes:", JSON.stringify(nodes?.slice(0, 1) || []).slice(0, 200) + '...');
    
    if (!nodes || !Array.isArray(nodes)) {
      console.error("Invalid nodes data:", nodes);
      throw new Error('Invalid nodes data');
    }
    
    // Transform nodes to Deckhard object properties
    return nodes.map(node => {
      // Debug the node structure
      console.log("Processing node:", JSON.stringify(node));
      
      // Create a more flexible properties extraction
      const properties = {
        name: String(node.name || node.label || node.id || 'Unnamed Node'),
        ndex_id: String(node.id || Math.random()),
      };
      
      // Handle "represents" property specially
      if (node.represents) {
        properties.represents = String(node.represents);
      }
      
      // Add any additional properties that might exist on the node
      for (const [key, value] of Object.entries(node)) {
        if (key !== 'id' && key !== 'name' && value !== undefined && value !== null) {
          // Clean the key name to ensure it's valid for Deckhard
          const cleanKey = key.replace(/[^a-zA-Z0-9_]/g, '_').toLowerCase();
          if (typeof value === 'object') {
            properties[cleanKey] = JSON.stringify(value);
          } else {
            properties[cleanKey] = value;
          }
        }
      }
      
      // Process node attributes if available
      if (Array.isArray(nodeAttributes)) {
        const nodeAttrs = nodeAttributes.filter(attr => 
          attr.propertyOf !== undefined && 
          attr.propertyOf.toString() === node.id.toString()
        );
        
        nodeAttrs.forEach(attr => {
          if (attr.name) {
            const propName = attr.name.replace(/[^a-zA-Z0-9_]/g, '_').toLowerCase();
            properties[propName] = attr.value;
          }
        });
      }
      
      return properties;
    });
  },
  
  /**
   * Transform NDEx edges to Deckhard object properties
   * @param {Array} edges - NDEx edges
   * @param {Array} edgeAttributes - NDEx edge attributes (optional)
   * @returns {Array} - Array of Deckhard object properties
   */
  transformEdgesForDeckhard: function(edges, edgeAttributes = []) {
    console.log("Transforming edges:", JSON.stringify(edges?.slice(0, 1) || []).slice(0, 200) + '...');
    
    if (!edges || !Array.isArray(edges)) {
      console.error("Invalid edges data:", edges);
      throw new Error('Invalid edges data');
    }
    
    // Transform edges to Deckhard object properties
    return edges.map(edge => {
      // Debug the edge structure
      console.log("Processing edge:", JSON.stringify(edge));
      
      // Create a more flexible properties extraction
      const properties = {
        name: String(edge.name || edge.interaction || 'Edge ' + (edge.id || Math.random())),
        ndex_id: String(edge.id || Math.random()),
      };
      
      // Handle source and target
      if (edge.source !== undefined) {
        properties.source = String(edge.source);
      } else if (edge.sourceNode !== undefined) {
        properties.source = String(edge.sourceNode);
      }
      
      if (edge.target !== undefined) {
        properties.target = String(edge.target);
      } else if (edge.targetNode !== undefined) {
        properties.target = String(edge.targetNode);
      }
      
      // Add interaction if available
      if (edge.interaction) {
        properties.interaction = String(edge.interaction);
      }
      
      // Add any additional properties that might exist on the edge
      for (const [key, value] of Object.entries(edge)) {
        if (!['id', 'name', 'source', 'sourceNode', 'target', 'targetNode', 'interaction']
              .includes(key) && value !== undefined && value !== null) {
          // Clean the key name to ensure it's valid for Deckhard
          const cleanKey = key.replace(/[^a-zA-Z0-9_]/g, '_').toLowerCase();
          if (typeof value === 'object') {
            properties[cleanKey] = JSON.stringify(value);
          } else {
            properties[cleanKey] = value;
          }
        }
      }
      
      // Process edge attributes if available
      if (Array.isArray(edgeAttributes)) {
        const edgeAttrs = edgeAttributes.filter(attr => 
          attr.propertyOf !== undefined && 
          attr.propertyOf.toString() === edge.id.toString()
        );
        
        edgeAttrs.forEach(attr => {
          if (attr.name) {
            const propName = attr.name.replace(/[^a-zA-Z0-9_]/g, '_').toLowerCase();
            properties[propName] = attr.value;
          }
        });
      }
      
      return properties;
    });
  },
  
  /**
   * Validate scoring criteria format
   * @param {Object} criteria - Scoring criteria object
   * @returns {boolean} - True if valid
   */
  validateScoringCriteria: function(criteria) {
    if (!criteria || !Array.isArray(criteria)) {
      return false;
    }
    
    // Check if all criteria items have required properties
    return criteria.every(item => {
      return (
        item.label && typeof item.label === 'string' &&
        item.property_name && typeof item.property_name === 'string' &&
        (!item.input_type || ['text', 'textarea', 'checkbox', 'menu'].includes(item.input_type))
      );
    });
  },
  
  /**
   * Import network to Deckhard
   * @param {Object} networkData - Network data
   * @param {string} objectType - Object type for nodes/edges
   * @param {string} importType - 'nodes' or 'edges'
   * @param {Object} options - Additional options
   * @returns {Promise} - Import result
   */
  importNetworkToDeckhard: async function(networkData, objectType, importType, options = {}) {
    try {
      console.log(`Starting import of ${importType} as ${objectType}`,
                  `NetworkData structure includes:`, Object.keys(networkData),
                  `with ${networkData.properties?.length || 0} network properties.`);
      
      // 1. Create object_list
      const objectListProps = {
        name: options.name || networkData.name || 'NDEx Import',
        description: `Imported from NDEx network: ${networkData.name || 'Unnamed'}`,
        ndex_uuid: networkData.externalId || networkData.uuid || '', // Keep if available, else empty
        import_source: 'cx_file', // Indicate source was a file
        import_type: importType,
        object_type: objectType
      };
      
      // Add network attributes from CX file (networkData.properties)
      // These usually have { n: name, v: value, d: dataType }
      if (networkData.properties && Array.isArray(networkData.properties)) {
        networkData.properties.forEach(prop => {
          if (prop.n && prop.v !== undefined && prop.v !== null) {
            // Clean the property name and avoid overwriting core props
            const key = prop.n.replace(/[^a-zA-Z0-9_]/g, '_').toLowerCase();
            if (!['name', 'description', 'ndex_uuid', 'import_source', 'import_type', 'object_type', 'object_ids', '_criteria', '_order'].includes(key)) {
              // Convert value to string if it's not a basic type (default for unknown complex attributes)
              if (typeof prop.v === 'object') {
                objectListProps[key] = JSON.stringify(prop.v);
              } else {
                objectListProps[key] = prop.v; // Store the value directly
              }
            }
          }
        });
        console.log("Added network properties to object list props:", objectListProps);
      }
      
      // Add _order specifically as an object if it exists
      const orderAttribute = networkData.properties?.find(prop => prop.n === '_order');
      if (orderAttribute && orderAttribute.v !== undefined && orderAttribute.v !== null) {
        try {
          objectListProps._order = (typeof orderAttribute.v === 'string')
                                   ? JSON.parse(orderAttribute.v)
                                   : orderAttribute.v;
          console.log("Added _order object:", objectListProps._order);
        } catch (e) {
          console.warn("Could not parse _order attribute as JSON, skipping:", orderAttribute.v, e);
        }
      }
      
      // Add scoring criteria if available and valid (this handles _criteria)
      const criteriaAttribute = networkData.properties?.find(prop => prop.n === '_criteria');
      if (criteriaAttribute && criteriaAttribute.v !== undefined && criteriaAttribute.v !== null) {
        try {
          const parsedCriteria = (typeof criteriaAttribute.v === 'string')
                                 ? JSON.parse(criteriaAttribute.v)
                                 : criteriaAttribute.v;

          if (this.validateScoringCriteria(parsedCriteria)) {
            objectListProps._criteria = parsedCriteria;
            console.log("Added valid _criteria object:", objectListProps._criteria);
          } else {
            console.warn('Invalid scoring criteria format found in CX, not including in object_list', parsedCriteria);
          }
        } catch (e) {
          console.warn("Could not parse _criteria attribute as JSON, skipping:", criteriaAttribute.v, e);
        }
      }
      
      const objectList = await this.createObjectList(objectListProps);
      console.log("Object list created:", objectList);
      
      // 2. Create objects based on import type
      let objectsToCreate = [];
      
      if (importType === 'nodes') {
        // Check different potential locations for nodes data
        const nodesData = networkData.nodes || networkData.nodeList || [];
        const nodeAttrs = networkData.nodeAttributes || [];
        
        console.log(`Found ${nodesData.length} nodes to import`);
        objectsToCreate = this.transformNodesForDeckhard(nodesData, nodeAttrs);
      } else if (importType === 'edges') {
        // Check different potential locations for edges data
        const edgesData = networkData.edges || networkData.edgeList || [];
        const edgeAttrs = networkData.edgeAttributes || [];
        
        console.log(`Found ${edgesData.length} edges to import`);
        objectsToCreate = this.transformEdgesForDeckhard(edgesData, edgeAttrs);
      }
      
      console.log(`Transformed ${objectsToCreate.length} objects for creation`);
      
      // Limit to a reasonable number of objects for import
      const MAX_OBJECTS = 100;
      const objectsToSend = objectsToCreate.length > MAX_OBJECTS ? 
                           objectsToCreate.slice(0, MAX_OBJECTS) : objectsToCreate;
      
      // 3. Create objects in Deckhard
      console.log(`Creating ${objectsToSend.length} objects in Deckhard`);
      const createdObjects = await this.createObjectsBatch(objectType, objectsToSend);
      console.log(`Successfully created ${createdObjects.length} objects`);
      
      // 4. Update object_list with object IDs
      const objectIds = createdObjects.map(obj => obj.object_id);
      console.log("Updating object list with object IDs:", objectIds);
      await this.updateObjectList(objectList.object_id, { object_ids: objectIds });
      
      return {
        objectListId: objectList.object_id,
        objectCount: createdObjects.length,
        objectIds
      };
    } catch (error) {
      console.error('Error importing network to Deckhard:', error);
      throw error;
    }
  },
  
  /**
   * Update an object_list in Deckhard
   * @param {string} objectListId - Object list ID
   * @param {Object} properties - Properties to update
   * @returns {Promise} - Updated object_list
   */
  updateObjectList: async function(objectListId, properties) {
    try {
      console.log(`Updating object list ${objectListId} with properties:`, properties);
      
      // Add object_id to properties
      properties.object_id = objectListId;
      
      const response = await fetch(`/objects/object_list/${objectListId}/edit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(properties)
      });
      
      if (!response.ok) {
        throw new Error(`Failed to update object_list: ${response.statusText}`);
      }
      
      return true;
    } catch (error) {
      console.error('Error updating object_list:', error);
      throw error;
    }
  }
};

// Export the Deckhard client module
if (typeof module !== 'undefined' && module.exports) {
  module.exports = deckhardClient;
}