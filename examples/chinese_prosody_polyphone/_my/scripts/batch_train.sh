#!/usr/bin/env bash

# Batch train with Grid Search

mkdir -p _logs

# ./run_cli.sh 10 _backup/exp_v10  &> _logs/exp_v10.log

# total_version=9
# total_version=13
# total_version=17
# total_version=21
# total_version=25
total_version=26
cuda_device=2

num_epoch=10

# for learning_rate in 1e-5 2e-5 3e-5 4e-5; do
for learning_rate in 4e-5 5e-5; do
    total_version=$((total_version + 1))
    cuda_device=$((cuda_device + 1))

    echo "Start exp ${total_version} learning_rate ${learning_rate}"
    cmd="bash -ex ./run_cli.sh ${num_epoch} _backup/exp_v${total_version} data/prosody_org ${learning_rate} ${cuda_device}"
    ($cmd &>_logs/exp_v${total_version}.log) &
done

wait

# i=0
# while [[ $i -lt $num_epoch ]]; do
#     num_ckpt=$i
#     i=$((i+1))
#     dir=_backup/exp_v${total_version}
#     echo "=== Test with ${num_ckpt} in ${dir}"
#     bash -ex ./test_model.sh ${dir} ${num_ckpt} data/prosody_org
# done

