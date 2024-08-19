# Deployment of Agent Evaluation App
#### Redeploying the app:
 - $ cd /home/speccoud/agent_evaluation
 - $ git pull
 - $ conda activate agent_eval
 - $ cd react-app
 - $ npm i
 - $ npm run build
 - $ sudo systemctl restart agent_eval

#### Changing the Database File
- $ scp path/to/local/file user@server.ucsd.edu:/home/user
- $ mv file /home/speccoud/ae_datatbase/ae_database.db
- $ sudo systemctl restart agent_eval

#### Edit the agent_eval service:
- $ sudo nano /etc/systemd/system/agent_eval.service
- $ sudo systemctl daemon-reload
- $ sudo systemctl restart agent_eval

#### Edit the nginx configuration:
- $ sudo nano /etc/nginx/sites-available/agent_eval.conf
- $ sudo systemctl daemon-reload
- $ sudo systemctl restart nginx