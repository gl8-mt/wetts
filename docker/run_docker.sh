set -e

container_name=gl-wetts-frontend

docker run --gpus all \
  --user $(id -u):$(id -g) \
  -it --rm -d \
  --name ${container_name} \
  -v $PWD/..:/app -w /app/wetts \
  -v /nfs1:/nfs1 -v /nfs2:/nfs2 \
  --shm-size=8g \
  --ulimit memlock=-1 --ulimit stack=67108864 \
  gl_wetts_frontend \
  bash

echo "docker container name: ${container_name}"
