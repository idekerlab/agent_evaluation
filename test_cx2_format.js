/**
 * Test script for validating CX2 format with string-based scoring_criteria and display_order
 * Run this in the browser console while on the reviewer page
 */

// Sample CX2 network attributes with string-based formats
const sampleNetworkAttributes = [
  {
    "name": "Test Network",
    "scoring_criteria": "checkbox: All correct|checkbox: Incorrect entities|menu: Severity: high, medium, low|textarea: Comments",
    "display_order": "bel_expression,evidence,interaction,text,source,target"
  }
];

// Function to log the status of scoring_criteria and display_order in an object_list
function inspectObjectList(objectListId) {
  fetch(`/objects/object_list/${objectListId}`)
    .then(response => response.json())
    .then(data => {
      console.log("Object List Data:", data);
      
      // Check if scoring_criteria exists and is a string
      if (data.scoring_criteria && typeof data.scoring_criteria === 'string') {
        console.log("✅ scoring_criteria is present as a string:", data.scoring_criteria);
      } else if (data._criteria) {
        console.log("❌ Using legacy _criteria instead of scoring_criteria:", data._criteria);
      } else {
        console.log("❌ No scoring criteria found");
      }
      
      // Check if display_order exists and is a string
      if (data.display_order && typeof data.display_order === 'string') {
        console.log("✅ display_order is present as a string:", data.display_order);
      } else if (data._order) {
        console.log("❌ Using legacy _order instead of display_order:", data._order);
      } else {
        console.log("❌ No display order found");
      }
      
      return data;
    })
    .catch(error => {
      console.error("Error fetching object list:", error);
    });
}

// Function to create a test object_list with string-based attributes
function createTestObjectList() {
  const objectListProps = {
    name: "CX2 String Format Test",
    description: "Testing string-based scoring_criteria and display_order",
    object_type: "test",
    scoring_criteria: "checkbox: All correct|checkbox: Incorrect entities|menu: Severity: high, medium, low|textarea: Comments",
    display_order: "name,description,type,evidence,interaction"
  };
  
  fetch('/objects/object_list/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(objectListProps)
  })
    .then(response => response.json())
    .then(data => {
      console.log("Created test object_list:", data);
      console.log("To inspect this object_list, run:");
      console.log(`inspectObjectList("${data.object_id}")`);
      return data;
    })
    .catch(error => {
      console.error("Error creating test object_list:", error);
    });
}

// Helper function to parse and display scoring criteria
function testParseScoringCriteria(criteriaString) {
  console.log("Testing parsing of scoring criteria string:", criteriaString);
  
  const criteriaItems = criteriaString.split('|');
  const parsedCriteria = [];
  
  criteriaItems.forEach((item, index) => {
    const trimmedItem = item.trim();
    if (!trimmedItem) return;
    
    const firstColonIndex = trimmedItem.indexOf(':');
    if (firstColonIndex === -1) return;
    
    const inputType = trimmedItem.substring(0, firstColonIndex).trim();
    const rest = trimmedItem.substring(firstColonIndex + 1).trim();
    
    const criterion = {
      input_type: inputType,
      label: rest,
      property_name: '',
      options: null
    };
    
    if (inputType === 'menu') {
      const secondColonIndex = rest.indexOf(':');
      
      if (secondColonIndex !== -1) {
        criterion.label = rest.substring(0, secondColonIndex).trim();
        const optionsStr = rest.substring(secondColonIndex + 1).trim();
        criterion.options = optionsStr.split(',').map(o => o.trim());
      }
    }
    
    criterion.property_name = criterion.label
      .toLowerCase()
      .replace(/\s+/g, '_')
      .replace(/[^a-z0-9_]/g, '')
      .trim();
    
    if (!criterion.property_name || criterion.property_name.match(/^_+$/)) {
      criterion.property_name = `criterion_${index + 1}`;
    }
    
    parsedCriteria.push(criterion);
  });
  
  console.log("Parsed criteria:", parsedCriteria);
  return parsedCriteria;
}

// Tests
console.log("=== CX2 String Format Tests ===");
console.log("Run createTestObjectList() to create a test object list");
console.log("Then run inspectObjectList(object_id) with the returned ID to verify the attributes");
console.log("You can also test parsing with testParseScoringCriteria(criteriaString)");
