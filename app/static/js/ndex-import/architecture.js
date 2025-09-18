/**
 * NDEx to Deckhard Import - Architecture and Implementation Plan
 * 
 * Project Overview:
 * Single-page application to import NDEx networks as Deckhard object_lists.
 * Users provide an NDEx UUID, the tool fetches the network, and creates Deckhard objects
 * from either nodes or edges of the network (limited to 100 elements).
 * 
 * Key Requirements:
 * - Fetch NDEx network by UUID
 * - Limit to 100 nodes/edges max
 * - Check for "scoring_criteria" property and validate it
 * - Create Deckhard object_list with network properties
 * - Create Deckhard objects from either nodes or edges
 * - Set appropriate object type for created objects
 */

/**
 * Architecture Components:
 * 
 * 1. UI Components (ndex-import.html, ndex-import-ui.js)
 *    - NDEx UUID Input Form
 *    - Network Preview Display
 *    - Import Options Form
 *    - Error/Success Notifications
 *    - Results Display
 * 
 * 2. Core Modules
 *    - NDEx Client (ndex-client.js)
 *      - Network Fetching and Validation
 *      - Scoring Criteria Extraction and Validation
 *    - Deckhard Client (deckhard-client.js)
 *      - Deckhard API Integration
 *      - Object Creation
 * 
 * 3. Implementation Files
 *    - ndex-import.html (main page with UI structure and styling)
 *    - ndex-client.js (NDEx API client)
 *    - deckhard-client.js (Deckhard API client)
 *    - ndex-import-ui.js (UI logic handling)
 *    - architecture.js (this file - documentation and overview)
 */

/**
 * Data Flow:
 * 
 * 1. User enters NDEx UUID and clicks "Fetch Network"
 * 2. ndex-client.js validates UUID and fetches network summary
 * 3. UI displays network summary and import options
 * 4. User selects import type (nodes or edges) and object type
 * 5. User submits the form to start import
 * 6. ndex-client.js fetches network elements (nodes or edges)
 * 7. deckhard-client.js transforms elements to Deckhard objects
 * 8. deckhard-client.js creates object_list and objects in Deckhard
 * 9. UI displays import results with link to view object_list
 */

/**
 * Key Features:
 * 
 * 1. Network Preview
 *    - Basic network properties (name, description, size)
 *    - Size validation (≤ 100 nodes/edges)
 *    - Visual indicators for size limits
 * 
 * 2. Scoring Criteria Handling
 *    - Check for "scoring_criteria" in network properties
 *    - Validate format and structure
 *    - Display criteria in UI
 *    - Include criteria in object_list if valid
 * 
 * 3. Import Options
 *    - Choose between nodes or edges import
 *    - Specify object type for created objects
 *    - Edit network name
 * 
 * 4. Results Display
 *    - Import summary (object_list ID, object count)
 *    - Link to view object_list in browser
 *    - Error messages and troubleshooting guidance
 * 
 * 5. Error Handling
 *    - Network not found or access errors
 *    - Size limit violations
 *    - Invalid scoring criteria
 *    - Deckhard API errors
 */

/**
 * Integration with Deckhard Browser:
 * 
 * The importer follows the same UI/UX patterns as the Deckhard Browser:
 * - Common CSS styles and layout
 * - Three-panel design (instructions, form, results)
 * - Consistent notification system
 * - Loading indicators
 * - Table-based data display
 * - Direct links to the browser for viewing results
 */

/**
 * Maintenance and Extension:
 * 
 * 1. Adding Support for Larger Networks
 *    - Implement pagination or filtering
 *    - Add selection interface for choosing specific elements
 * 
 * 2. Enhanced Property Mapping
 *    - Custom property mapping from NDEx to Deckhard
 *    - Support for advanced property types
 * 
 * 3. Additional NDEx Features
 *    - Network search integration
 *    - User authentication
 *    - Support for private networks
 * 
 * 4. Advanced Data Processing
 *    - Network analysis features
 *    - Custom scoring criteria generation
 *    - Network metrics calculation
 */

/**
 * Dependencies:
 * 
 * 1. External Libraries
 *    - NDEx JavaScript Client (ndexjs)
 * 
 * 2. Deckhard API Endpoints
 *    - /objects/object_list/create (for creating object lists)
 *    - /objects/:type/create (for creating objects)
 *    - /objects/object_list/:id/edit (for updating object lists)
 */
