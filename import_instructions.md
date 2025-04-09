# Instructions for Creating Sample Object List

To create a sample object list with the specified criteria for testing the reviewer interface:

## Option 1: Using Python with Deckhard API

```python
from app.config import load_database_uri
from app.sqlite_database import SqliteDatabase
import json

# Load the object list definition
with open('sample_object_list_definition.json', 'r') as f:
    object_list = json.load(f)

# Connect to database
uri = load_database_uri()
db = SqliteDatabase(uri)

# Find some hypotheses (first 3)
hypotheses = db.find('hypothesis', {})[:3]
hypothesis_ids = [h['object_id'] for h in hypotheses]

# Add hypothesis IDs to object list
object_list['object_ids'] = hypothesis_ids

# Create the object list in the database
object_list_id, _, _ = db.add(object_id=None, properties=object_list, object_type="object_list")

print(f"Created object list with ID: {object_list_id}")
print(f"Object list contains hypothesis IDs: {hypothesis_ids}")

# Close database connection
db.close()
```

## Option 2: Using the Deckhard Web UI

1. Navigate to the Deckhard web interface
2. Click on "object_list" in the sidebar
3. Click "New object_list"
4. Fill in the form:
   - Name: "Hypothesis Review Sample"
   - Description: "A collection of hypotheses for demonstration of the review interface"
   - Find and select 3 hypotheses in the object_ids selector
   - In the "_criteria" field, paste the following JSON:
   ```json
   [
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
   ```
5. Click "Submit" to create the object list

## Testing the Reviewer Interface

Once the object list is created:

1. Navigate to the Browser interface at `/browser`
2. Search for "Hypothesis Review Sample" or browse object lists
3. Click on the object list to view its details
4. Click the "Review" button to open the reviewer interface
5. The reviewer will display the hypotheses with the criteria for scoring
