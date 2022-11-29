#!/bin/bash

dir=$1
num_ckpt=$2

# export onnx model
python wetts/frontend/export_onnx.py \
--phone_dict data/polyphone/phone2id.txt \
--prosody_dict local/prosody2id.txt \
--checkpoint $dir/${num_ckpt}.pt \
--onnx_model $dir/${num_ckpt}.onnx

## Check loss to find better model

#
# cat ./logs/v6/run.log | grep CV | grep -v 'prosody_acc nan' | less

