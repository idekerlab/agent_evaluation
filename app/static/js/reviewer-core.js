// Reviewer Interface - Core Module
// Handles initialization and main functionality

// State
let objectListId = null;
let objectList = null;
let objects = [];
let currentObjectIndex = 0;
let review = null;
let autoSaveTimeout = null;

// DOM Elements
let objectContainer, scoringFormContainer, reviewerInput;
let prevButton, nextButton, saveButton, submitButton, navInfo;
let statusIndicator, statusText, completionCount, reviewStatusValue;
let notificationContainer;

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM content loaded');
  
  // Get URL parameters
  const urlParams = new URLSearchParams(window.location.search);
  objectListId = urlParams.get('object_list_id');
  
  console.log('Object List ID:', objectListId);
  
  if (!objectListId) {
    showNotification('No object list ID provided. Please select an object list to review.', 'error');
    return;
  }
  
  // Get DOM elements
  objectContainer = document.getElementById('object-container');
  scoringFormContainer = document.getElementById('scoring-form-container');
  reviewerInput = document.getElementById('reviewer-input');
  prevButton = document.getElementById('prev-button');
  nextButton = document.getElementById('next-button');
  saveButton = document.getElementById('save-button');
  submitButton = document.getElementById('submit-button');
  navInfo = document.getElementById('nav-info');
  statusIndicator = document.getElementById('status-indicator');
  statusText = document.getElementById('status-text');
  completionCount = document.getElementById('completion-count');
  reviewStatusValue = document.getElementById('review-status-value');
  notificationContainer = document.getElementById('notification-container');
  
  // Set up event listeners
  prevButton.addEventListener('click', goToPreviousObject);
  nextButton.addEventListener('click', goToNextObject);
  saveButton.addEventListener('click', () => saveReview(false));
  submitButton.addEventListener('click', submitReview);
  
  // Set up auto-save
  reviewerInput.addEventListener('input', scheduleAutoSave);
  
  // Load the object list and initialize the review
  initializeReview();
});

// Initialize the review
async function initializeReview() {
  try {
    console.log('Initializing review...');
    
    // Fetch the object list
    console.log('Fetching object list:', objectListId);
    const objectListResponse = await fetch(`/objects/object_list/${objectListId}`);
    if (!objectListResponse.ok) {
      throw new Error(`Failed to fetch object list: ${objectListResponse.statusText}`);
    }
    
    const objectListData = await objectListResponse.json();
    objectList = objectListData.object;
    
    console.log('Object list data:', objectList);
    
    if (!objectList.object_ids || !Array.isArray(objectList.object_ids) || objectList.object_ids.length === 0) {
      throw new Error('Object list does not contain any objects to review.');
    }
    
    // Check if the object list has criteria
    if (!objectList._criteria || !Array.isArray(objectList._criteria) || objectList._criteria.length === 0) {
      showNotification('Warning: Object list does not define any scoring criteria.', 'warning');
    }
    
    // Fetch all objects in the list
    console.log('Fetching objects with IDs:', objectList.object_ids);
    objects = []; // Reset objects array
    
    // Create an array of promises for fetching each object directly
    const objectPromises = objectList.object_ids.map(async (objectId) => {
      try {
        const response = await fetch(`/objects/objects/${objectId}`);
        if (!response.ok) {
          console.error(`Failed to fetch object ${objectId}: ${response.statusText}`);
          return null;
        }
        const data = await response.json();
        return data.object;
      } catch (error) {
        console.error(`Error fetching object ${objectId}:`, error);
        return null;
      }
    });
    
    // Wait for all fetch operations to complete
    const results = await Promise.all(objectPromises);
    
    // Filter out any null results
    objects = results.filter(obj => obj !== null);
    
    console.log('Fetched objects:', objects);
    
    if (objects.length === 0) {
      throw new Error('Could not fetch any objects to review.');
    }
    
    // Check if a review already exists for this object list
    console.log('Finding or creating review...');
    await findOrCreateReview();
    
    // Update UI
    updateNavigation();
    updateScoringStatus();
    
    // Display the first object
    console.log('Displaying first object...');
    displayObject(currentObjectIndex);
    
    // Generate the scoring form
    console.log('Generating scoring form...');
    generateScoringForm();
    
    console.log('Initialization complete.');
    
  } catch (error) {
    console.error('Error in initializeReview:', error);
    showNotification(`Error initializing review: ${error.message}`, 'error');
    objectContainer.innerHTML = `<div class="notification error">Error: ${error.message}</div>`;
  }
}

// Go to the previous object
function goToPreviousObject() {
  if (currentObjectIndex > 0) {
    saveCurrentScores(); // Save scores before changing objects
    currentObjectIndex--;
    displayObject(currentObjectIndex);
    updateNavigation();
  }
}

// Go to the next object
function goToNextObject() {
  if (currentObjectIndex < objects.length - 1) {
    saveCurrentScores(); // Save scores before changing objects
    currentObjectIndex++;
    displayObject(currentObjectIndex);
    updateNavigation();
  }
}

// Update navigation controls and info
function updateNavigation() {
  navInfo.textContent = `Object ${currentObjectIndex + 1} of ${objects.length}`;
  
  // Disable/enable navigation buttons based on current index
  prevButton.disabled = currentObjectIndex === 0;
  nextButton.disabled = currentObjectIndex === objects.length - 1;
}

// Schedule auto-save
function scheduleAutoSave() {
  // Clear any existing timeout
  if (autoSaveTimeout) {
    clearTimeout(autoSaveTimeout);
  }
  
  // Set new timeout for 2 seconds after the last change
  autoSaveTimeout = setTimeout(() => {
    saveReview(true); // true indicates this is an auto-save
  }, 2000);
}

// Helper function to show loading spinner
function showLoading(container) {
  container.innerHTML = '<div class="spinner"></div><div>Loading object details...</div>';
}

// Show a notification message
function showNotification(message, type = 'info') {
  console.log(`Notification (${type}):`, message);
  
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `notification ${type}`;
  notification.textContent = message;
  
  // Add to notification container
  notificationContainer.prepend(notification);
  
  // Remove after a delay (except for errors)
  if (type !== 'error') {
    setTimeout(() => {
      notification.remove();
    }, 5000);
  }
}