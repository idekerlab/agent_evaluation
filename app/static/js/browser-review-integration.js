/**
 * Review Integration for Browser Interface
 * Functions to open review interfaces and review list viewers
 */

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

// Open review list viewer in a new tab
function openReviewListViewer(reviewListId) {
  // Create a notification to show that we're opening the review list viewer
  const notification = document.createElement('div');
  notification.className = 'notification success';
  notification.textContent = 'Opening review list viewer in a new tab...';
  
  // Add notification above the buttons
  const actionButtons = document.querySelector('.action-buttons');
  if (actionButtons && actionButtons.parentNode) {
    actionButtons.parentNode.insertBefore(notification, actionButtons);
  }
  
  // Open the review list viewer in a new tab - using relative path to review_list.html
  window.open(`review_list.html?review_list_id=${reviewListId}`, '_blank');
  
  // Remove the notification after a few seconds
  setTimeout(() => {
    if (notification.parentNode) {
      notification.remove();
    }
  }, 3000);
}
