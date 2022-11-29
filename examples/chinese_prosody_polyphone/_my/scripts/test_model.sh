#!/bin/bash

dir=${1-backup/exp_v1}
num_ckpt=${2-9}
prosody_data_dir=${3-data/prosody_org}

t0=$SECONDS

# Test polyphone, metric: accuracy
python wetts/frontend/test_polyphone.py \
  --phone_dict data/polyphone/phone2id.txt \
  --prosody_dict local/prosody2id.txt \
  --test_data data/polyphone/test.txt \
  --batch_size 32 \
  --checkpoint $dir/${num_ckpt}.pt

echo "Done test polyphone, et=$((SECONDS - t0))"

t0=$SECONDS

# Test prosody, metric: F1-score
python wetts/frontend/test_prosody.py \
    --phone_dict data/polyphone/phone2id.txt \
    --prosody_dict local/prosody2id.txt \
    --test_data ${prosody_data_dir}/cv.txt \
    --batch_size 32 \
    --checkpoint $dir/${num_ckpt}.pt

echo "Done test prosody, et=$((SECONDS - t0))"
