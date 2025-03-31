// Reviewer Interface - UI Module
// Handles UI rendering and scoring functionality

// Display the object at the specified index
function displayObject(index) {
  console.log('Displaying object at index:', index);
  
  if (!objects || index < 0 || index >= objects.length) {
    console.error('Invalid object index or no objects available:', { index, objects });
    showNotification('Invalid object index', 'error');
    return;
  }
  
  const object = objects[index];
  console.log('Object to display:', object);
  
  objectContainer.innerHTML = '';
  
  const objectView = document.createElement('div');
  objectView.className = 'object-view';
  
  // Object header
  const header = document.createElement('div');
  header.className = 'object-header';
  
  const title = document.createElement('h2');
  title.className = 'object-title';
  title.textContent = object.name || 'Unnamed object';
  
  const type = document.createElement('div');
  type.className = 'object-type';
  type.textContent = `Type: ${object.type || 'Unknown'}`;
  
  const objectId = document.createElement('div');
  objectId.className = 'object-id';
  objectId.textContent = `ID: ${object.object_id}`;
  
  header.appendChild(title);
  header.appendChild(type);
  header.appendChild(objectId);
  objectView.appendChild(header);
  
  // Properties section
  const propertiesHeader = document.createElement('h3');
  propertiesHeader.className = 'panel-header';
  propertiesHeader.textContent = 'Properties';
  objectView.appendChild(propertiesHeader);
  
  const propertiesList = document.createElement('div');
  propertiesList.className = 'property-list';
  
  // Check for _display_types in the object
  const displayTypes = {};
  if (object._display_types && Array.isArray(object._display_types)) {
    object._display_types.forEach(dt => {
      if (dt.property_name && dt.display_type) {
        displayTypes[dt.property_name] = dt.display_type;
      }
    });
  }
  
  // Get order configuration from the object list, not from the individual object
  // _order: An optional property in the object list that defines the display order of properties
  // Format: { "property_name": order_rank_number, ... }
  // Properties with lower rank numbers are displayed first
  // Properties with the same rank are sorted alphabetically
  // Properties not mentioned in _order are displayed after ordered properties, sorted alphabetically
  const orderConfig = objectList && objectList._order ? objectList._order : {};
  console.log('Object list order configuration:', orderConfig);
  
  // Display object properties, excluding system properties
  const systemProperties = ['object_id', 'type', '_criteria', '_display_types', '_order'];
  
  // Get all property keys from this object and sort them according to objectList._order if available
  const propertyKeys = Object.keys(object).filter(key => !systemProperties.includes(key) && 
                                                      object[key] !== null && 
                                                      object[key] !== undefined && 
                                                      object[key] !== '');
  
  // Sort keys of this object using the _order property from objectList
  propertyKeys.sort((a, b) => {
    // Get the order ranks from objectList._order for the properties in this object
    const rankA = orderConfig[a];
    const rankB = orderConfig[b];
    
    // Log the ranks for debugging
    if (rankA !== undefined || rankB !== undefined) {
      console.log(`Comparing object property ${a} (rank ${rankA}) with ${b} (rank ${rankB})`);
    }
    
    // If both have defined ranks in objectList._order
    if (rankA !== undefined && rankB !== undefined) {
      // If ranks are different, sort by rank
      if (rankA !== rankB) {
        return rankA - rankB;
      }
      // If ranks are the same, sort alphabetically
      return a.localeCompare(b);
    }
    
    // If only a has rank in objectList._order, it comes first
    if (rankA !== undefined) {
      return -1;
    }
    
    // If only b has rank in objectList._order, it comes first
    if (rankB !== undefined) {
      return 1;
    }
    
    // If neither has rank in objectList._order, sort alphabetically
    return a.localeCompare(b);
  });
  
  // Now display this object's properties in the sorted order
  propertyKeys.forEach(key => {
    const value = object[key];
    
    const propertyItem = document.createElement('div');
    propertyItem.className = 'property-item';
    
    const propertyLabel = document.createElement('div');
    propertyLabel.className = 'property-label';
    propertyLabel.textContent = key;
    
    const propertyValue = document.createElement('div');
    propertyValue.className = 'property-value';
    
    // Handle different display types
    const displayType = displayTypes[key] || 'text';
    
    if (displayType === 'csv' && typeof value === 'string') {
      // Display CSV as a table
      const csvContainer = document.createElement('div');
      csvContainer.className = 'csv-table';
      
      const table = document.createElement('table');
      const rows = value.trim().split('\n');
      
      if (rows.length > 0) {
        // Create header
        const header = rows[0].split(',');
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        
        header.forEach(cell => {
          const th = document.createElement('th');
          th.textContent = cell.trim();
          headerRow.appendChild(th);
        });
        
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        // Create body
        const tbody = document.createElement('tbody');
        
        for (let i = 1; i < rows.length; i++) {
          const cells = rows[i].split(',');
          const tr = document.createElement('tr');
          
          cells.forEach(cell => {
            const td = document.createElement('td');
            td.textContent = cell.trim();
            tr.appendChild(td);
          });
          
          tbody.appendChild(tr);
        }
        
        table.appendChild(tbody);
      }
      
      csvContainer.appendChild(table);
      propertyValue.appendChild(csvContainer);
    } else if (typeof value === 'object') {
      // Display objects as formatted JSON
      try {
        const pre = document.createElement('pre');
        pre.textContent = JSON.stringify(value, null, 2);
        propertyValue.appendChild(pre);
      } catch (e) {
        propertyValue.textContent = 'Complex object';
      }
    } else {
      // Default text display
      propertyValue.textContent = value;
    }
    
    propertyItem.appendChild(propertyLabel);
    propertyItem.appendChild(propertyValue);
    propertiesList.appendChild(propertyItem);
  });
  
  objectView.appendChild(propertiesList);
  objectContainer.appendChild(objectView);
  
  // Update scoring form for this object
  updateScoringForm();
}

// Generate the scoring form based on criteria
function generateScoringForm() {
  console.log('Generating scoring form with criteria:', objectList._criteria);
  
  scoringFormContainer.innerHTML = '';
  
  if (!objectList._criteria || !Array.isArray(objectList._criteria) || objectList._criteria.length === 0) {
    scoringFormContainer.innerHTML = '<div class="notification warning">No scoring criteria defined.</div>';
    return;
  }
  
  const currentObject = objects[currentObjectIndex];
  
  // Create form elements for each criterion
  objectList._criteria.forEach(criterion => {
    console.log('Processing criterion:', criterion);
    
    const formGroup = document.createElement('div');
    formGroup.className = 'form-group';
    
    const label = document.createElement('label');
    label.className = 'form-label';
    label.setAttribute('for', `criterion-${criterion.property_name}`);
    label.textContent = criterion.label || criterion.property_name;
    
    let input;
    
    // Create different input types based on criterion definition
    switch (criterion.input_type) {
      case 'textarea':
        input = document.createElement('textarea');
        input.className = 'form-textarea';
        break;
        
      case 'checkbox':
        input = document.createElement('input');
        input.type = 'checkbox';
        input.className = 'form-checkbox';
        break;
        
      case 'menu':
        input = document.createElement('select');
        input.className = 'form-select';
        
        // If options are provided, add them to the select
        if (criterion.options && Array.isArray(criterion.options)) {
          // Add an empty option first
          const emptyOption = document.createElement('option');
          emptyOption.value = '';
          emptyOption.textContent = 'Select an option';
          input.appendChild(emptyOption);
          
          criterion.options.forEach(option => {
            const optionEl = document.createElement('option');
            optionEl.value = option;
            optionEl.textContent = option;
            input.appendChild(optionEl);
          });
        } else {
          // Default options
          [1, 2, 3, 4, 5].forEach(val => {
            const optionEl = document.createElement('option');
            optionEl.value = val;
            optionEl.textContent = val;
            input.appendChild(optionEl);
          });
        }
        break;
        
      case 'text':
      default:
        input = document.createElement('input');
        input.type = 'text';
        input.className = 'form-input';
        break;
    }
    
    // Set common attributes
    input.id = `criterion-${criterion.property_name}`;
    input.name = criterion.property_name;
    input.placeholder = `Enter ${criterion.label || criterion.property_name}`;
    
    // Add event listener for auto-save
    input.addEventListener('change', function() {
      console.log(`Input changed for ${criterion.property_name}`);
      // First save the scores for the current object
      saveCurrentScores();
      // Then schedule auto-save
      scheduleAutoSave();
    });
    
    // For textareas, also add input event for real-time saving
    if (input.tagName === 'TEXTAREA') {
      input.addEventListener('input', function() {
        // Only schedule auto-save, don't save scores immediately on each keystroke
        scheduleAutoSave();
      });
    }
    
    formGroup.appendChild(label);
    formGroup.appendChild(input);
    scoringFormContainer.appendChild(formGroup);
  });
  
  // Update the form with any existing scores for this specific object
  updateScoringForm();
}

// Update the scoring form with values from the review for the current object
function updateScoringForm() {
  console.log('Updating scoring form for object index:', currentObjectIndex);
  
  if (!review || !review.scores || !objects || currentObjectIndex >= objects.length) {
    console.warn('Cannot update scoring form - missing required data', { 
      review: !!review, 
      scores: review ? !!review.scores : false, 
      objects: !!objects, 
      currentObjectIndex 
    });
    return;
  }
  
  const currentObject = objects[currentObjectIndex];
  const objectId = currentObject.object_id;
  
  // Find existing scores for this specific object
  const objectScores = review.scores.find(s => s.reviewed_object === objectId);
  console.log('Found object scores:', objectScores);
  
  // Clear all inputs first to avoid carrying over values from previous objects
  if (objectList._criteria && Array.isArray(objectList._criteria)) {
    objectList._criteria.forEach(criterion => {
      const input = document.getElementById(`criterion-${criterion.property_name}`);
      if (!input) return;
      
      if (input.type === 'checkbox') {
        input.checked = false;
      } else if (input.tagName === 'SELECT') {
        input.selectedIndex = 0;
      } else {
        input.value = '';
      }
    });
  }
  
  // If no scores exist for this object, leave form empty
  if (!objectScores) return;
  
  // Update form values with this object's specific scores
  if (objectList._criteria && Array.isArray(objectList._criteria)) {
    objectList._criteria.forEach(criterion => {
      const input = document.getElementById(`criterion-${criterion.property_name}`);
      if (!input) return;
      
      const value = objectScores.scores[criterion.property_name];
      console.log(`Setting ${criterion.property_name} to:`, value);
      
      if (value !== undefined) {
        if (input.type === 'checkbox') {
          input.checked = Boolean(value);
        } else if (input.tagName === 'SELECT') {
          input.value = value;
        } else {
          input.value = value;
        }
      }
    });
  }
}

// Save the scores for the current object only
function saveCurrentScores() {
  console.log('Saving scores for object index:', currentObjectIndex);
  
  if (!review || !objectList._criteria || !Array.isArray(objectList._criteria) || currentObjectIndex >= objects.length) {
    console.warn('Cannot save scores - missing required data', { 
      review: !!review, 
      criteria: objectList ? !!objectList._criteria : false, 
      objects: !!objects, 
      currentObjectIndex 
    });
    return;
  }
  
  const currentObject = objects[currentObjectIndex];
  const objectId = currentObject.object_id;
  
  // Create a new scores object for this specific object
  const scores = {};
  let isValid = true;
  
  // Collect scores from form inputs
  objectList._criteria.forEach(criterion => {
    const input = document.getElementById(`criterion-${criterion.property_name}`);
    if (!input) {
      console.warn(`Input not found for criterion: ${criterion.property_name}`);
      return;
    }
    
    let value;
    
    if (input.type === 'checkbox') {
      value = input.checked;
    } else {
      value = input.value;
    }
    
    console.log(`Collected value for ${criterion.property_name}:`, value);
    
    // Validate based on data_type
    if (criterion.data_type) {
      if (criterion.data_type === 'int' && value !== '') {
        const intValue = parseInt(value, 10);
        if (isNaN(intValue)) {
          showNotification(`${criterion.label || criterion.property_name} must be an integer.`, 'error');
          isValid = false;
          return;
        }
        value = intValue;
      }
    }
    
    scores[criterion.property_name] = value;
  });
  
  if (!isValid) return;
  
  // Update or add scores for this specific object only
  const existingScoreIndex = review.scores.findIndex(s => s.reviewed_object === objectId);
  
  if (existingScoreIndex !== -1) {
    // Update existing scores for this object
    console.log(`Updating existing scores at index ${existingScoreIndex}:`, scores);
    review.scores[existingScoreIndex].scores = scores;
  } else {
    // Add new scores for this object
    console.log('Adding new scores for object:', objectId);
    review.scores.push({
      reviewed_object: objectId,
      scores: scores
    });
  }
  
  // Update UI
  updateScoringStatus();
}

// Update the scoring status UI
function updateScoringStatus() {
  console.log('Updating scoring status');
  
  if (!review || !review.scores || !objects) {
    console.warn('Cannot update scoring status - missing required data', { 
      review: !!review, 
      scores: review ? !!review.scores : false, 
      objects: !!objects 
    });
    return;
  }
  
  const scoredObjects = new Set(review.scores.map(s => s.reviewed_object));
  const totalScored = scoredObjects.size;
  const totalObjects = objects.length;
  
  console.log(`Scored objects: ${totalScored}/${totalObjects}`);
  
  // Update completion count
  completionCount.textContent = `${totalScored}/${totalObjects} objects scored`;
  
  // Update status indicator
  if (totalScored === totalObjects) {
    statusIndicator.className = 'status-indicator status-complete';
    statusText.textContent = 'Complete';
  } else {
    statusIndicator.className = 'status-indicator status-incomplete';
    statusText.textContent = 'Incomplete';
  }
  
  // Update review status
  reviewStatusValue.textContent = review.status || 'open';
  
  // Enable/disable submit button
  submitButton.disabled = (totalScored < totalObjects) || !review.reviewer;
}