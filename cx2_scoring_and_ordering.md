# CX2 Scoring Criteria and Property Ordering Guide

This guide explains how to define scoring criteria and property ordering in CX2 files for import into Deckard.

## 1. Adding Scoring Criteria and Property Ordering to CX2 Files

In CX2 format, both scoring criteria and property ordering are specified as network attributes. When a CX2 file is imported, these attributes are extracted and included in the object_list.

### CX2 Network Attributes Structure

In a CX2 file, network attributes are defined in the "networkAttributes" aspect. The format can vary depending on how the CX2 file was created:

**Format 1 - Direct key-value pairs:**
```json
{
  "networkAttributes": [
    {
      "name": "My Network",
      "description": "Network description",
      "scoring_criteria": [...],
      "_order": {...}
    }
  ]
}
```

**Format 2 - NVD format (used by NDEx and some tools):**
```json
{
  "networkAttributes": [
    { "n": "name", "v": "My Network", "d": "string" },
    { "n": "description", "v": "Network description", "d": "string" },
    { "n": "scoring_criteria", "v": [...], "d": "list" },
    { "n": "_order", "v": {...}, "d": "object" }
  ]
}
```

In Format 2:
- `n`: Name of the attribute
- `v`: Value of the attribute 
- `d`: Data type (optional)

The Deckard importer currently expects Format 2 (NVD structure).

### Scoring Criteria Format

Scoring criteria is stored as a JSON array under the network attribute name `scoring_criteria`. Each criterion is an object with these properties:

```json
{
  "networkAttributes": [
    {
      "n": "scoring_criteria",
      "v": [
        {
          "label": "Comments",
          "property_name": "comments",
          "input_type": "textarea",
          "display_type": "text",
          "data_type": "str"
        },
        {
          "label": "Evaluation",
          "property_name": "evaluation",
          "input_type": "menu",
          "display_type": "text",
          "data_type": "str",
          "options": ["great!", "good.", "ok.", "needs work.", "unacceptable"]
        }
      ]
    }
  ]
}
```

Required fields:
- `label`: Display name for the criterion
- `property_name`: Property name to store in the database
- `input_type`: Type of input control ("text", "textarea", "checkbox", "menu")

Optional fields:
- `display_type`: How to display the value ("text", "csv", etc.)
- `data_type`: Data type ("str", "int", etc.)
- `options`: Array of options for "menu" input type

### Property Ordering Format

Property ordering is stored as a JSON object under the network attribute name `_order`. The keys are property names, and the values are numeric ranks (lower ranks appear first):

```json
{
  "networkAttributes": [
    {
      "n": "_order",
      "v": {
        "bel_expression": 1,
        "evidence": 2,
        "text": 3,
        "interaction": 4
      }
    }
  ]
}
```

Properties with the same rank will be sorted alphabetically, and properties not mentioned will appear after all ranked properties.

## 2. How They're Processed During Import

The import process extracts these attributes from CX2 as follows:

### Scoring Criteria Extraction

In `ndex-import-ui.js`, the `findAndParseScoringCriteria` function extracts and validates the scoring criteria:

```javascript
function findAndParseScoringCriteria(networkAttributes) {
  if (!networkAttributes || !Array.isArray(networkAttributes)) {
    return null;
  }
  
  const criteriaAttr = networkAttributes.find(attr => attr.n === 'scoring_criteria');
  
  if (!criteriaAttr || criteriaAttr.v === undefined) {
    return null;
  }
  
  // Parse the criteria (if it's a string) or use it directly (if it's already an object)
  const criteria = typeof criteriaValue === 'string' ?
                 JSON.parse(criteriaValue) : criteriaValue;
                 
  // Validate that it's an array
  if (!Array.isArray(criteria)) {
    throw new Error('Scoring criteria is not an array.');
  }
  
  return criteria;
}
```

In `deckhard-client.js`, the criteria is validated and included in the object_list properties:

```javascript
// Add scoring criteria if available and valid
if (criteria && this.validateScoringCriteria(criteria)) {
  objectListProps._criteria = criteria;
}
```

### Property Ordering Extraction

Similarly, in `deckhard-client.js`, the property ordering is extracted and included:

```javascript
// Add _order specifically as an object if it exists
const orderAttribute = networkData.properties?.find(prop => prop.n === '_order');
if (orderAttribute && orderAttribute.v !== undefined) {
  try {
    objectListProps._order = (typeof orderAttribute.v === 'string')
                           ? JSON.parse(orderAttribute.v)
                           : orderAttribute.v;
  } catch (e) {
    console.warn("Could not parse _order attribute as JSON, skipping");
  }
}
```

## 3. Implementation in Another Project

To add scoring criteria and property ordering to CX2 files generated in another project, follow these steps:

### Adding Network Attributes in Code

```javascript
// Example in JavaScript/TypeScript
const networkAttributes = [];

// Add scoring criteria
networkAttributes.push({
  n: "scoring_criteria",
  v: [
    {
      label: "Comments",
      property_name: "comments",
      input_type: "textarea",
      display_type: "text",
      data_type: "str"
    },
    {
      label: "Evaluation", 
      property_name: "evaluation",
      input_type: "menu",
      display_type: "text",
      data_type: "str",
      options: ["great!", "good.", "ok.", "needs work.", "unacceptable"]
    }
  ],
  d: "list"
});

// Add property ordering
networkAttributes.push({
  n: "_order",
  v: {
    bel_expression: 1,
    evidence: 2,
    text: 3
  },
  d: "object"
});

// Then include networkAttributes in your CX2 structure
const cx2Data = [
  { networkAttributes: networkAttributes },
  // Other aspects like nodes, edges, etc.
];
```

### Python Example

```python
network_attributes = []

# Add scoring criteria
network_attributes.append({
  "n": "scoring_criteria",
  "v": [
    {
      "label": "Comments",
      "property_name": "comments",
      "input_type": "textarea", 
      "display_type": "text",
      "data_type": "str"
    },
    {
      "label": "Evaluation",
      "property_name": "evaluation",
      "input_type": "menu",
      "display_type": "text",
      "data_type": "str",
      "options": ["great!", "good.", "ok.", "needs work.", "unacceptable"]
    }
  ]
})

# Add property ordering
network_attributes.append({
  "n": "_order",
  "v": {
    "bel_expression": 1,
    "evidence": 2,
    "text": 3
  }
})

# Then include network_attributes in your CX2 structure
cx2_data = [
  {"networkAttributes": network_attributes},
  # Other aspects like nodes, edges, etc.
]
```

## 4. Testing with Modified CX2 Files

To test these features:

1. Export an existing CX2 file
2. Add or modify the "networkAttributes" aspect to include `scoring_criteria` and `_order`
3. Reimport the modified file into Deckard
4. Open the object list in the reviewer interface to verify that:
   - The scoring criteria appear as form fields in the reviewer
   - The properties are displayed in the specified order

## 5. Validation

Deckard validates scoring criteria during import. A valid criterion must have:
- A `label` property (string)
- A `property_name` property (string) 
- If `input_type` is specified, it must be one of: "text", "textarea", "checkbox", or "menu"
- If `input_type` is "menu", an `options` array should be provided

The property ordering is simpler, requiring just a valid JSON object where keys are property names and values are numeric ranks.
