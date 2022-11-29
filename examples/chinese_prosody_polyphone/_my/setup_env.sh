#!/bin/bash

set -e

dst_root_dir=${1-_tmp/wetts_psp}

proj_dir=$(dirname $0)

echo "Install python deps ..."
pip install -r ${proj_dir}/requirements.txt

echo "Copy model files ..."
data_root_dir=/nfs2/speech/model/tts/frontend/wetts_psp
dict_dir=${data_root_dir}/local
model_path=${data_root_dir}/model/exp_v21/9.onnx

# dict files
mkdir -p ${dst_root_dir}
cp -R -v $dict_dir $dst_root_dir

# onnx model file
mkdir -p ${dst_root_dir}/exp
cp -v $model_path ${dst_root_dir}/exp

echo "Done. model files is inside ${dst_root_dir}"
