# Deployment of Agent Evaluation App
#### Redeploying the app:
 - $ ssh <your_username>@<server_name>.ideker.ucsd.edu
 - $ cd /home/speccoud/agent_evaluation
 - $ git pull
 - $ conda activate agent_eval
 - $ cd react-app
 - $ npm i
 - $ npm run build
 - $ sudo systemctl restart agent_eval

#### Changing the Database File
- $ scp path/to/local/file <your_username>@<server_name>.ideker.ucsd.edu:/home/speccoud
- $ ssh <your_username>@<server_name>.ideker.ucsd.edu
- $ rm /home/speccoud/ae_database/ae_database.db
- $ mv <file_from_local_machine> /home/speccoud/ae_datatbase/ae_database.db
- $ sudo systemctl restart agent_eval

#### Edit the agent_eval service:
- $ ssh <your_username>@<server_name>.ideker.ucsd.edu
- $ sudo nano /etc/systemd/system/agent_eval.service
- $ sudo systemctl daemon-reload
- $ sudo systemctl restart agent_eval

#### Edit the nginx configuration:
- $ ssh <your_username>@<server_name>.ideker.ucsd.edu
- $ sudo nano /etc/nginx/sites-available/agent_eval.conf
- $ sudo systemctl daemon-reload
- $ sudo systemctl restart nginx