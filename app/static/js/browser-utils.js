/**
 * Browser Utility Functions
 * Helper functions for date parsing, text formatting, and other utilities
 */

// Helper function to format long text
function formatLongText(text, maxLength = 35) {
  if (!text) return '';
  text = String(text);
  
  if (text.length <= maxLength) return text;
  
  // If text contains underscores, try to break it at a logical point
  if (text.includes('_')) {
    const parts = text.split('_');
    
    // If there are just a few parts, try to keep the first and last parts
    if (parts.length <= 3) {
      const firstPart = parts[0];
      const lastPart = parts[parts.length - 1];
      
      // If first + last would fit with ellipsis between
      if (firstPart.length + lastPart.length + 3 <= maxLength) {
        return firstPart + '...' + lastPart;
      }
    }
    
    // Otherwise build up from the start
    let result = parts[0];
    let currentLength = result.length;
    
    // Add parts until we approach the max length
    for (let i = 1; i < parts.length; i++) {
      if (currentLength + parts[i].length + 1 > maxLength - 3) {
        return result + '...';
      }
      result += '_' + parts[i];
      currentLength = result.length;
    }
    
    return result;
  }
  
  // Simple truncation with ellipsis
  return text.substring(0, maxLength - 3) + '...';
}

// Helper function to parse date strings in format "mm-dd-yyyy hh:mm:ss" or "yyyy-mm-dd hh:mm:ss"
function parseDate(dateStr) {
  if (!dateStr) return null;
  
  // Try to determine the format based on the string
  let parts;
  let year, month, day, hours, minutes, seconds;
  
  // Check for mm.dd.yyyy format (with dots)
  if (dateStr.includes('.')) {
    parts = dateStr.split(/[\.\s:]/);
    month = parseInt(parts[0], 10);
    day = parseInt(parts[1], 10);
    year = parseInt(parts[2], 10);
    hours = parts.length > 3 ? parseInt(parts[3], 10) : 0;
    minutes = parts.length > 4 ? parseInt(parts[4], 10) : 0;
    seconds = parts.length > 5 ? parseInt(parts[5], 10) : 0;
  }
  // Check for mm-dd-yyyy format (with hyphens)
  else if (dateStr.includes('-') && dateStr.indexOf('-') < 3) {
    parts = dateStr.split(/[-\s:]/);
    month = parseInt(parts[0], 10);
    day = parseInt(parts[1], 10);
    year = parseInt(parts[2], 10);
    hours = parts.length > 3 ? parseInt(parts[3], 10) : 0;
    minutes = parts.length > 4 ? parseInt(parts[4], 10) : 0;
    seconds = parts.length > 5 ? parseInt(parts[5], 10) : 0;
  }
  // Assume yyyy-mm-dd format (standard ISO-like)
  else if (dateStr.includes('-')) {
    parts = dateStr.split(/[-\s:]/);
    year = parseInt(parts[0], 10);
    month = parseInt(parts[1], 10);
    day = parseInt(parts[2], 10);
    hours = parts.length > 3 ? parseInt(parts[3], 10) : 0;
    minutes = parts.length > 4 ? parseInt(parts[4], 10) : 0;
    seconds = parts.length > 5 ? parseInt(parts[5], 10) : 0;
  }
  // Handle slash-separated dates (mm/dd/yyyy)
  else if (dateStr.includes('/')) {
    parts = dateStr.split(/[\/\s:]/);
    month = parseInt(parts[0], 10);
    day = parseInt(parts[1], 10);
    year = parseInt(parts[2], 10);
    hours = parts.length > 3 ? parseInt(parts[3], 10) : 0;
    minutes = parts.length > 4 ? parseInt(parts[4], 10) : 0;
    seconds = parts.length > 5 ? parseInt(parts[5], 10) : 0;
  }
  // If none of the above formats match, try creating a date directly
  else {
    return new Date(dateStr);
  }
  
  // JavaScript months are 0-indexed (0-11)
  return new Date(year, month - 1, day, hours, minutes, seconds);
}

// Helper function to show loading spinner
function showLoading(container) {
  container.innerHTML = '<div class="spinner"></div>';
}

// Helper function to show error message
function showError(container, message) {
  container.innerHTML = `<div class="notification error">${message}</div>`;
}

// Helper function to reset the Object Details panel header
function resetObjectDetailsHeader() {
  const panelHeader = document.querySelector('.right-panel .panel-header');
  if (panelHeader) {
    panelHeader.innerHTML = 'Object Details';
  }
}
