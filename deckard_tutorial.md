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
  ```
  [
      ...
      {
          "networkAttributes": [
              ...
              {
                  "n": "_criteria",
                  "v": [ { "label": "test1", "property_name": "test1", "input_type": "textarea", "display_type": "text", "data_type": "str" } ]
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
- Upload it to Deckard

- Review it in Reviwer
