#!/usr/bin/env bash

# Batch train with Grid Search

mkdir -p _logs

total_version=${1-1}
num_epoch=${2-10}

i=0
while [[ $i -lt $num_epoch ]]; do
    num_ckpt=$i
    i=$((i+1))
    dir=_backup/exp_v${total_version}
    echo "=== Test with ${num_ckpt} in ${dir}"
    bash -ex ./test_model.sh ${dir} ${num_ckpt} data/prosody_org
done


