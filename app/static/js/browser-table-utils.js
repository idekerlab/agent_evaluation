/**
 * Browser Table Utility Functions
 * Helper functions for creating and managing tables and visualizations
 */

// Helper function to check if value is a 2D array with consistent row lengths
function is2DArray(value) {
  // Check if it's an array first
  if (!Array.isArray(value)) return false;
  
  // Check if all elements are arrays
  const allArrays = value.every(item => Array.isArray(item));
  if (!allArrays) return false;
  
  // Check if all subarrays have the same length
  if (value.length === 0) return false;
  
  const firstLength = value[0].length;
  const allSameLength = value.every(arr => arr.length === firstLength);
  
  return allSameLength;
}

// Function to create a table from a 2D array
function createTableFromArray(arr) {
  const csvContainer = document.createElement('div');
  csvContainer.className = 'csv-table';
  
  const table = document.createElement('table');
  
  // Create header row (using first row of array)
  const thead = document.createElement('thead');
  const headerRow = document.createElement('tr');
  
  arr[0].forEach(cell => {
    const th = document.createElement('th');
    th.textContent = cell !== null && cell !== undefined ? String(cell).trim() : '';
    headerRow.appendChild(th);
  });
  
  thead.appendChild(headerRow);
  table.appendChild(thead);
  
  // Create table body rows (rest of the array)
  const tbody = document.createElement('tbody');
  
  for (let i = 1; i < arr.length; i++) {
    const tr = document.createElement('tr');
    
    arr[i].forEach(cell => {
      const td = document.createElement('td');
      td.textContent = cell !== null && cell !== undefined ? String(cell).trim() : '';
      tr.appendChild(td);
    });
    
    tbody.appendChild(tr);
  }
  
  table.appendChild(tbody);
  csvContainer.appendChild(table);
  
  return csvContainer;
}

// Function to create sortable table headers
function createSortableHeader(header) {
  const th = document.createElement('th');
  th.className = 'sortable-header';
  th.setAttribute('data-header', header);
  
  // Create a simple text node for the header label
  const labelText = document.createTextNode(header);
  th.appendChild(labelText);
  
  // Create the sort button
  const sortButton = document.createElement('button');
  sortButton.className = 'sort-button';
  sortButton.innerHTML = '<i class="fas fa-sort-alpha-up"></i>';
  
  // Add click event for sorting
  sortButton.addEventListener('click', (e) => {
    e.stopPropagation();
    sortAndRender(header);
  });
  
  // Add the button after the text
  th.appendChild(sortButton);
  
  return th;
}

// Function to create CSV table from string
function createCSVTable(value) {
  try {
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
      csvContainer.appendChild(table);
      return csvContainer;
    }
  } catch (e) {
    // Return null if CSV parsing fails
    return null;
  }
  return null;
}
