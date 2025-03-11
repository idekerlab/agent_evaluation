/**
 * NDEx Import UI Module
 * 
 * This module handles the UI interactions for the NDEx to Deckhard importer.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const uuidInput = document.getElementById('ndex-uuid');
    const fetchButton = document.getElementById('fetch-network-btn');
    const networkPreview = document.getElementById('network-preview');
    const previewContent = document.getElementById('preview-content');
    const importOptions = document.getElementById('import-options');
    const networkNameInput = document.getElementById('network-name');
    const criteriaPreview = document.getElementById('criteria-preview');
    const criteriaContent = document.getElementById('criteria-content');
    const importForm = document.getElementById('import-form');
    const resultsContainer = document.getElementById('results-container');
    const notificationContainer = document.getElementById('notification-container');
    const testFetchBtn = document.getElementById('test-fetch-btn');
    const testProxyBtn = document.getElementById('test-proxy-btn');
    
    // State variables
    let networkData = null;
    let fullNetworkData = null;
    let scoringCriteria = null;
    
    // Add event listeners
    fetchButton.addEventListener('click', fetchNetworkHandler);
    importForm.addEventListener('submit', importNetworkHandler);
    
    // Test buttons
    testFetchBtn.addEventListener('click', testFetchHandler);
    testProxyBtn.addEventListener('click', testProxyHandler);
    
    // Handle enter key in the UUID input
    uuidInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            fetchNetworkHandler(e);
        }
    });
    
    /**
     * Validate UUID format
     * @param {string} uuid - The UUID to validate
     * @returns {boolean} - True if valid UUID format
     */
    function validateUUID(uuid) {
        const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
        return uuidRegex.test(uuid);
    }
    
    /**
     * Test direct fetch button handler
     */
    async function testFetchHandler() {
        const uuid = uuidInput.value.trim();
        if (!uuid) {
            alert('Please enter a UUID first');
            return;
        }
        
        showLoading(resultsContainer);
        
        try {
            const data = await ndexClient.testFetchNetwork(uuid);
            
            const html = `
                <div class="object-view">
                    <h3>Direct Fetch Test Result (Success)</h3>
                    <div class="notification success">Successfully fetched network details directly</div>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                </div>
            `;
            resultsContainer.innerHTML = html;
        } catch (error) {
            const html = `
                <div class="object-view">
                    <h3>Direct Fetch Test Result (Failed)</h3>
                    <div class="notification error">${error.message}</div>
                </div>
            `;
            resultsContainer.innerHTML = html;
        }
    }
    
    /**
     * Test proxy fetch button handler
     */
    async function testProxyHandler() {
        const uuid = uuidInput.value.trim();
        if (!uuid) {
            alert('Please enter a UUID first');
            return;
        }
        
        showLoading(resultsContainer);
        
        try {
            const data = await ndexClient.testProxyFetch(uuid);
            
            const html = `
                <div class="object-view">
                    <h3>Proxy Fetch Test Result (Success)</h3>
                    <div class="notification success">Successfully fetched network details via proxy</div>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                </div>
            `;
            resultsContainer.innerHTML = html;
        } catch (error) {
            const html = `
                <div class="object-view">
                    <h3>Proxy Fetch Test Result (Failed)</h3>
                    <div class="notification error">${error.message}</div>
                </div>
            `;
            resultsContainer.innerHTML = html;
        }
    }
    
    /**
     * Handle fetch network button click
     * @param {Event} event - Click event
     */
    async function fetchNetworkHandler(event) {
        event.preventDefault();
        
        // Clear previous notifications
        notificationContainer.innerHTML = '';
        
        const uuid = uuidInput.value.trim();
        if (!uuid) {
            showNotification('Please enter a valid UUID', 'error');
            return;
        }
        
        // Reset UI
        networkPreview.classList.add('hidden');
        importOptions.classList.add('hidden');
        criteriaPreview.classList.add('hidden');
        
        // Show loading state
        fetchButton.disabled = true;
        fetchButton.textContent = 'Fetching...';
        showLoading(previewContent);
        
        try {
            // Validate UUID format
            if (!validateUUID(uuid)) {
                throw new Error('Invalid UUID format. Please enter a valid NDEx UUID.');
            }
            
            console.log("Attempting to fetch network with UUID:", uuid);
            
            // First, fetch the network summary for quick display
            try {
                networkData = await ndexClient.getNetworkSummary(uuid);
                console.log("Successfully retrieved network summary:", networkData);
                
                // Then fetch the full network data in the background
                try {
                    showNotification('Fetching full network data...', 'info');
                    fullNetworkData = await ndexClient.getFullNetwork(uuid);
                    console.log("Successfully retrieved full network data");
                    showNotification('Successfully fetched full network data', 'success');
                } catch (fullNetworkError) {
                    console.error("Error fetching full network:", fullNetworkError);
                    showNotification('Failed to fetch full network data. Import may be limited.', 'warning');
                }
            } catch (fetchError) {
                console.error("Error fetching network:", fetchError);
                throw new Error(`Failed to fetch network: ${fetchError.message}`);
            }
            
            // Check network size
            const nodeCount = networkData.nodeCount || (fullNetworkData?.nodes?.length || 0);
            const edgeCount = networkData.edgeCount || (fullNetworkData?.edges?.length || 0);
            
            if (nodeCount > 100 && edgeCount > 100) {
                showNotification('Network too large: both nodes and edges exceed 100 limit. This network cannot be imported.', 'warning');
            }
            
            // Extract network properties
            const properties = ndexClient.extractNetworkProperties(networkData);
            
            // Display network preview
            const html = `
                <table class="result-table">
                    <tbody>
                        <tr>
                            <td><strong>Name:</strong></td>
                            <td>${properties.name || 'Unnamed Network'}</td>
                        </tr>
                        <tr>
                            <td><strong>Description:</strong></td>
                            <td>${properties.description || 'No description'}</td>
                        </tr>
                        <tr>
                            <td><strong>Nodes:</strong></td>
                            <td>${nodeCount} ${nodeCount > 100 ? '<span class="notification warning" style="padding:2px 5px; margin:0;">exceeds limit</span>' : ''}</td>
                        </tr>
                        <tr>
                            <td><strong>Edges:</strong></td>
                            <td>${edgeCount} ${edgeCount > 100 ? '<span class="notification warning" style="padding:2px 5px; margin:0;">exceeds limit</span>' : ''}</td>
                        </tr>
                        <tr>
                            <td><strong>Owner:</strong></td>
                            <td>${properties.owner || 'Unknown'}</td>
                        </tr>
                        <tr>
                            <td><strong>Created:</strong></td>
                            <td>${new Date(properties.creationTime).toLocaleString()}</td>
                        </tr>
                    </tbody>
                </table>
            `;
            
            previewContent.innerHTML = html;
            networkPreview.classList.remove('hidden');
            
            // Set network name in form
            networkNameInput.value = properties.name || 'Unnamed Network';
            
            // Check for scoring criteria
            try {
                scoringCriteria = ndexClient.getScoringCriteria(networkData);
                
                if (scoringCriteria) {
                    criteriaContent.textContent = JSON.stringify(scoringCriteria, null, 2);
                    criteriaPreview.classList.remove('hidden');
                    
                    // Validate criteria
                    if (!deckhardClient.validateScoringCriteria(scoringCriteria)) {
                        showNotification('Scoring criteria found but format is invalid. The criteria will not be included in the import.', 'warning');
                    }
                }
            } catch (criteriaError) {
                showNotification('Error parsing scoring criteria: ' + criteriaError.message, 'error');
                scoringCriteria = null;
            }
            
            // Show import options
            importOptions.classList.remove('hidden');
            
            // Show additional guidance in results panel
            updateResultsWithGuidance(nodeCount, edgeCount);
            
        } catch (error) {
            console.error("Error in fetchNetworkHandler:", error);
            showNotification('Error: ' + error.message, 'error');
            // Display error in results panel to make it more visible
            resultsContainer.innerHTML = `
                <div class="object-view">
                    <h3>Error Fetching Network</h3>
                    <div class="notification error">${error.message}</div>
                    <p>Try a different NDEx UUID or check your connection.</p>
                </div>
            `;
        } finally {
            // Reset button state
            fetchButton.disabled = false;
            fetchButton.textContent = 'Fetch Network';
        }
    }
    
    /**
     * Update results panel with guidance
     * @param {number} nodeCount - Number of nodes in the network
     * @param {number} edgeCount - Number of edges in the network
     */
    function updateResultsWithGuidance(nodeCount, edgeCount) {
        let guidance = '<div class="object-view">';
        guidance += '<h3>Import Guidance</h3>';
        
        if (nodeCount <= 100 && edgeCount <= 100) {
            guidance += '<div class="notification success">This network can be imported completely.</div>';
            guidance += '<p>You can choose to import either:</p>';
            guidance += '<ul style="margin-left: 20px; margin-top: 10px;">';
            guidance += `<li><strong>Nodes:</strong> ${nodeCount} nodes will be imported</li>`;
            guidance += `<li><strong>Edges:</strong> ${edgeCount} edges will be imported</li>`;
            guidance += '</ul>';
        } else if (nodeCount <= 100) {
            guidance += '<div class="notification warning">This network has too many edges but nodes can be imported.</div>';
            guidance += '<p>Recommendation:</p>';
            guidance += '<ul style="margin-left: 20px; margin-top: 10px;">';
            guidance += `<li><strong>Nodes:</strong> ${nodeCount} nodes can be imported</li>`;
            guidance += `<li><strong>Edges:</strong> Cannot import (${edgeCount} > 100 limit)</li>`;
            guidance += '</ul>';
        } else if (edgeCount <= 100) {
            guidance += '<div class="notification warning">This network has too many nodes but edges can be imported.</div>';
            guidance += '<p>Recommendation:</p>';
            guidance += '<ul style="margin-left: 20px; margin-top: 10px;">';
            guidance += `<li><strong>Nodes:</strong> Cannot import (${nodeCount} > 100 limit)</li>`;
            guidance += `<li><strong>Edges:</strong> ${edgeCount} edges can be imported</li>`;
            guidance += '</ul>';
        } else {
            guidance += '<div class="notification error">This network exceeds both node and edge limits.</div>';
            guidance += '<p>Consider using a smaller network or creating a subnetwork in NDEx first.</p>';
        }
        
        guidance += '<p style="margin-top: 15px;"><strong>Object Type:</strong> Choose a descriptive type for the imported objects (e.g., "protein", "gene", "reaction", etc.)</p>';
        guidance += '</div>';
        
        resultsContainer.innerHTML = guidance;
    }
    
    /**
     * Handle import form submission
     * @param {Event} event - Submit event
     */
    async function importNetworkHandler(event) {
        event.preventDefault();
        
        if (!networkData) {
            showNotification('Please fetch a network first', 'error');
            return;
        }
        
        // Check if we have full network data
        if (!fullNetworkData) {
            showNotification('Full network data is not available. Please try fetching the network again.', 'error');
            return;
        }
        
        // Get form values
        const importType = document.querySelector('input[name="import-type"]:checked').value;
        const objectType = document.getElementById('object-type').value.trim();
        const networkName = networkNameInput.value.trim();
        
        if (!objectType) {
            showNotification('Please enter an object type', 'error');
            return;
        }
        
        if (!networkName) {
            showNotification('Please enter a network name', 'error');
            return;
        }
        
        // Use either the summary counts or the actual length of the arrays
        const nodeCount = networkData.nodeCount || fullNetworkData.nodes?.length || 0;
        const edgeCount = networkData.edgeCount || fullNetworkData.edges?.length || 0;
        
        // Check size limits based on import type
        if (importType === 'nodes' && nodeCount > 100) {
            showNotification('Network has too many nodes (> 100). Please choose to import edges or use a smaller network.', 'error');
            return;
        }
        
        if (importType === 'edges' && edgeCount > 100) {
            showNotification('Network has too many edges (> 100). Please choose to import nodes or use a smaller network.', 'error');
            return;
        }
        
        // Disable form during import
        const importBtn = document.getElementById('import-btn');
        importBtn.disabled = true;
        importBtn.textContent = 'Importing...';
        showLoading(resultsContainer);
        
        try {
            // Use the full network data for import
            // Make sure it includes all the summary data
            const dataToImport = {
                ...fullNetworkData,
                name: networkData.name || fullNetworkData.name,
                description: networkData.description || fullNetworkData.description,
                externalId: networkData.externalId || fullNetworkData.externalId,
                properties: networkData.properties || fullNetworkData.properties
            };
            
            // Call the importNetworkToDeckhard function
            const result = await deckhardClient.importNetworkToDeckhard(
                dataToImport,
                objectType,
                importType,
                {
                    name: networkName,
                    criteria: scoringCriteria
                }
            );
            
            // Show success message
            showNotification(`Successfully imported ${result.objectCount} ${importType} to Deckhard as ${objectType} objects`, 'success');
            
            // Display detailed results
            displayImportResults(result, networkName, objectType, importType);
            
        } catch (error) {
            showNotification('Import failed: ' + error.message, 'error');
            resultsContainer.innerHTML = `
                <div class="object-view">
                    <h3>Import Failed</h3>
                    <div class="notification error">${error.message}</div>
                    <p>Please check your connection and try again. If the problem persists, contact the system administrator.</p>
                </div>
            `;
        } finally {
            // Reset button state
            importBtn.disabled = false;
            importBtn.textContent = 'Import to Deckhard';
        }
    }
    
    /**
     * Display import results
     * @param {Object} result - Import result
     * @param {string} networkName - Network name
     * @param {string} objectType - Object type
     * @param {string} importType - Import type (nodes or edges)
     */
    function displayImportResults(result, networkName, objectType, importType) {
        const html = `
            <div class="object-view">
                <div class="object-header">
                    <h2 class="object-title">Import Successful</h2>
                    <div class="object-type">Network: ${networkName}</div>
                </div>
                
                <h3 class="panel-header">Summary</h3>
                <div class="property-list">
                    <div class="property-item">
                        <div class="property-label">Object List ID:</div>
                        <div class="property-value">${result.objectListId}</div>
                    </div>
                    <div class="property-item">
                        <div class="property-label">Objects Created:</div>
                        <div class="property-value">${result.objectCount} ${importType} as ${objectType}</div>
                    </div>
                    <div class="property-item">
                        <div class="property-label">Scoring Criteria:</div>
                        <div class="property-value">${scoringCriteria ? 'Included' : 'Not available'}</div>
                    </div>
                </div>
                
                <div style="margin-top: 20px;">
                    <a href="/browser#object_list/${result.objectListId}" target="_blank" class="search-button" style="text-decoration: none; display: inline-block;">
                        View Object List in Browser
                    </a>
                </div>
            </div>
        `;
        
        resultsContainer.innerHTML = html;
    }
    
    /**
     * Show a notification message
     * @param {string} message - Message to display
     * @param {string} type - 'error', 'success', or 'warning'
     */
    function showNotification(message, type = 'info') {
        console.log(`Notification (${type}): ${message}`);
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        // Add to notification container
        notificationContainer.appendChild(notification);
        
        // Remove after a delay (except for errors)
        if (type !== 'error') {
            setTimeout(() => {
                notification.remove();
            }, 5000);
        }
    }
    
    /**
     * Show loading spinner
     * @param {HTMLElement} container - Container element
     */
    function showLoading(container) {
        container.innerHTML = '<div class="spinner"></div>';
    }
    
    // Make utility functions available globally
    window.ndexImportUI = {
        showNotification,
        showLoading
    };
});
