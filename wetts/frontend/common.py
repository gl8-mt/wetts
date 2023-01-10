import os
import logging

# BERT_PRETRAIN_MODEL = 'bert-base-chinese'
# BERT_PRETRAIN_MODEL = 'prajjwal1/bert-medium'
# BERT_PRETRAIN_MODEL = 'prajjwal1/bert-small'
# BERT_PRETRAIN_MODEL = 'prajjwal1/bert-tiny'

# BERT_PRETRAIN_MODEL = os.environ.get('BERT_PRETRAIN_MODEL', BERT_PRETRAIN_MODEL)

## === 基于全词掩码（Whole Word Masking）技术的中文预训练模型BERT-wwm ===
#
# https://github.com/ymcui/Chinese-BERT-wwm
#
# BERT_PRETRAIN_MODEL = 'hfl/chinese-roberta-wwm-ext-large'
# BERT_PRETRAIN_MODEL = 'hfl/chinese-roberta-wwm-ext'

## === MT ===
#
# BERT_PRETRAIN_MODEL = '/nfs1/nlp/models/MTBert_v0.0.1'
# BERT_PRETRAIN_MODEL = '/nfs1/nlp/models/MTBert_v0.0.3'
# BERT_PRETRAIN_MODEL = '/nfs1/nlp/models/deberta'
# BERT_PRETRAIN_MODEL = '/nfs1/nlp/models/deberta-small'
# BERT_PRETRAIN_MODEL = '/nfs1/nlp/models/deberta-xsmall'
BERT_PRETRAIN_MODEL = '/nfs1/nlp/models/bert-small'

# BERT_PRETRAIN_MODEL = '/nfs1/nlp/models/bert-base'
# BERT_PRETRAIN_CONFIG = '/nfs1/nlp/models/bert-base/config_base.json'
# BERT_PRETRAIN_CONFIG = '/nfs1/nlp/models/bert-base/config_half.json'
# BERT_PRETRAIN_CONFIG = '/nfs1/nlp/models/bert-base/config_small.json'

logging.warning(f'fine-tune with pretrain bert {BERT_PRETRAIN_MODEL}')
