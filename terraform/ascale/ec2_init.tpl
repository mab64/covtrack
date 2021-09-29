#!/bin/bash
apt update
apt -y install net-tools stress-ng docker docker.io # nfs-common docker-compose
systemctl start docker
docker run -dit -p 80:5000 \
    -e MYSQL_HOST="${rdb_address}" \
    -e MYSQL_DATABASE="${db_name}" \
    -e MYSQL_USER="${db_user}" \
    -e MYSQL_PASSWORD="${db_password}" \
    --restart always --name covtrack ${docker_img_name}
