## Run the app on your local machine

- Select a folder and clone the repo: `git clone https://github.com/idekerlab/agent_evaluation`

- Use the latest branch (still in development)

  ```
  git fetch --all
  git checkout deckard-chengzhan
  ```

- Install libraries

  ```
  conda create -n agent_eval python==3.11
  conda activate agent_eval
  pip install -r requirements.txt
  ```

- Run the app by running `main.py` in the root directory
- Check whether it is successful
  - http://localhost:8000/browser
  - http://localhost:8000/ndex-import
  - http://localhost:8000/reviewer

## Workflow

Here this network, [prkdc_kg](https://www.ndexbio.org/viewer/networks/737f161f-fdf8-11ef-b81d-005056ae3c32) , is used as an example.

- Download cx file of this network from NDEx.

- Editing the cx file
  - The criteria can be customized by adding '\_criteria' in the `networkAttributes`
  - The order of the properties can also be customized by adding '\_order'
  - Also remember to increase the `elementCount` in `metaData -> networkAttributes" if you add new network properties
  ```
  [
      ...
      {
          "metaData":[
              {
                "name": "networkAttributes",
                "elementCount": 7, // Also remember to increase the count here if you add new network properties
                "version": "1.0",
                "consistencyGroup": 1
              },
              ...
          ]
      }
      ...
      {
          "networkAttributes": [
              ...
              {
                  "n": "_criteria",
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
              },
              {
                  "n": "_order",
                  "v": {
                    "bel_expression": 1,
                    "evidence": 2,
                    "test": 3
                  }
              }
              ...
          ]
      }
      ...
  ]
  ```
- Upload it to Deckard via http://localhost:8000/ndex-import
  <img width="1000" alt="image" src="https://github.com/user-attachments/assets/83baff61-c192-4a33-82bd-cc28c0b60039" />

- Click "View Object List in the Browser" in the right panel and direct to http://localhost:8000/browser
  <img width="1000" alt="image" src="https://github.com/user-attachments/assets/336f4f45-ba9b-4be9-818d-fe8c9866ab6c" />

- In the browser page, click "Object Lists" in the left panel and choose the object list you've just imported in the middle panel, then the preview of the object list will show in the right panel

- In the browser page, click "Review Object List" in the right panel to review it
  <img width="1000" alt="image" src="https://github.com/user-attachments/assets/32f51b96-8bc6-4e53-a358-53e0618e336e" />

