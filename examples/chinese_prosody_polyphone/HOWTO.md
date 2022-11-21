# How to Set-up

## Setup environment with docker

* build docker image

```sh
# cd path/to/wetts/root
bash -ex ./docker/build_docker.sh
```

* start docker container in the background

```sh
bash -ex ./docker/run_docker.sh
```

* attach to docker container

```sh
docker exec -it gl-wetts-frontned
```

## Training & Test

Assume that you are inside the docker.

* Train & Test:

```sh
# cd path/to/wetts/examples/chinese_prosody_polyphone/

# bash -ex ./run_cli.sh <num_epoch> <out_dir> <corpus_dir> <learning_rate> <gpu_id>
bash -ex ./run_cli.sh 10 exp data/prosody 4e-5 1
```

**NOTE**: it trains 10 epoch, will take nearly two hour with a single GPU A100.


### Test

it's inside the `run.sh`, in stage 1,

```sh
if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
  # Test polyphone, metric: accuracy
  python wetts/frontend/test_polyphone.py \
    --phone_dict data/polyphone/phone2id.txt \
    --prosody_dict local/prosody2id.txt \
    --test_data data/polyphone/test.txt \
    --batch_size 32 \
    --checkpoint $dir/9.pt

  # Test prosody, metric: F1-score
  python wetts/frontend/test_prosody.py \
    --phone_dict data/polyphone/phone2id.txt \
    --prosody_dict local/prosody2id.txt \
    --test_data data/prosody/cv.txt \
    --batch_size 32 \
    --checkpoint $dir/9.pt
fi
```


### Speed Benchmark


```sh
pytest -x -sv ./tests/test_prosody.py --benchmark-min-rounds 50
```
