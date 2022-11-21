FROM pytorch/pytorch:1.13.0-cuda11.6-cudnn8-devel

LABEL MAINTAINER "guang.liang@mthreads.com"

RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install transformers==4.22.2
# cpu version
RUN pip install onnxruntime==1.12.1
# For: f1 score metrics, TN
RUN pip install scikit-learn WeTextProcessing

RUN apt update -y
RUN apt install wget -y

RUN pip install fire faker
RUN pip install pytest pytest-benchmark