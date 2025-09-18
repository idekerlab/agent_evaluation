// Reviewer Interface - Data Module
// Handles data loading and manipulation

// Find an existing review_list or create a new one
async function findOrCreateReview() {
  try {
    // Search for existing review_lists for this object list
    const sql = `
      SELECT * FROM nodes 
      WHERE object_type = 'review_list' 
      AND json_extract(properties, '$.object_list_id') = '${objectListId}'
      AND json_extract(properties, '$.status') = 'open'
    `;
    
    console.log('Searching for existing review_list with SQL:', sql);
    
    const response = await fetch('/query_knowledge_graph_database', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ sql })
    });
    
    if (!response.ok) {
      throw new Error(`Error searching for review lists: ${response.statusText}`);
    }
    
    const reviews = await response.json();
    console.log('Found reviews:', reviews);
    
    if (reviews && reviews.length > 0) {
      // Use the first open review_list found
      const reviewData = reviews[0];
      const reviewProperties = JSON.parse(reviewData.properties);
      
      review = {
        object_id: reviewData.object_id,
        type: 'review_list',
        object_list_id: objectListId,
        object_ids: objectList.object_ids,
        reviewer: reviewProperties.reviewer || '',
        _criteria: objectList._criteria,
        status: 'open',
        scores: reviewProperties.scores || [],
        submit_date: ''
      };
      
      // Update UI with existing review data
      reviewerInput.value = review.reviewer;
      
    } else {
      // Create a new review_list
      review = {
        type: 'review_list',
        object_list_id: objectListId,
        object_ids: objectList.object_ids,
        reviewer: '',
        _criteria: objectList._criteria,
        status: 'open',
        scores: [],
        submit_date: ''
      };
      
      console.log('Creating new review_list:', review);
      
      // Save the new review_list to the database
      const createResponse = await fetch('/objects/review_list/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(review)
      });
      
      if (!createResponse.ok) {
        throw new Error(`Error creating review list: ${createResponse.statusText}`);
      }
      
      const createdReview = await createResponse.json();
      review.object_id = createdReview.object_id;
      
      console.log('Created review_list with ID:', review.object_id);
    }
    
  } catch (error) {
    console.error('Error in findOrCreateReview:', error);
    showNotification(`Error with review list: ${error.message}`, 'error');
  }
}

// Save the review
async function saveReview(isAutoSave = false) {
  try {
    // Save current scores
    saveCurrentScores();
    
    // Update review metadata
    review.reviewer = reviewerInput.value;
    
    console.log('Saving review_list:', review);
    
    // Use JSON submission for non-specified object types
    const response = await fetch(`/objects/review_list/${review.object_id}/edit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(review)
    });
    
    if (!response.ok) {
      throw new Error(`Error saving review list: ${response.statusText}`);
    }
    
    // Show success notification if not auto-save
    if (!isAutoSave) {
      showNotification('Review saved successfully!', 'success');
    }
    
    // Update UI
    updateScoringStatus();
    
  } catch (error) {
    console.error('Error in saveReview:', error);
    showNotification(`Error saving review: ${error.message}`, 'error');
  }
}

// Submit the review
async function submitReview() {
  try {
    // Save current scores first
    saveCurrentScores();
    
    // Update review metadata
    review.reviewer = reviewerInput.value;
    
    // Validate review
    if (!review.reviewer.trim()) {
      showNotification('Please enter your name in the Reviewer field before submitting.', 'error');
      return;
    }
    
    // Check if all objects have been scored
    const scoredObjects = new Set(review.scores.map(s => s.reviewed_object));
    const objectIds = new Set(objects.map(o => o.object_id));
    
    // Check if all objects have been scored
    let allScored = true;
    objectIds.forEach(id => {
      if (!scoredObjects.has(id)) {
        allScored = false;
      }
    });
    
    if (!allScored) {
      showNotification('Please score all objects before submitting the review.', 'error');
      return;
    }
    
    // Ask for confirmation
    if (!confirm('Are you sure you want to submit this review? You will not be able to edit it after submission.')) {
      return;
    }
    
    // Update review status
    review.status = 'submitted';
    review.submit_date = new Date().toISOString();
    
    console.log('Submitting review_list:', review);
    
    // Use JSON submission for non-specified object types
    const response = await fetch(`/objects/review_list/${review.object_id}/edit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(review)
    });
    
    if (!response.ok) {
      throw new Error(`Error submitting review: ${response.statusText}`);
    }
    
    // Show success notification
    showNotification('Review submitted successfully!', 'success');
    
    // Disable form inputs
    disableFormInputs();
    
    // Update UI
    reviewStatusValue.textContent = 'submitted';
    submitButton.disabled = true;
    saveButton.disabled = true;
    
  } catch (error) {
    console.error('Error in submitReview:', error);
    showNotification(`Error submitting review: ${error.message}`, 'error');
  }
}

// Export the review, object list, and objects as JSON
async function exportReview() {
  try {
    // Save current scores first to ensure everything is up to date
    saveCurrentScores();
    
    // Prepare the export data
    const exportData = {
      review: review,
      object_list: objectList,
      objects: objects
    };
    
    console.log('Exporting review data:', exportData);
    
    // Convert to JSON
    const jsonData = JSON.stringify(exportData, null, 2);
    
    // Create a blob and download link
    const blob = new Blob([jsonData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    // Create a filename with the review ID and timestamp
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `review_${review.object_id}_${timestamp}.json`;
    
    // Create a temporary link element to trigger the download
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.style.display = 'none';
    
    // Add to the document, click, and remove
    document.body.appendChild(link);
    link.click();
    
    // Cleanup
    setTimeout(() => {
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }, 100);
    
    showNotification('Review exported successfully!', 'success');
    
  } catch (error) {
    console.error('Error in exportReview:', error);
    showNotification(`Error exporting review: ${error.message}`, 'error');
  }
}

// Disable all form inputs
function disableFormInputs() {
  // Disable reviewer input
  reviewerInput.disabled = true;
  
  // Disable all scoring form inputs
  const formInputs = scoringFormContainer.querySelectorAll('input, textarea, select');
  formInputs.forEach(input => {
    input.disabled = true;
  });
}