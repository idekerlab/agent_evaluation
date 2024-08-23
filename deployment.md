# Deployment of Agent Evaluation App
#### Redeploying the app:
 - $ ssh deckard@<server_name>.ideker.ucsd.edu
 - $ cd /opt/data/agent_evaluation
 - $ git pull
 - $ cd react-app
 - $ npm i
 - $ npm run build
 - $ sudo systemctl restart agent_eval

#### Changing the Database File
- $ scp path/to/local/file deckard@<server_name>.ideker.ucsd.edu:/opt/data/ae_database/ae_database.db.tmp
- $ ssh deckard@<server_name>.ideker.ucsd.edu
- $ mv /opt/data/ae_database/ae_database.db /opt/data/ae_database/ae_database.db.\`date +%s\`.bkup
- $ mv /opt/data/ae_database/ae_database.db.tmp /opt/data/ae_database/ae_database.db
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

TODO: How to configure server (Ask Kevin)