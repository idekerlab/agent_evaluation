# CX2 Scoring Criteria and Property Ordering Guide

This guide explains how to define scoring criteria and property ordering in CX2 files for import into Deckard.

## Overview

In CX2 format, scoring criteria and display ordering are defined as simple string attributes in the networkAttributes section. These attributes use human-readable, parseable string formats that are easy to include in CX2 files and avoid JSON parsing issues in tools like Cytoscape Desktop.

## CX2 Network Attributes Structure

In a CX2 file, network attributes are defined using direct key-value pairs in the "networkAttributes" aspect:

```json
{
  "networkAttributes": [
    {
      "name": "My Network",
      "description": "Network description",
      "scoring_criteria": "checkbox: All correct|checkbox: Needs improvement|textarea: Comments",
      "display_order": "name,interaction,evidence,text"
    }
  ]
}
```

## Scoring Criteria Format

Scoring criteria are stored as a pipe-delimited string under the `scoring_criteria` attribute:

```
checkbox: Label|menu: Label: option1, option2|textarea: Label
```

### Format Rules

1. Each criterion is separated by a pipe (`|`) character
2. Each criterion begins with the input type, followed by a colon and the label
3. For `menu` type, options are provided after another colon, as a comma-separated list
4. Available input types:
   - `checkbox`: Boolean input (true/false)
   - `textarea`: Multi-line text input
   - `text`: Single-line text input
   - `menu`: Dropdown selection with options

### Examples

```
checkbox: All correct|checkbox: Correct but could be more precise|textarea: Comments
```

```
checkbox: Approve|menu: Rating: excellent, good, fair, poor|textarea: Feedback
```

## Property Ordering Format

Property ordering is stored as a comma-separated string under the `display_order` attribute:

```
property1,property2,property3
```

Properties will be displayed in the order they appear in this list. Properties not listed will appear after the ordered properties, in alphabetical order.

### Example

```
interaction,evidence,text,source,target
```



## Working with These Formats in Code

### Parsing Scoring Criteria

When parsing the scoring criteria string, split by the pipe character (`|`) to get individual criteria. Then for each criterion:

1. Split at the first colon to get the input type
2. For types other than menu, everything after the colon is the label
3. For menu type, split again at the second colon to separate label from options
4. Generate property names programmatically from labels (e.g., by converting to snake_case)

### Parsing Display Order

To parse the display order string, simply split by comma (`,`) to get the ordered list of property names.

## Implementation Notes

- The string formats are deliberately simple to avoid JSON escaping and parsing issues
- Property names for scoring criteria are derived from the labels
- No nested or complex structures are used, keeping the format flat and readable
- Both formats should be preserved as strings throughout the system until they need to be used for display
