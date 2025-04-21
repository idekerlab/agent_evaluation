# Deployment of Agent Evaluation App

## Redeploying the app


```bash
sudo -u deckard /bin/bash
cd /opt/agent_evaluation
git pull
exit # switches back to your user account
sudo systemctl restart agent_eval
```

NOTE: To check status of service run `systemctl status agent_eval`

## Changing the Database File


### To copy the database, do the following command on your local machine

```bash
scp /path/to/ae_database.db user@server.ideker.ucsd.edu:/tmp/ae_database.db
```

### To backup and update the copied database file

 ```bash
 sudo -u deckard /bin/bash
 cp /opt/data/ae_database/ae_database.db /opt/data/ae_database/ae_database.db.bk.`date +%s`
 cp /tmp/ae_database.db /opt/data/ae_database/.
 exit # switches back to your user account
 rm /tmp/ae_database.db # remove the database file from temp so the next upload does NOT fail
 sudo systemctl restart agent_eval
 ```

### Edit the agent_eval service

This is used by systemd to stop and start the service

```bash
sudo nano /etc/systemd/system/agent_eval.service
sudo systemctl daemon-reload
sudo systemctl restart agent_eval
```

### Edit the nginx configuration

```bash
sudo nano /etc/nginx/sites-available/agent_eval.conf
sudo systemctl daemon-reload
sudo systemctl restart nginx
