set -e

container_name=gl-wetts-frontend

docker run --gpus all \
  -it --rm -d \
  --name ${container_name} \
  -v $PWD:/wetts -w /wetts --shm-size=8g \
  -v $HOME/repo:/app \
  -v /nfs1:/nfs1 -v /nfs2:/nfs2 \
  --ulimit memlock=-1 --ulimit stack=67108864 \
  gl_wetts_frontend \
  bash

echo "docker container name: ${container_name}"
