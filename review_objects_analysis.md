# Review Objects Analysis

## Overview

This document analyzes the review object models in the Deckard system and clarifies which model is canonical for the current system.

## Review Object Models

### Canonical Model: review_list

The `review_list` is the canonical model for reviews in the current system. It is used by the active frontend code in the reviewer interface.

```javascript
// As used in reviewer-data.js and reviewer-ui.js
review = {
  type: 'review_list',
  object_list_id: objectListId,
  object_ids: objectList.object_ids,
  reviewer: '',
  _criteria: objectList._criteria,
  status: 'open',
  scores: [
    {
      reviewed_object: "obj1",
      scores: {
        property1: "value1",
        property2: "value2"
      }
    }
  ],
  submit_date: ''
}
```

Key characteristics:
- The `scores` property is an array of objects
- Each score object has a `reviewed_object` field (an object ID) and a `scores` object with the actual scores
- The review_list copies `_criteria` from the object_list for consistency
- Status transitions from "open" to "submitted" when completed

### Legacy Model: review

In `app/view_edit_specs.py`, there's a rigid schema definition for a `review` object that is legacy:

```javascript
"review": {
    "documentation": "Review objects are generated either by automated queries to LLMs or by human reviewers through the review portal...",
    "properties": {
        "name": { ... },
        "review_text": { ... },
        "ranking_data": { ... },
        "summary_review": { ... },
        "hypotheses_text": { ... },
        "agent_id": { ... },
        "description": { ... },
        "review_set_id": { ... },
        "analysis_run_id": { ... }
    }
}
```

This model was used by the legacy analysis and review frameworks that used LLMs to automatically generate reviews and is no longer actively used in the frontend.

## Design Rationale

The `review_list` model was designed based on the understanding that:

1. Reviews always operate on collections of objects (object_lists)
2. Even when a single object is being reviewed, it's still wrapped in an object_list
3. Creating individual review objects for each item would unnecessarily clutter the database

This approach allows for a more efficient workflow where:
- Review data for multiple objects is stored in a single database entry
- The reviewing interface can handle consistent navigation between objects
- Criteria and other metadata are shared across all objects in the review

## API Endpoints

The current system uses these endpoints for review operations:

```
POST /objects/review_list/create
POST /objects/review_list/{review_list_id}/edit
```

## Terminology Note

While "review" is used as a general concept in documentation and discussions, the actual object type in the database and API is `review_list`. This naming convention accurately reflects that reviews in the system operate on collections of objects.

## Recommendations for Cleanup

1. **Remove the legacy `review` model**: The rigid schema model defined in view_edit_specs.py can be safely removed as part of the cleanup.

2. **Standardize documentation terminology**: Ensure all documentation consistently refers to `review_list` objects rather than `review` objects.

3. **No need for database migration**: Since the active frontend already uses the correct model, there's no need to migrate data.

4. **Consider renaming for clarity**: In a future update, it might be worth considering whether to rename the object type to simply "review" for clarity while maintaining the current structure. This would require updating frontend code and ensuring backward compatibility.
