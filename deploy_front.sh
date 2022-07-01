#!/bin/bash
target=$(pwd)
read -p "Installation directory Anfisa-front: ${target}? (y/n)" response
if [ "$response" != "y" ] && [ "$response" != "Y" ] ; then
read -p "Type directory: " target
fi
mkdir -p ${target}/front
DIR=${target}/front
echo "Cloning a Anfisa-react-client repo"
cd $DIR
git clone https://github.com/ForomePlatform/Anfisa-React-Client.git .
BRUNCH=$(git branch -r | grep "release-" | sort -r | awk '{print $1}' | head -1 | sed 's|.*/||')
git checkout $BRUNCH
result=$( sudo docker images -q anfisa-react-client)
if [[ -n "$result" ]]; then
echo "image exists"
sudo docker rmi -f anfisa-react-client
fi
echo "build the new docker image"
cat << \EOF > default.nginx
server {
    listen 80;

    location /app {
         rewrite ^/(.*)$ /anfisa/$1 break;
         proxy_pass http://172.23.0.4:80;
         error_log /var/log/nginx/anfisa_err.log warn;
         access_log /var/log/nginx/anfisa.log;

    }

    location /anfisa {
        rewrite ^/(.*)$ /$1/app break;
        proxy_pass http://172.23.0.4:80;
        error_log /var/log/nginx/anfisa_err.log warn;
        access_log /var/log/nginx/anfisa.log;
    }

    location / {
        client_max_body_size 100M;
        proxy_buffering off;
        proxy_read_timeout 3000;
        root /usr/share/nginx/html/Anfisa/;
        try_files $uri $uri/ /index.html;
   }
}
EOF
sudo docker build -t anfisa-react-client . >> ${DIR}/output
echo "built docker images and proceeding to delete existing container"
result=$( docker ps -aq -f name=anfisa-react-client)
if [[ -n "$result" ]]; then
echo "Container exists"
sudo docker ps -aq -f name=anfisa-react-client | xargs docker rm -f
echo "Deleted the existing docker container"
else
echo "No such running container"
fi
echo "Deploying the updated container"
sudo docker run --name anfisa-react-client -d -p 3000:80 --network anfisa_default anfisa-react-client
touch env-config.js
cat << EOF > ./env-config.js
window._env_ = {
  REACT_APP_URL_BACKEND: 'http://localhost:9010/anfisa/app'
}
EOF
echo "Copy env-config.js into running container"
sudo docker cp ./env-config.js anfisa-react-client:/usr/share/nginx/html/Anfisa/
echo "Add header Access-Control-Allow-Origin in Back-end container"
sudo docker exec -d anfisa7 sed -i '59 i \\t\tadd_header 'Access-Control-Allow-Origin' '*' always;' /etc/nginx/conf.d/anfisa.conf
sudo docker restart anfisa7
echo "Open URL http://localhost:3000"