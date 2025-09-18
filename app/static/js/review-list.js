/**
 * Review List Viewer with Modal Selection
 * Displays review lists in a read-only interface with export functionality
 */

// Global state
let currentReviewListData = null;
let selectedReviewIndex = null;
let currentReviews = []; // Store the loaded reviews for export

// DOM Elements
let reviewTableBody, detailsContainer, exportButton;
let selectReviewListBtn, modal, modalClose, modalLoading, reviewListsContainer, reviewListsTableBody;

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
  // Get DOM elements
  reviewTableBody = document.getElementById('review-table-body');
  detailsContainer = document.getElementById('details-container');
  exportButton = document.getElementById('export-button');
  selectReviewListBtn = document.getElementById('select-review-list-btn');
  
  // Modal elements
  modal = document.getElementById('review-list-modal');
  modalClose = document.querySelector('.close');
  modalLoading = document.getElementById('modal-loading');
  reviewListsContainer = document.getElementById('review-lists-container');
  reviewListsTableBody = document.getElementById('review-lists-table-body');
  
  // Set up event listeners
  selectReviewListBtn.addEventListener('click', openModal);
  modalClose.addEventListener('click', closeModal);
  exportButton.addEventListener('click', exportReviewList);
  
  // Close modal when clicking outside of it
  window.addEventListener('click', (event) => {
    if (event.target === modal) {
      closeModal();
    }
  });
  
  // Close modal with Escape key
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && modal.style.display === 'flex') {
      closeModal();
    }
  });
  
  // Show initial empty state
  showEmptyState();
});

// Open the review list selection modal
function openModal() {
  modal.style.display = 'flex';
  modalLoading.style.display = 'flex';
  reviewListsContainer.style.display = 'none';
  
  // Fetch available review lists
  fetchReviewLists();
}

// Close the modal
function closeModal() {
  modal.style.display = 'none';
}

// Fetch all available review lists
async function fetchReviewLists() {
  try {
    // Query for all review_list objects
    const response = await fetch('/query_knowledge_graph_database', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        sql: "SELECT object_id, properties FROM nodes WHERE object_type = 'review_list' ORDER BY json_extract(properties, '$.created') DESC"
      })
    });
    
    if (!response.ok) {
      throw new Error(`Error fetching review lists: ${response.statusText}`);
    }
    
    const data = await response.json();
    displayReviewLists(data);
    
  } catch (error) {
    console.error('Error fetching review lists:', error);
    modalLoading.innerHTML = `<div class="notification error">Error loading review lists: ${error.message}</div>`;
  }
}

// Display review lists in the modal table
function displayReviewLists(reviewLists) {
  modalLoading.style.display = 'none';
  reviewListsContainer.style.display = 'block';
  
  reviewListsTableBody.innerHTML = '';
  
  if (!reviewLists || reviewLists.length === 0) {
    document.getElementById('no-review-lists').style.display = 'block';
    return;
  }
  
  reviewLists.forEach(reviewList => {
    const properties = JSON.parse(reviewList.properties);
    const row = document.createElement('tr');
    
    // Format the date for display
    const createdDate = properties.created || 'Unknown';
    const reviewer = properties.reviewer || 'Unknown';
    
    row.innerHTML = `
      <td>${reviewList.object_id}</td>
      <td>${reviewer}</td>
      <td>${createdDate}</td>
      <td><button class="select-button" onclick="selectReviewList('${reviewList.object_id}')">Select</button></td>
    `;
    
    reviewListsTableBody.appendChild(row);
  });
}

// Select a review list and load its data
async function selectReviewList(reviewListId) {
  closeModal();
  
  try {
    showLoading();
    
    // Fetch the review list object
    const response = await fetch(`/objects/review_list/${reviewListId}`);
    
    if (!response.ok) {
      throw new Error(`Error fetching review list: ${response.statusText}`);
    }
    
    const data = await response.json();
    currentReviewListData = data;
    
    // Update metadata
    updateMetadata(data.object);
    
    // Load reviews for this review list
    await loadReviews(data.object);
    
  } catch (error) {
    console.error('Error loading review list:', error);
    showError(`Error loading review list: ${error.message}`);
  }
}

// Update the metadata bar with review list information
function updateMetadata(reviewListData) {
  document.getElementById('reviewer-name').textContent = reviewListData.reviewer || '-';
  document.getElementById('object-id').textContent = reviewListData.object_id || '-';
  document.getElementById('linked-list-id').textContent = reviewListData.linked_object_list_id || '-';
  document.getElementById('created-date').textContent = reviewListData.created || '-';
}

// Load reviews for the selected review list
async function loadReviews(reviewListData) {
  try {
    // First, get the object_list that this review_list references
    const objectListId = reviewListData.object_list_id;
    
    if (!objectListId) {
      console.error('No object_list_id found in review_list');
      currentReviews = [];
      showEmptyReviews();
      return;
    }
    
    // Fetch the object_list
    const objectListResponse = await fetch(`/objects/object_list/${objectListId}`);
    if (!objectListResponse.ok) {
      throw new Error(`Error fetching object_list ${objectListId}: ${objectListResponse.statusText}`);
    }
    
    const objectListData = await objectListResponse.json();
    const objectIds = objectListData.object.object_ids || [];
    
    if (objectIds.length === 0) {
      currentReviews = [];
      showEmptyReviews();
      return;
    }
    
    // Fetch all objects referenced in the object_list
    const reviewedObjects = [];
    for (const objectId of objectIds) {
      try {
        // Try to determine object type and fetch accordingly
        const response = await fetch(`/objects/objects/${objectId}`);
        if (response.ok) {
          const objectData = await response.json();
          
          // Find the corresponding review score from the review_list
          const reviewScore = reviewListData.scores?.find(score => 
            score.reviewed_object === objectId
          );
          
          // Combine object data with review information
          const reviewedObject = {
            object_id: objectId,
            object_type: objectData.object_type,
            object_data: objectData.object,
            reviewer: reviewListData.reviewer,
            review_scores: reviewScore?.scores || {},
            review_comments: reviewScore?.scores?.comments || '',
            // Extract key fields for display
            bel_expression: objectData.object.bel_expression || 'N/A',
            interaction: objectData.object.interaction || 'N/A',
            evidence: objectData.object.evidence || 'N/A',
            text: objectData.object.text || 'N/A',
            reviewed_object_id: objectId
          };
          
          reviewedObjects.push(reviewedObject);
        } else {
          console.error(`Failed to fetch object ${objectId}: ${response.statusText}`);
        }
      } catch (error) {
        console.error(`Error fetching object ${objectId}:`, error);
      }
    }
    
    // Store reviewed objects globally for export
    currentReviews = reviewedObjects;
    
    displayReviews(reviewedObjects);
    
  } catch (error) {
    console.error('Error loading reviews:', error);
    showError(`Error loading reviews: ${error.message}`);
  }
}

// Display reviews in the summary table
function displayReviews(reviews) {
  reviewTableBody.innerHTML = '';
  
  if (reviews.length === 0) {
    showEmptyReviews();
    return;
  }
  
  // Hide the empty state and show the table
  document.getElementById('no-reviews').style.display = 'none';
  document.querySelector('.review-table').style.display = 'table';
  
  reviews.forEach((review, index) => {
    // Calculate a simple score indicator based on review scores
    let scoreIndicator = 'N/A';
    if (review.review_scores) {
      if (review.review_scores.all_correct) {
        scoreIndicator = '✓ Correct';
      } else {
        const errorTypes = Object.keys(review.review_scores).filter(key => 
          key !== 'all_correct' && key !== 'comments' && review.review_scores[key] === true
        );
        if (errorTypes.length > 0) {
          scoreIndicator = `✗ ${errorTypes.length} issue${errorTypes.length > 1 ? 's' : ''}`;
        }
      }
    }
    
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${review.object_id || 'N/A'}</td>
      <td>${review.reviewer || 'N/A'}</td>
      <td class="review-score">${scoreIndicator}</td>
      <td>${review.reviewed_object_id || 'N/A'}</td>
    `;
    
    // Add click event to show review details
    row.addEventListener('click', () => {
      selectReview(index, review);
    });
    
    reviewTableBody.appendChild(row);
  });
}

// Select and display a specific review
function selectReview(index, reviewData) {
  // Remove previous selection
  const previouslySelected = reviewTableBody.querySelector('.selected');
  if (previouslySelected) {
    previouslySelected.classList.remove('selected');
  }
  
  // Add selection to current row
  const rows = reviewTableBody.querySelectorAll('tr');
  if (rows[index]) {
    rows[index].classList.add('selected');
  }
  
  selectedReviewIndex = index;
  displayReviewDetails(reviewData);
}

// Display detailed information for the selected review
function displayReviewDetails(review) {
  const truncateText = (text, maxLines = 2) => {
    if (!text) return 'N/A';
    const lines = text.split('\n');
    if (lines.length <= maxLines) return text;
    return lines.slice(0, maxLines).join('\n') + '...';
  };
  
  // Generate review scores display
  let reviewScoresHtml = '';
  if (review.review_scores && Object.keys(review.review_scores).length > 0) {
    const scores = review.review_scores;
    reviewScoresHtml = `
      <div class="property-item">
        <div class="property-label">Review Scores:</div>
        <div class="property-value">
          <div class="review-scores">
            ${scores.all_correct ? '<span class="score-correct">✓ All Correct</span>' : ''}
            ${scores.correct_but_could_be_more_precise ? '<span class="score-issue">⚠ Could be more precise</span>' : ''}
            ${scores.posttranslational_modification_errors ? '<span class="score-error">✗ Post-translational modification errors</span>' : ''}
            ${scores.interaction_type_errors ? '<span class="score-error">✗ Interaction type errors</span>' : ''}
            ${scores.identifier_database_errors ? '<span class="score-error">✗ Identifier database errors</span>' : ''}
            ${scores.incorrect_entities ? '<span class="score-error">✗ Incorrect entities</span>' : ''}
            ${scores.incorrect_order_source_and_target_switched ? '<span class="score-error">✗ Source/target switched</span>' : ''}
            ${scores.not_a_valid_relationshiptype ? '<span class="score-error">✗ Invalid relationship type</span>' : ''}
            ${scores.other_errors ? '<span class="score-error">✗ Other errors</span>' : ''}
          </div>
        </div>
      </div>
    `;
    
    if (scores.comments) {
      reviewScoresHtml += `
        <div class="property-item">
          <div class="property-label">Review Comments:</div>
          <div class="property-value">${scores.comments}</div>
        </div>
      `;
    }
  }
  
  detailsContainer.innerHTML = `
    <div class="review-header">
      <div class="reviewer-name">${review.reviewer || 'Unknown Reviewer'}</div>
      <div class="review-score-display">Object Type: ${review.object_type || 'N/A'}</div>
    </div>
    
    <div class="property-list">
      <div class="property-item">
        <div class="property-label">BEL Expression:</div>
        <div class="property-value">${review.bel_expression || 'N/A'}</div>
      </div>
      
      <div class="property-item">
        <div class="property-label">Interaction:</div>
        <div class="property-value">${review.interaction || 'N/A'}</div>
      </div>
      
      <div class="property-item">
        <div class="property-label">Evidence:</div>
        <div class="property-value">${review.evidence || 'N/A'}</div>
      </div>
      
      <div class="property-item">
        <div class="property-label">Text:</div>
        <div class="property-value text-truncated">${truncateText(review.text)}</div>
      </div>
      
      <div class="property-item">
        <div class="property-label">Reviewed Object ID:</div>
        <div class="property-value">${review.reviewed_object_id || 'N/A'}</div>
      </div>
      
      ${reviewScoresHtml}
    </div>
  `;
}

// Export the current review list as JSON with detailed review data
async function exportReviewList() {
  if (!currentReviewListData) {
    alert('No review list loaded to export');
    return;
  }
  
  try {
    // Helper function to truncate text to first 2 lines
    const truncateText = (text, maxLines = 2) => {
      if (!text) return 'N/A';
      const lines = text.split('\n');
      if (lines.length <= maxLines) return text;
      return lines.slice(0, maxLines).join('\n') + '...';
    };
    
    const exportData = {
      metadata: {
        reviewer: currentReviewListData.object.reviewer,
        object_id: currentReviewListData.object.object_id,
        linked_object_list_id: currentReviewListData.object.linked_object_list_id,
        created: currentReviewListData.object.created,
        exported_at: new Date().toISOString()
      },
      review_list: currentReviewListData.object,
      review_count: currentReviews.length,
      reviews: []
    };
    
    // Add detailed review data for each review
    for (const review of currentReviews) {
      const reviewDetail = {
        review_id: review.object_id || 'N/A',
        reviewer: review.reviewer || 'N/A',
        object_type: review.object_type || 'N/A',
        bel_expression: review.bel_expression || 'N/A',
        interaction: review.interaction || 'N/A',
        evidence: review.evidence || 'N/A',
        text: truncateText(review.text), // Truncated to 2 lines as requested
        reviewed_object_id: review.reviewed_object_id || 'N/A',
        review_scores: review.review_scores || {},
        review_comments: review.review_comments || 'N/A'
      };
      
      exportData.reviews.push(reviewDetail);
    }
    
    const dataStr = JSON.stringify(exportData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `review_list_detailed_${currentReviewListData.object.object_id}_${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    
    // Show success notification
    showNotification(`Review list with ${currentReviews.length} detailed reviews exported successfully!`, 'success');
    
  } catch (error) {
    console.error('Error exporting review list:', error);
    showNotification('Error exporting review list', 'error');
  }
}

// Show loading state
function showLoading() {
  reviewTableBody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 20px;">Loading...</td></tr>';
  detailsContainer.innerHTML = '<div class="notification info">Loading review details...</div>';
}

// Show error state
function showError(message) {
  reviewTableBody.innerHTML = `<tr><td colspan="4" style="text-align: center; padding: 20px; color: red;">${message}</td></tr>`;
  detailsContainer.innerHTML = `<div class="notification error">${message}</div>`;
}

// Show empty state
function showEmptyState() {
  document.querySelector('.review-table').style.display = 'none';
  document.getElementById('no-reviews').style.display = 'block';
  detailsContainer.innerHTML = '<div class="notification info">Select a review list to view details</div>';
}

// Show empty reviews state
function showEmptyReviews() {
  reviewTableBody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 20px;">No reviews found in this list</td></tr>';
  detailsContainer.innerHTML = '<div class="notification info">No reviews available</div>';
}

// Show notification
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `notification ${type}`;
  notification.textContent = message;
  notification.style.position = 'fixed';
  notification.style.top = '20px';
  notification.style.right = '20px';
  notification.style.zIndex = '1001';
  notification.style.padding = '10px 20px';
  notification.style.borderRadius = '4px';
  notification.style.color = 'white';
  notification.style.backgroundColor = type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3';
  
  document.body.appendChild(notification);
  
  setTimeout(() => {
    if (notification.parentNode) {
      notification.parentNode.removeChild(notification);
    }
  }, 3000);
}

// Make selectReviewList available globally for onclick handlers
window.selectReviewList = selectReviewList;
