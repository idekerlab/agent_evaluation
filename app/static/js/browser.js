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

let currentData = [];

let sortDirections = {
  name: 'asc',
  date: 'asc',
  object_id: 'asc',
  object_type: 'asc',
};

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
  
  // Reset the right panel header
  resetObjectDetailsHeader();
  
  // Execute the first predefined query on load to show some initial data
  sqlInput.value = predefinedQueries[0].query;
  
  // Handle enter key in search inputs
  sqlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') executeSQL();
  });
  
  textSearchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') executeTextSearch();
  });
  
  // Add keyboard event to close modal with Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      const modal = document.getElementById('confirmation-modal');
      if (modal.style.display === 'flex') {
        modal.style.display = 'none';
      }
    }
  });
  
  // Also close modal when clicking outside of it
  const modal = document.getElementById('confirmation-modal');
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.style.display = 'none';
    }
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
  currentData = data;
  resultsContainer.innerHTML = '';

  // If no data
  if (!data || !data.length) {
    resultsContainer.innerHTML = '<div class="notification">No results found</div>';
    return;
  }

  const table = document.createElement('table');
  table.className = 'result-table';

  const thead = document.createElement('thead');
  const headerRow = document.createElement('tr');

  const headers = ['name', 'date', 'object_id', 'object_type'];

  // Set column widths based on content type
  const colWidths = {
    'name': '38%',      // Allocate more space for names
    'date': '15%',      // Dates have a consistent format
    'object_id': '25%', // IDs can be long
    'object_type': '22%' // Types are usually short
  };

  headers.forEach((header) => {
    const th = createSortableHeader(header);
    // Set the width for each column
    th.style.width = colWidths[header];
    headerRow.appendChild(th);
  });

  thead.appendChild(headerRow);
  table.appendChild(thead);

  // Create table body
  const tbody = document.createElement('tbody');

  data.forEach((row) => {
    const tr = document.createElement('tr');
    const properties = JSON.parse(row['properties']);
    const date = properties['created'];
    const name = properties['name'];

    headers.forEach((header) => {
      const td = document.createElement('td');
      td.setAttribute('data-header', header);
      let value;
      
      if (header === 'date') {
        value = date;
      } else if (header === 'name') {
        value = name;
        // Add title attribute for tooltip on hover for long names
        td.title = name || '';
        // Format long names for display
        td.textContent = formatLongText(value);
        tr.appendChild(td);
        return; // Skip the td.textContent line below
      } else {
        value = row[header];
        // Don't format object_id or other columns, use their original values
      }
      
      td.textContent = value || '';
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
            const idParts = objectId.split('_');
            if (idParts.length > 1) objectType = idParts[0];
          }
        }

        if (objectId && objectType) {
          fetchObjectDetails(objectId, objectType);
        } else if (objectId) {
          fetchObjectDetails(objectId);
        }
      }
    });

    tbody.appendChild(tr);
  });

  table.appendChild(tbody);
  resultsContainer.appendChild(table);
}

function sortAndRender(header) {
  // Toggle direction
  const currentDirection = sortDirections[header];
  const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
  sortDirections[header] = newDirection;

  currentData.sort((a, b) => {
    const propsA = JSON.parse(a.properties);
    const propsB = JSON.parse(b.properties);

    let valA, valB;
    if (header === 'name') {
      valA = propsA.name || '';
      valB = propsB.name || '';
      
      // Convert to string & lowercase for case-insensitive compare
      valA = String(valA).toLowerCase();
      valB = String(valB).toLowerCase();
      
      // Compare as strings
      if (valA < valB) return newDirection === 'asc' ? -1 : 1;
      if (valA > valB) return newDirection === 'asc' ? 1 : -1;
      return 0;
    } 
    else if (header === 'date') {
      // Handle date sorting
      const dateStrA = propsA.created || '';
      const dateStrB = propsB.created || '';
      
      // Parse the date strings to Date objects
      const dateA = parseDate(dateStrA);
      const dateB = parseDate(dateStrB);
      
      // Handle invalid dates - put them at the bottom
      if (!dateA && !dateB) return 0;
      if (!dateA) return newDirection === 'asc' ? 1 : -1;
      if (!dateB) return newDirection === 'asc' ? -1 : 1;
      
      // Compare date objects
      if (dateA < dateB) return newDirection === 'asc' ? -1 : 1;
      if (dateA > dateB) return newDirection === 'asc' ? 1 : -1;
      return 0;
    } 
    else {
      valA = a[header] || '';
      valB = b[header] || '';
      
      // Convert to string & lowercase for case-insensitive compare
      valA = String(valA).toLowerCase();
      valB = String(valB).toLowerCase();
      
      // Compare as strings
      if (valA < valB) return newDirection === 'asc' ? -1 : 1;
      if (valA > valB) return newDirection === 'asc' ? 1 : -1;
      return 0;
    }
  });

  displayResults(currentData);
  const allHeaders = document.querySelectorAll('th.sortable-header');
  allHeaders.forEach((th) => {
    const hName = th.getAttribute('data-header');
    const icon = th.querySelector('button.sort-button i'); // the <i> inside the button
    if (!icon) return;

    // If this is the sorted column, set the correct icon
    if (hName === header) {
      if (newDirection === 'asc') {
        icon.className = hName === 'date' ? 'fas fa-sort-numeric-up' : 'fas fa-sort-alpha-up';
      } else {
        icon.className = hName === 'date' ? 'fas fa-sort-numeric-down' : 'fas fa-sort-alpha-down';
      }
    } else {
      // For all other columns, revert to the appropriate icon
      icon.className = hName === 'date' ? 'fas fa-sort-numeric-up' : 'fas fa-sort-alpha-up';
    }
  });
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
    console.log(data);
    // First, clear the Object Details panel header
    const panelHeader = document.querySelector('.right-panel .panel-header');
    
    // Create the delete button for the panel header
    const deleteButton = document.createElement('button');
    deleteButton.className = 'delete-button';
    deleteButton.innerHTML = '<i class="fas fa-trash"></i> Delete';
    deleteButton.addEventListener('click', () => {
      showDeleteConfirmation(data.object.object_id, data.object_type, data.object);
    });
    
    // Clear the panel header and re-add the text and delete button
    panelHeader.innerHTML = 'Object Details';
    panelHeader.appendChild(deleteButton);
    
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
  
  // Check for _display_types in the object
  const displayTypes = {};
  if (properties._display_types && Array.isArray(properties._display_types)) {
    properties._display_types.forEach(dt => {
      if (dt.property_name && dt.display_type) {
        displayTypes[dt.property_name] = dt.display_type;
      }
    });
  }
  
  sortedKeys.forEach(key => {
    const value = properties[key];
    
    // Skip empty values or complex objects that have their own visualization
    if (value === null || value === undefined || value === '') return;
    if (key === 'visualizations' || key === '_display_types') return;
    
    const propertyItem = document.createElement('div');
    propertyItem.className = 'property-item';
    
    const propertyLabel = document.createElement('div');
    propertyLabel.className = 'property-label';
    propertyLabel.textContent = key;
    
    const propertyValue = document.createElement('div');
    propertyValue.className = 'property-value';
    
    // Check if this property has a special display type
    const displayType = displayTypes[key];
    
    if (displayType === 'csv' && typeof value === 'string') {
      const csvTable = createCSVTable(value);
      if (csvTable) {
        propertyValue.appendChild(csvTable);
      } else {
        propertyValue.textContent = value;
      }
    } else if (Array.isArray(value) && is2DArray(value) && value.length > 0) {
      // Handle 2D arrays by displaying them as tables
      try {
        const tableElement = createTableFromArray(value);
        propertyValue.appendChild(tableElement);
      } catch (e) {
        // Fallback to JSON display if table creation fails
        propertyValue.textContent = JSON.stringify(value, null, 2);
      }
    } else if (typeof value === 'object') {
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
  
  // Add a View Reviews button for review_list type
  if (data.object_type === 'review_list') {
    const viewReviewsButton = document.createElement('button');
    viewReviewsButton.className = 'search-button';
    viewReviewsButton.textContent = 'View Review List';
    viewReviewsButton.addEventListener('click', () => {
      openReviewListViewer(data.object.object_id);
    });
    actionButtons.appendChild(viewReviewsButton);
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

// Show delete confirmation modal
function showDeleteConfirmation(objectId, objectType, objectData) {
  const modal = document.getElementById('confirmation-modal');
  const modalDetail = document.getElementById('modal-detail');
  const modalCancel = document.getElementById('modal-cancel');
  const modalConfirm = document.getElementById('modal-confirm');
  
  // Clear previous event listeners
  const newModalCancel = modalCancel.cloneNode(true);
  const newModalConfirm = modalConfirm.cloneNode(true);
  modalCancel.parentNode.replaceChild(newModalCancel, modalCancel);
  modalConfirm.parentNode.replaceChild(newModalConfirm, modalConfirm);
  
  // If it's an object_list, add additional warning
  if (objectType === 'object_list' && objectData.object_ids && objectData.object_ids.length > 0) {
    modalDetail.textContent = `This will also delete ${objectData.object_ids.length} objects contained in this list.`;
  } else {
    modalDetail.textContent = '';
  }
  
  // Show the modal
  modal.style.display = 'flex';
  
  // Cancel button event
  newModalCancel.addEventListener('click', () => {
    modal.style.display = 'none';
  });
  
  // Confirm button event
  newModalConfirm.addEventListener('click', () => {
    deleteObject(objectId, objectType, objectData);
    modal.style.display = 'none';
  });
}

// Delete an object
async function deleteObject(objectId, objectType, objectData) {
  showLoading(objectContainer);
  
  try {
    // Delete the main object
    const response = await fetch(`/objects/${objectType}/${objectId}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      throw new Error(`Error deleting object: ${response.statusText}`);
    }
    
    // If it's an object_list, also delete all contained objects
    if (objectType === 'object_list' && objectData.object_ids && objectData.object_ids.length > 0) {
      // We'll delete the objects sequentially to avoid overwhelming the server
      for (const containedId of objectData.object_ids) {
        try {
          // Use POST for contained objects since it's guaranteed to work
          // The DELETE endpoint might not be supported for all object types
          await fetch(`/objects/objects/${containedId}/delete`, {
            method: 'POST'
          });
        } catch (error) {
          console.error(`Error deleting contained object ${containedId}:`, error);
          // Continue with other deletions even if one fails
        }
      }
    }
    
    // Show success message and clear the object view
    objectContainer.innerHTML = '<div class="notification success">Object successfully deleted.</div>';
    
    // Reset the panel header after deletion
    resetObjectDetailsHeader();
    
    // Refresh the search results
    if (sqlInput.value) {
      executeSQL();
    } else if (textSearchInput.value) {
      executeTextSearch();
    }
    
  } catch (error) {
    showError(objectContainer, `Error deleting object: ${error.message}`);
  }
}
