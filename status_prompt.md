# Review List Viewer - Status and Next Steps

## Current Problem Summary
The review list viewer interface has been created but has critical functionality issues:

1. **Export Issue**: Export button only exports review_list metadata, not the detailed review data from individual review objects
2. **Display Issue**: Selected review lists are not properly displaying their detailed review content
3. **API Integration**: There may be issues with fetching individual review objects or data structure mismatches

## Files to Review and Fix

### Primary Files to Examine:
1. **`app/static/js/review-list.js`** - Main JavaScript file with export and display logic
2. **`app/static/review_list.html`** - HTML structure and element IDs
3. **`app/app.py`** - Flask routes serving the page and API endpoints
4. **`app/routes/object_routes.py`** - API endpoints for fetching review objects
5. **Sample export file**: `review_list_detailed_review_list_df00fe63-31a8-43bc-a811-1df1c8870ecc_2025-05-26.json` - Check what's actually being exported

## Specific Issues to Investigate

### 1. Export Function Issues
- [ ] Verify `currentReviews` array is being populated in `loadReviews()`
- [ ] Check if `exportReviewList()` function is using the correct data
- [ ] Verify the export data structure matches requirements
- [ ] Check console for JavaScript errors during export

### 2. Review Display Issues  
- [ ] Verify `displayReviews()` function is being called
- [ ] Check if individual review objects are being fetched correctly
- [ ] Verify DOM elements exist with correct IDs
- [ ] Check for API endpoint availability for `/objects/review/{reviewId}`

### 3. API Endpoint Verification
- [ ] Test `/objects/review_list/{id}` endpoint manually
- [ ] Test `/objects/review/{id}` endpoint manually  
- [ ] Verify database contains review_list objects with review_ids arrays
- [ ] Check if review objects exist in database

## Required Export Data Structure
```json
{
  "metadata": {
    "reviewer": "...",
    "object_id": "...", 
    "linked_object_list_id": "...",
    "created": "...",
    "exported_at": "..."
  },
  "reviews": [
    {
      "reviewer": "...",
      "score": "...",
      "bel_expression": "...",
      "interaction": "...",
      "evidence": "...",
      "text": "...first two lines...",
      "reviewed_object_id": "..."
    }
  ]
}
```

## Testing Checklist

### Browser Console Testing:
- [ ] Open browser dev tools and check for JavaScript errors
- [ ] Test `currentReviews` variable in console after selecting a review list
- [ ] Verify API calls are successful in Network tab

### Functional Testing:
- [ ] Navigate to `http://localhost:3000/review_list.html`
- [ ] Click "Select Review List" button - modal should open
- [ ] Select a review list - should display in summary table
- [ ] Click a review row - should show details in right panel
- [ ] Click Export - should download file with complete review data

### Data Verification:
- [ ] Check if review_list objects exist in database
- [ ] Verify review_list objects have review_ids property
- [ ] Confirm individual review objects exist and are accessible
- [ ] Test SQL query: `SELECT * FROM nodes WHERE object_type = 'review_list' LIMIT 1`
- [ ] Test SQL query: `SELECT * FROM nodes WHERE object_type = 'review' LIMIT 1`

## Debugging Steps

### 1. Check Database Content
```sql
-- Check review_list objects
SELECT object_id, properties FROM nodes WHERE object_type = 'review_list' LIMIT 3;

-- Check review objects  
SELECT object_id, properties FROM nodes WHERE object_type = 'review' LIMIT 3;
```

### 2. Browser Console Debugging
```javascript
// After selecting a review list, check:
console.log('currentReviewListData:', currentReviewListData);
console.log('currentReviews:', currentReviews);
console.log('currentReviews.length:', currentReviews.length);
```

### 3. Network Tab Verification
- Check if `/objects/review_list/{id}` returns valid data
- Check if `/objects/review/{id}` calls are being made
- Verify response status codes and content

## Root Cause Hypotheses

1. **API Endpoint Issues**: Review objects may not be accessible via `/objects/review/{id}`
2. **Data Structure Mismatch**: Review IDs in review_list may not match actual review object IDs
3. **JavaScript Logic Error**: `currentReviews` array not being properly populated
4. **Async/Await Issues**: Race conditions in data loading
5. **Database Schema Issues**: Missing or incorrectly structured review data

## Success Criteria

- [ ] Modal opens and displays available review lists
- [ ] Selecting a review list populates the summary table with individual reviews
- [ ] Clicking a review shows detailed information in right panel
- [ ] Export button downloads JSON with complete review data including all required fields
- [ ] Export includes metadata plus array of detailed review objects with truncated text

## Next Actions Priority

1. **HIGH**: Debug why `currentReviews` array is empty
2. **HIGH**: Verify individual review objects can be fetched via API
3. **MEDIUM**: Check database schema and data consistency  
4. **MEDIUM**: Add better error handling and console logging
5. **LOW**: Improve UI feedback during loading states

---

**Note**: Focus on the data flow: review_list selection → fetch individual reviews → populate currentReviews → export detailed data. The break is likely in the "fetch individual reviews" step.
