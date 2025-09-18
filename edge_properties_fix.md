# Edge Properties Display Issue Fix

## Issue Identified
When importing networks from CX2 files or NDEx, edge properties stored in the 'v' field are not being flattened in the client-side parser, leading to properties like "interaction", "bel_expression", "text", and "evidence" not appearing in the interface.

## Root Cause
In the `ndex-import-ui.js` file, the `parseCxToStructuredData` function correctly flattens 'v' properties for nodes but not for edges:

```javascript
// For nodes - properties are flattened
if (node.v && typeof node.v === 'object') {
  return {
    id: node.id,
    name: node.v.n || 'Unnamed Node',
    represents: node.v.represents || null,
    _rawData: node.v  // Properly stores all v properties
  };
}

// For edges - v properties are not handled
structuredData.edges = aspectData.map(edge => ({
  id: edge['@id'],
  source: edge.s,
  target: edge.t,
  interaction: edge.i
  // Missing: edge.v properties are not included
}));
```

In contrast, the server-side code in `ndex_utils.py` correctly flattens 'v' properties for both nodes and edges:

```python
# For edges - properties are flattened
if 'v' in edge_attrs and isinstance(edge_attrs['v'], dict):
    for key, value in edge_attrs['v'].items():
        edge[key] = value  # This adds all nested properties to the top level
```

## Fix Required
Modify the `parseCxToStructuredData` function in `ndex-import-ui.js` to include the 'v' properties for edges:

```javascript
// Updated edge mapping code
structuredData.edges = aspectData.map(edge => {
  const edgeObj = {
    id: edge['@id'] || edge.id,
    source: edge.s,
    target: edge.t,
    interaction: edge.i
  };
  
  // Add all properties from the 'v' object if it exists
  if (edge.v && typeof edge.v === 'object') {
    Object.keys(edge.v).forEach(key => {
      edgeObj[key] = edge.v[key];
    });
  }
  
  return edgeObj;
});
```

This change will make the client-side parsing consistent with the server-side handling and ensure that all edge properties are displayed in the interface.

## Implementation Plan
1. Modify the `parseCxToStructuredData` function in `ndex-import-ui.js` as shown above
2. Test with both NDEx imports and local CX2 file imports
3. Verify that edge properties like "bel_expression", "text", and "evidence" now appear in the browser interface

## Impact
This fix will ensure that users can see all relevant edge properties in the interface, providing a more complete view of the network data without requiring any backend changes.
