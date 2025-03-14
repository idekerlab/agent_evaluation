

// Store predefined queries
const predefinedQueries = [
  {
    name: "All Objects",
    query: "SELECT * FROM nodes LIMIT 100",
    description: "Shows the first 100 objects in the database"
  },
  {
    name: "All Agents",
    query: "SELECT * FROM nodes WHERE object_type = 'agent'",
    description: "Lists all agent objects"
  },
  {
    name: "All Datasets",
    query: "SELECT * FROM nodes WHERE object_type = 'dataset'",
    description: "Lists all dataset objects"
  },
  {
    name: "All Hypotheses",
    query: "SELECT * FROM nodes WHERE object_type = 'hypothesis'",
    description: "Lists all hypothesis objects"
  },
  {
    name: "Object Lists",
    query: "SELECT * FROM nodes WHERE object_type = 'object_list'",
    description: "Lists all object_list objects"
  },
  {
    name: "Recent Objects",
    query: "SELECT * FROM nodes ORDER BY json_extract(properties, '$.created') DESC LIMIT 20",
    description: "Shows the 20 most recently created objects"
  },
  {
    name: "Object Types Count",
    query: "SELECT object_type, COUNT(*) as count FROM nodes GROUP BY object_type ORDER BY count DESC",
    description: "Counts objects by type"
  }
];

// DOM Elements
let sqlInput, textSearchInput, resultsContainer, objectContainer;
let sqlSearchButton, textSearchButton;

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
  // Get DOM elements
  sqlInput = document.getElementById('sql-input');
  textSearchInput = document.getElementById('text-search-input');
  resultsContainer = document.getElementById('results-container');
  objectContainer = document.getElementById('object-container');
  sqlSearchButton = document.getElementById('sql-search-button');
  textSearchButton = document.getElementById('text-search-button');
  
  // Initialize the predefined queries list
  initPredefinedQueries();
  
  // Set up event listeners
  sqlSearchButton.addEventListener('click', executeSQL);
  textSearchButton.addEventListener('click', executeTextSearch);
  
  // Execute the first predefined query on load to show some initial data
  sqlInput.value = predefinedQueries[0].query;
  
  // Handle enter key in search inputs
  sqlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') executeSQL();
  });
  
  textSearchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') executeTextSearch();
  });
});

// Initialize the predefined queries list
function initPredefinedQueries() {
  const queryList = document.getElementById('query-list');
  queryList.innerHTML = '';
  
  predefinedQueries.forEach(query => {
    const listItem = document.createElement('li');
    listItem.className = 'query-item';
    listItem.textContent = query.name;
    listItem.title = query.description;
    
    listItem.addEventListener('click', () => {
      sqlInput.value = query.query;
      executeSQL();
    });
    
    queryList.appendChild(listItem);
  });
}

// Execute SQL query
async function executeSQL() {
  showLoading(resultsContainer);
  const sql = sqlInput.value.trim();
  
  if (!sql) {
    showError(resultsContainer, 'Please enter a SQL query');
    return;
  }
  
  try {
    const response = await fetch('/query_knowledge_graph_database', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ sql })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Error executing query');
    }
    
    const data = await response.json();
    displayResults(data);
  } catch (error) {
    showError(resultsContainer, `Error executing query: ${error.message}`);
  }
}

// Execute text search
async function executeTextSearch() {
  showLoading(resultsContainer);
  const searchText = textSearchInput.value.trim();
  
  if (!searchText) {
    showError(resultsContainer, 'Please enter a search term');
    return;
  }
  
  try {
    // Construct a SQL query to search in name, description and object_id fields
    const sql = `
      SELECT object_id, object_type, properties FROM nodes
      WHERE json_extract(properties, '$.name') LIKE '%${searchText}%'
      OR json_extract(properties, '$.description') LIKE '%${searchText}%'
      OR object_id LIKE '%${searchText}%'
      LIMIT 100
    `;
    
    const response = await fetch('/query_knowledge_graph_database', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ sql })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Error executing search');
    }
    
    const data = await response.json();
    displayResults(data);
  } catch (error) {
    showError(resultsContainer, `Error executing search: ${error.message}`);
  }
}

// Display query results in the middle panel
function displayResults(data) {
  resultsContainer.innerHTML = '';
  
  if (!data || !data.length) {
    resultsContainer.innerHTML = '<div class="notification">No results found</div>';
    return;
  }
  
  // Create table for results
  const table = document.createElement('table');
  table.className = 'result-table';
  
  // Create table header
  const thead = document.createElement('thead');
  const headerRow = document.createElement('tr');
  
  // Hardcoded headers 
  const headers = ['name', 'date', 'object_id',  'object_type'];
  
  headers.forEach(header => {
    const th = document.createElement('th');
    th.textContent = header;
    headerRow.appendChild(th);
  });
  
  thead.appendChild(headerRow);
  table.appendChild(thead);
  
  // Create table body
  const tbody = document.createElement('tbody');
  
  data.forEach(row => {
    const tr = document.createElement('tr');
    const properties = JSON.parse(row['properties']);
    const date = properties['created'];
    const name = properties['name'];

    headers.forEach(header => {
      const td = document.createElement('td');
      let value;
      if (header === 'date') {
        value = date;
      }else if (header === 'name'){
        value = name;
      }else{
        value = row[header];
      }

      td.textContent = value;
      tr.appendChild(td);
    });
    
    // Add click event to show object details
    tr.addEventListener('click', () => {
      let objectId, objectType;
      
      if (row.object_id) {
        objectId = row.object_id;
        
        // Try to get object_type
        if (row.object_type) {
          objectType = row.object_type;
        } else if (row.properties) {
          try {
            const props = JSON.parse(row.properties);
            if (props.object_type) objectType = props.object_type;
          } catch (e) {
            // If parsing fails, extract type from ID (format is usually type_uuid)
            const idParts = objectId.split('_');
            if (idParts.length > 1) objectType = idParts[0];
          }
        }
        
        if (objectId && objectType) {
          fetchObjectDetails(objectId, objectType);
        } else if (objectId) {
          // If we have an ID but no type, try to load it anyway
          fetchObjectDetails(objectId);
        }
      }
    });
    
    tbody.appendChild(tr);
  });
  
  table.appendChild(tbody);
  resultsContainer.appendChild(table);
}

// Fetch details of a specific object
async function fetchObjectDetails(objectId, objectType = 'objects') {
  showLoading(objectContainer);
  
  try {
    const response = await fetch(`/objects/${objectType}/${objectId}`);
    
    if (!response.ok) {
      throw new Error(`Error fetching object: ${response.statusText}`);
    }
    
    const data = await response.json();
    displayObjectDetails(data);
  } catch (error) {
    showError(objectContainer, `Error fetching object details: ${error.message}`);
  }
}

// Display object details in the right panel
function displayObjectDetails(data) {
  objectContainer.innerHTML = '';
  
  const objectView = document.createElement('div');
  objectView.className = 'object-view';
  
  // Object header
  const header = document.createElement('div');
  header.className = 'object-header';
  
  const title = document.createElement('h2');
  title.className = 'object-title';
  title.textContent = data.object.name || 'Unnamed object';
  
  const type = document.createElement('div');
  type.className = 'object-type';
  type.textContent = `Type: ${data.object_type}`;
  
  header.appendChild(title);
  header.appendChild(type);
  objectView.appendChild(header);
  
  // Properties section
  const propertiesHeader = document.createElement('h3');
  propertiesHeader.className = 'panel-header';
  propertiesHeader.textContent = 'Properties';
  objectView.appendChild(propertiesHeader);
  
  const propertiesList = document.createElement('div');
  propertiesList.className = 'property-list';
  
  // Sort properties alphabetically but keep object_id at the top
  const properties = data.object;
  const sortedKeys = Object.keys(properties).sort((a, b) => {
    if (a === 'object_id') return -1;
    if (b === 'object_id') return 1;
    return a.localeCompare(b);
  });
  
  sortedKeys.forEach(key => {
    const value = properties[key];
    
    // Skip empty values or complex objects that have their own visualization
    if (value === null || value === undefined || value === '') return;
    if (key === 'visualizations') return;
    
    const propertyItem = document.createElement('div');
    propertyItem.className = 'property-item';
    
    const propertyLabel = document.createElement('div');
    propertyLabel.className = 'property-label';
    propertyLabel.textContent = key;
    
    const propertyValue = document.createElement('div');
    propertyValue.className = 'property-value';
    
    // Handle different value types
    if (typeof value === 'object') {
      try {
        propertyValue.textContent = JSON.stringify(value, null, 2);
      } catch (e) {
        propertyValue.textContent = 'Complex object';
      }
    } else {
      propertyValue.textContent = value;
    }
    
    propertyItem.appendChild(propertyLabel);
    propertyItem.appendChild(propertyValue);
    propertiesList.appendChild(propertyItem);
  });
  
  objectView.appendChild(propertiesList);
  
  // Add action buttons based on object type
  const actionButtons = document.createElement('div');
  actionButtons.className = 'action-buttons';
  
  // Add a Review button for object_list type
  if (data.object_type === 'object_list') {
    const reviewButton = document.createElement('button');
    reviewButton.className = 'search-button';
    reviewButton.textContent = 'Review Object List';
    reviewButton.addEventListener('click', () => {
      openReviewInterface(data.object.object_id);
    });
    actionButtons.appendChild(reviewButton);
  }
  
  // Handle relationships if present
  if (data.object_type && data.object.object_id) {
    // Add a button to load relationships
    const relationshipsButton = document.createElement('button');
    relationshipsButton.className = 'search-button';
    relationshipsButton.textContent = 'Load Relationships';
    relationshipsButton.addEventListener('click', () => {
      fetchObjectRelationships(data.object.object_id);
    });
    actionButtons.appendChild(relationshipsButton);
  }
  
  if (actionButtons.children.length > 0) {
    objectView.appendChild(actionButtons);
  }
  
  // Handle visualizations if present
  if (data.object.visualizations) {
    const visualizationsHeader = document.createElement('h3');
    visualizationsHeader.className = 'panel-header';
    visualizationsHeader.textContent = 'Visualizations';
    objectView.appendChild(visualizationsHeader);
    
    const visualizationsContainer = document.createElement('div');
    visualizationsContainer.className = 'visualizations-container';
    
    try {
      const visualizations = data.object.visualizations;
      Object.keys(visualizations).forEach(key => {
        const vizContainer = document.createElement('div');
        vizContainer.style.marginBottom = '20px';
        
        const vizTitle = document.createElement('h4');
        vizTitle.textContent = key;
        vizContainer.appendChild(vizTitle);
        
        // If it's HTML, render it directly
        if (typeof visualizations[key] === 'string' && 
            (visualizations[key].startsWith('<') || visualizations[key].includes('<!DOCTYPE'))) {
          vizContainer.innerHTML += visualizations[key];
        } else {
          // Otherwise try to create appropriate visualization based on the data
          const pre = document.createElement('pre');
          pre.textContent = JSON.stringify(visualizations[key], null, 2);
          vizContainer.appendChild(pre);
        }
        
        visualizationsContainer.appendChild(vizContainer);
      });
    } catch (e) {
      visualizationsContainer.textContent = 'Unable to display visualizations';
    }
    
    objectView.appendChild(visualizationsContainer);
  }
  
  objectContainer.appendChild(objectView);
}

// Open review interface in a new tab
function openReviewInterface(objectListId) {
  // Create a notification to show that we're opening the review interface
  const notification = document.createElement('div');
  notification.className = 'notification success';
  notification.textContent = 'Opening review interface in a new tab...';
  
  // Add notification above the buttons
  const actionButtons = document.querySelector('.action-buttons');
  actionButtons.parentNode.insertBefore(notification, actionButtons);
  
  // Open the review interface in a new tab
  window.open(`/reviewer?object_list_id=${objectListId}`, '_blank');
  
  // Remove the notification after a few seconds
  setTimeout(() => {
    notification.remove();
  }, 3000);
}

// Fetch relationships for an object
async function fetchObjectRelationships(objectId) {
  const relationshipsSection = document.querySelector('.relationship-section');
  
  // Remove existing relationships section if it exists
  if (relationshipsSection) {
    relationshipsSection.remove();
  }
  
  const objectView = document.querySelector('.object-view');
  
  const loadingSpinner = document.createElement('div');
  loadingSpinner.className = 'spinner';
  objectView.appendChild(loadingSpinner);
  
  try {
    // Get relationships where this object is the source
    const sourceResponse = await fetch('/get_relationships', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ source_id: parseInt(objectId) })
    });
    
    const sourceData = await sourceResponse.json();
    
    // Get relationships where this object is the target
    const targetResponse = await fetch('/get_relationships', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ target_id: parseInt(objectId) })
    });
    
    const targetData = await targetResponse.json();
    
    // Remove loading spinner
    loadingSpinner.remove();
    
    // Create relationships section
    const relationshipsSection = document.createElement('div');
    relationshipsSection.className = 'relationship-section';
    
    const relationshipsHeader = document.createElement('h3');
    relationshipsHeader.className = 'panel-header';
    relationshipsHeader.textContent = 'Relationships';
    relationshipsSection.appendChild(relationshipsHeader);
    
    // Add outgoing relationships
    if (sourceData && sourceData.length > 0) {
      const outgoingHeader = document.createElement('h4');
      outgoingHeader.textContent = 'Outgoing Relationships';
      relationshipsSection.appendChild(outgoingHeader);
      
      const outgoingList = document.createElement('ul');
      
      sourceData.forEach(rel => {
        const listItem = document.createElement('li');
        listItem.style.marginBottom = '5px';
        
        // Make the target ID clickable
        const targetLink = document.createElement('a');
        targetLink.href = '#';
        targetLink.textContent = rel.target_id;
        targetLink.addEventListener('click', (e) => {
          e.preventDefault();
          // We don't know the object type, but the API can handle it with 'objects'
          fetchObjectDetails(rel.target_id);
        });
        
        listItem.textContent = `→ ${rel.type} → Object ID: `;
        listItem.appendChild(targetLink);
        
        outgoingList.appendChild(listItem);
      });
      
      relationshipsSection.appendChild(outgoingList);
    } else {
      const noOutgoing = document.createElement('p');
      noOutgoing.textContent = 'No outgoing relationships';
      relationshipsSection.appendChild(noOutgoing);
    }
    
    // Add incoming relationships
    if (targetData && targetData.length > 0) {
      const incomingHeader = document.createElement('h4');
      incomingHeader.textContent = 'Incoming Relationships';
      incomingHeader.style.marginTop = '15px';
      relationshipsSection.appendChild(incomingHeader);
      
      const incomingList = document.createElement('ul');
      
      targetData.forEach(rel => {
        const listItem = document.createElement('li');
        listItem.style.marginBottom = '5px';
        
        // Make the source ID clickable
        const sourceLink = document.createElement('a');
        sourceLink.href = '#';
        sourceLink.textContent = rel.source_id;
        sourceLink.addEventListener('click', (e) => {
          e.preventDefault();
          // We don't know the object type, but the API can handle it with 'objects'
          fetchObjectDetails(rel.source_id);
        });
        
        listItem.appendChild(sourceLink);
        listItem.appendChild(document.createTextNode(` → ${rel.type} →`));
        
        incomingList.appendChild(listItem);
      });
      
      relationshipsSection.appendChild(incomingList);
    } else {
      const noIncoming = document.createElement('p');
      noIncoming.textContent = 'No incoming relationships';
      noIncoming.style.marginTop = '15px';
      relationshipsSection.appendChild(noIncoming);
    }
    
    objectView.appendChild(relationshipsSection);
    
  } catch (error) {
    loadingSpinner.remove();
    
    const errorMessage = document.createElement('div');
    errorMessage.className = 'notification error';
    errorMessage.textContent = `Error fetching relationships: ${error.message}`;
    objectView.appendChild(errorMessage);
  }
}

// Helper function to show loading spinner
function showLoading(container) {
  container.innerHTML = '<div class="spinner"></div>';
}

// Helper function to show error message
function showError(container, message) {
  container.innerHTML = `<div class="notification error">${message}</div>`;
}