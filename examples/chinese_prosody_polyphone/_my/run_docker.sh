#!/bin/bash

set -e

vols="-v /etc/localtime:/etc/localtime:ro -v /etc/timezone:/etc/timezone:ro"
vols+=" -v /nfs1:/nfs1 -v /nfs2:/nfs2"
vols+=" -v $HOME:$HOME"

vols+=" -v $PWD/..:/app -w /app/$(basename $PWD)"

name=gl-wetts-frontend
image=gl_wetts_frontend


echo "Start docker container: ${name}"
docker run -d -it --name ${name} --rm --user "$(id -u)":"$(id -g)" $vols ${image} bash

echo "Add user in docker container: ${USER} => ${name}"
docker exec --user root -t ${name} sh -c 'groupadd -g 452200513 domain;
  useradd -u 452222195 guang.liang -g 452200513 -s /bin/bash;
  chown -R 452222195:452200513 .;'

echo "Docker container started: ${name}"
