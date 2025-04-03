/**
 * NDEx Import UI Module
 * 
 * This module handles the UI interactions for the NDEx to Deckhard importer.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const uuidInput = document.getElementById('ndex-uuid');
    const fetchButton = document.getElementById('fetch-network-btn');
    const fileDropZone = document.getElementById('file-drop-zone');
    const fileInput = document.getElementById('cx-file-input');
    const fileNameDisplay = document.getElementById('file-name-display');
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
    let fullNetworkData = null;
    let scoringCriteria = null;
    
    // Add event listeners
    importForm.addEventListener('submit', importNetworkHandler);
    
    // File input listeners
    fileDropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop listeners
    fileDropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileDropZone.classList.add('dragover');
    });
    fileDropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        fileDropZone.classList.remove('dragover');
    });
    fileDropZone.addEventListener('drop', handleFileDrop);
    
    // Test buttons
    testFetchBtn.style.display = 'none';
    testProxyBtn.style.display = 'none';
    
    /**
     * Handle file selection from input click
     */
    function handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            processFile(file);
        }
    }
    
    /**
     * Handle file drop event
     */
    function handleFileDrop(event) {
        event.preventDefault();
        fileDropZone.classList.remove('dragover');
        const file = event.dataTransfer.files[0];
        if (file) {
            processFile(file);
        }
    }
    
    /**
     * Process the selected/dropped CX file
     * @param {File} file
     */
    function processFile(file) {
        // Clear previous notifications and results
        notificationContainer.innerHTML = '';
        resultsContainer.innerHTML = '';
        
        // Validate file type
        if (!file.name.toLowerCase().endsWith('.cx')) {
            showNotification('Invalid file type. Please upload a .cx file.', 'error');
            resetFileInput();
            return;
        }
        
        fileNameDisplay.textContent = `Selected file: ${file.name}`;
        showLoading(previewContent);
        networkPreview.classList.remove('hidden');
        importOptions.classList.add('hidden');
        criteriaPreview.classList.add('hidden');
        
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const cxData = JSON.parse(e.target.result);
                console.log("Successfully parsed CX file");
                
                // Basic validation of CX structure (can be expanded)
                if (!Array.isArray(cxData) || cxData.length === 0) {
                    throw new Error('Invalid CX format: Expected an array of aspects.');
                }
                
                // Store the parsed data
                fullNetworkData = parseCxToStructuredData(cxData);
                console.log("Structured network data:", fullNetworkData);
                
                // Display preview using the parsed data
                displayNetworkPreviewFromFile(fullNetworkData);
                
            } catch (error) {
                console.error("Error parsing CX file:", error);
                showNotification(`Error processing file: ${error.message}`, 'error');
                resetFileInput();
                previewContent.innerHTML = `<div class="notification error">Failed to parse CX file. Ensure it's valid JSON.</div>`;
            }
        };
        reader.onerror = function() {
            showNotification('Error reading file.', 'error');
            resetFileInput();
            previewContent.innerHTML = `<div class="notification error">Failed to read file.</div>`;
        };
        
        reader.readAsText(file);
    }
    
    /**
     * Reset file input display
     */
    function resetFileInput() {
        fileNameDisplay.textContent = '';
        fileInput.value = '';
        networkPreview.classList.add('hidden');
        importOptions.classList.add('hidden');
        criteriaPreview.classList.add('hidden');
        fullNetworkData = null;
    }
    
    /**
     * Parses the raw CX JSON array into a more structured object
     * similar to what the NDEx API might return.
     * @param {Array} cxData - Raw array of CX aspects
     * @returns {Object} - Structured network data
     */
    function parseCxToStructuredData(cxData) {
        const structuredData = {
            name: 'Unnamed Network from CX',
            description: '',
            properties: [],
            nodes: [],
            edges: [],
            nodeAttributes: [],
            edgeAttributes: [],
        };
        
        cxData.forEach(aspectContainer => {
            const aspectName = Object.keys(aspectContainer)[0];
            const aspectData = aspectContainer[aspectName];
            
            switch (aspectName) {
                case 'networkAttributes':
                    structuredData.properties = aspectData;
                    const nameProp = aspectData.find(p => p.n === 'name');
                    if (nameProp) structuredData.name = nameProp.v;
                    const descProp = aspectData.find(p => p.n === 'description');
                    if (descProp) structuredData.description = descProp.v;
                    break;
                case 'nodes':
                    structuredData.nodes = aspectData.map(node => ({
                        id: node['@id'],
                        name: node.n,
                        represents: node.r
                    }));
                    break;
                case 'edges':
                    structuredData.edges = aspectData.map(edge => ({
                        id: edge['@id'],
                        source: edge.s,
                        target: edge.t,
                        interaction: edge.i
                    }));
                    break;
                case 'nodeAttributes':
                    structuredData.nodeAttributes = aspectData.map(attr => ({
                        propertyOf: attr.po,
                        name: attr.n,
                        value: attr.v,
                        dataType: attr.d
                    }));
                    break;
                case 'edgeAttributes':
                    structuredData.edgeAttributes = aspectData.map(attr => ({
                        propertyOf: attr.po,
                        name: attr.n,
                        value: attr.v,
                        dataType: attr.d
                    }));
                    break;
            }
        });
        
        structuredData.nodeCount = structuredData.nodes.length;
        structuredData.edgeCount = structuredData.edges.length;
        
        return structuredData;
    }
    
    /**
     * Display network preview based on data parsed from CX file
     * @param {Object} parsedData - Structured data from CX file
     */
    function displayNetworkPreviewFromFile(parsedData) {
        console.log("Displaying preview for data:", parsedData);
        
        const nodeCount = parsedData.nodeCount || 0;
        const edgeCount = parsedData.edgeCount || 0;
        
        if (nodeCount === 0 && edgeCount === 0) {
            showNotification('Warning: CX file contains no nodes or edges.', 'warning');
        }
        
        if (nodeCount > 100 && edgeCount > 100) {
            showNotification('Network too large: both nodes and edges exceed 100 limit. Import will be capped.', 'warning');
        } else if (nodeCount > 100) {
            showNotification('Network nodes exceed 100 limit. Import will be capped if importing nodes.', 'warning');
        } else if (edgeCount > 100) {
            showNotification('Network edges exceed 100 limit. Import will be capped if importing edges.', 'warning');
        }
        
        const html = `
            <table class="result-table">
                <tbody>
                    <tr>
                        <td><strong>Name:</strong></td>
                        <td>${parsedData.name || 'Unnamed Network'}</td>
                    </tr>
                    <tr>
                        <td><strong>Description:</strong></td>
                        <td>${parsedData.description || 'No description'}</td>
                    </tr>
                    <tr>
                        <td><strong>Nodes:</strong></td>
                        <td>${nodeCount} ${nodeCount > 100 ? '<span class="notification warning" style="padding:2px 5px; margin:0;">limit 100</span>' : ''}</td>
                    </tr>
                    <tr>
                        <td><strong>Edges:</strong></td>
                        <td>${edgeCount} ${edgeCount > 100 ? '<span class="notification warning" style="padding:2px 5px; margin:0;">limit 100</span>' : ''}</td>
                    </tr>
                    <tr>
                        <td><strong>Attributes:</strong></td>
                        <td>${(parsedData.properties?.length || 0)} network, ${parsedData.nodeAttributes?.length || 0} node, ${parsedData.edgeAttributes?.length || 0} edge</td>
                    </tr>
                </tbody>
            </table>
        `;
        previewContent.innerHTML = html;
        networkPreview.classList.remove('hidden');
        
        networkNameInput.value = parsedData.name || 'Unnamed Network';
        
        try {
            scoringCriteria = findAndParseScoringCriteria(parsedData.properties);
            if (scoringCriteria) {
                criteriaContent.textContent = JSON.stringify(scoringCriteria, null, 2);
                criteriaPreview.classList.remove('hidden');
                
                if (!deckhardClient.validateScoringCriteria(scoringCriteria)) {
                    showNotification('Scoring criteria found but format is invalid. The criteria will not be included in the import.', 'warning');
                }
            } else {
                criteriaPreview.classList.add('hidden');
            }
        } catch (criteriaError) {
            showNotification('Error processing scoring criteria: ' + criteriaError.message, 'error');
            scoringCriteria = null;
            criteriaPreview.classList.add('hidden');
        }
        
        importOptions.classList.remove('hidden');
        
        updateResultsWithGuidance(nodeCount, edgeCount);
    }
    
    /**
     * Finds and parses the scoring criteria from network attributes.
     * @param {Array} networkAttributes - Array of network attributes from CX.
     * @returns {Object|null} - Parsed scoring criteria object or null.
     */
    function findAndParseScoringCriteria(networkAttributes) {
        if (!networkAttributes || !Array.isArray(networkAttributes)) {
            return null;
        }
        
        const criteriaAttr = networkAttributes.find(attr => attr.n === 'scoring_criteria');
        
        if (!criteriaAttr || criteriaAttr.v === undefined || criteriaAttr.v === null) {
            console.log("No scoring_criteria attribute found in network properties");
            return null;
        }
        
        try {
            const criteriaValue = criteriaAttr.v;
            const criteria = typeof criteriaValue === 'string' ?
                           JSON.parse(criteriaValue) : criteriaValue;
            
            console.log("Found scoring criteria:", criteria);
            if (!Array.isArray(criteria)) {
                throw new Error('Scoring criteria is not an array.');
            }
            return criteria;
        } catch (error) {
            console.error('Failed to parse scoring criteria from attribute:', error);
            throw new Error('Invalid scoring_criteria format: ' + error.message);
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
        
        if (!fullNetworkData) {
            showNotification('Please upload and process a CX file first', 'error');
            return;
        }
        
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
        
        const nodeCount = fullNetworkData.nodeCount || 0;
        const edgeCount = fullNetworkData.edgeCount || 0;
        
        if (importType === 'nodes' && nodeCount > 100) {
            showNotification('Network has too many nodes (> 100). Import will be capped at 100 nodes.', 'warning');
        }
        
        if (importType === 'edges' && edgeCount > 100) {
            showNotification('Network has too many edges (> 100). Import will be capped at 100 edges.', 'warning');
        }
        
        const importBtn = document.getElementById('import-btn');
        importBtn.disabled = true;
        importBtn.textContent = 'Importing...';
        showLoading(resultsContainer);
        
        try {
            const dataToImport = fullNetworkData;
            
            const result = await deckhardClient.importNetworkToDeckhard(
                dataToImport,
                objectType,
                importType,
                {
                    name: networkName,
                    criteria: scoringCriteria
                }
            );
            
            showNotification(`Successfully imported ${result.objectCount} ${importType} to Deckhard as ${objectType} objects`, 'success');
            
            displayImportResults(result, networkName, objectType, importType);
            
        } catch (error) {
            console.error("Import failed:", error);
            showNotification(`Import failed: ${error.message}`, 'error');
            resultsContainer.innerHTML = `
                <div class="object-view">
                    <h3>Import Failed</h3>
                    <div class="notification error">${error.message}</div>
                    <p>Please check your connection and try again. If the problem persists, contact the system administrator.</p>
                </div>
            `;
        } finally {
            importBtn.disabled = false;
            importBtn.textContent = 'Import to Deckhard';
        }
    }
    
    /**
     * Display import results
     * @param {Object} result - Import result
     * @param {string} listName - Name given to the object list
     * @param {string} objectType - Object type
     * @param {string} importType - Import type (nodes or edges)
     */
    function displayImportResults(result, listName, objectType, importType) {
        const html = `
            <div class="object-view">
                <div class="object-header">
                    <h2 class="object-title">Import Successful</h2>
                    <div class="object-type">Object List: ${listName}</div>
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
        
        notificationContainer.appendChild(notification);
        
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
