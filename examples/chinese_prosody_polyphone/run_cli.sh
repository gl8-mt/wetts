#!/usr/bin/env bash
# Copyright 2022 Binbin Zhang(binbzha@qq.com)

stage=${6--1}
stop_stage=${7-100}
url=https://wetts-1256283475.cos.ap-shanghai.myqcloud.com/data/

num_epochs=${1-10}
dir=${2-exp}
prosody_data_dir=${3-data/prosody}
learning_rate=${4-4e-5}
gpu=${5--1}


export CUDA_VISIBLE_DEVICES=${gpu}
num_ckpt=$((num_epochs - 1))

if [ ${stage} -le -1 ] && [ ${stop_stage} -ge -1 ]; then
  # Download prosody and polyphone
  mkdir -p data/download
  pushd data/download
  wget -c $url/polyphone.tar.gz && tar zxf polyphone.tar.gz
  wget -c $url/prosody.tar.gz && tar zxf prosody.tar.gz
  popd

  # Combine prosody data
  mkdir -p data/prosody
  cat data/download/prosody/biaobei/train.txt > data/prosody/train.txt
  cat data/download/prosody/biaobei/cv.txt > data/prosody/cv.txt
  # Combine polyphone data
  mkdir -p data/polyphone
  cat data/download/polyphone/g2pM/train.txt > data/polyphone/train.txt
  cat data/download/polyphone/g2pM/dev.txt > data/polyphone/cv.txt
  cat data/download/polyphone/g2pM/test.txt > data/polyphone/test.txt
  cp data/download/polyphone/g2pM/phone2id.txt data/polyphone/phone2id.txt
fi


if [ ${stage} -le 0 ] && [ ${stop_stage} -ge 0 ]; then
  mkdir -p $dir
  et=$SECONDS

  python wetts/frontend/train.py --gpu ${gpu} \
    --lr ${learning_rate} \
    --num_epochs ${num_epochs} \
    --batch_size 32 \
    --log_interval 10 \
    --phone_weight 0.1 \
    --phone_dict data/polyphone/phone2id.txt \
    --train_polyphone_data data/polyphone/train.txt \
    --cv_polyphone_data data/polyphone/cv.txt \
    --prosody_dict local/prosody2id.txt \
    --train_prosody_data ${prosody_data_dir}/train.txt \
    --cv_prosody_data ${prosody_data_dir}/cv.txt \
    --model_dir $dir

  et=$((SECONDS - et))
  echo "Done training, elapse ${et}"
fi


if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
  et=$SECONDS

  # # Test polyphone, metric: accuracy
  # python wetts/frontend/test_polyphone.py \
  #   --phone_dict data/polyphone/phone2id.txt \
  #   --prosody_dict local/prosody2id.txt \
  #   --test_data data/polyphone/test.txt \
  #   --batch_size 32 \
  #   --checkpoint $dir/${num_ckpt}.pt

  # Test prosody, metric: F1-score
  python wetts/frontend/test_prosody.py \
    --phone_dict data/polyphone/phone2id.txt \
    --prosody_dict local/prosody2id.txt \
    --test_data ${prosody_data_dir}/cv.txt \
    --batch_size 32 \
    --checkpoint $dir/${num_ckpt}.pt

  et=$((SECONDS - et))
  echo "Done testing, elapse ${et}"
fi


if [ ${stage} -le 2 ] && [ ${stop_stage} -ge 2 ]; then
  # export onnx model
  python wetts/frontend/export_onnx.py \
    --phone_dict data/polyphone/phone2id.txt \
    --prosody_dict local/prosody2id.txt \
    --checkpoint $dir/${num_ckpt}.pt \
    --onnx_model $dir/${num_ckpt}.onnx
fi


if [ ${stage} -le 3 ] && [ ${stop_stage} -ge 3 ]; then
  # g2p
  # text: 8方財寶進
  # pinyin ['ba1', 'fang1', 'cai2', 'bao3', 'jin4']
  # prosody [0 1 0 0 4]

      # --text "我是你的语音助理呀，人工智能美少女哦。" \
  python wetts/frontend/g2p_prosody.py \
    --text "8方財寶進" \
    --hanzi2pinyin_file local/pinyin_dict.txt \
    --trad2simple_file local/traditional2simple.txt \
    --polyphone_phone_file local/polyphone_phone.txt \
    --polyphone_character_file local/polyphone_character.txt \
    --polyphone_prosody_model $dir/${num_ckpt}.onnx
fi
