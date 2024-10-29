docker run \
--name=hongisa \
--network mattermost-network \
--ip 172.22.0.5 \
--volume=/Users/Gwangui/mattermost/hongisa/:/app \
--volume=/Users/Gwangui/mattermost/hongisa/json-db:/json-db \
--restart=always \
-p 8006:8006 \
-d mattermost-bot