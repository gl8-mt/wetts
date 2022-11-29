from transformers import BertTokenizer
from transformers import BertModel

import time

BERT_PRETRAIN_MODEL_LIST = [
    'hfl/chinese-roberta-wwm-ext',
    'hfl/chinese-roberta-wwm-ext-large',
    'hfl/chinese-roberta-wwm-ext',
    'hfl/chinese-bert-wwm-ext',
    'hfl/chinese-bert-wwm',
    'hfl/rbt3',
    'hfl/rbtl3',
]


def load_bert_model(model_name):
    print(f'Load bert model {model_name}')
    tokenizer = BertTokenizer.from_pretrained(model_name)
    t0 = time.time()
    model = BertModel.from_pretrained(model_name)
    t1 = time.time()
    print(f'Done load model et={t1 - t0} seconds.')
    return model


for i, model_name in enumerate(BERT_PRETRAIN_MODEL_LIST):
    load_bert_model(model_name)

