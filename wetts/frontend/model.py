# Copyright (c) 2022, Binbin Zhang (binbzha@qq.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import torch
import torch.nn as nn
import torch.nn.functional as F

from transformers import AutoModel
from transformers import DebertaV2Model
from common import BERT_PRETRAIN_MODEL


class FrontendModel(nn.Module):
    def __init__(self, num_phones: int, num_prosody: int):
        super(FrontendModel, self).__init__()
        if 'deberta' in BERT_PRETRAIN_MODEL.rsplit('/', 1)[-1].lower():
            self.bert = DebertaV2Model.from_pretrained(BERT_PRETRAIN_MODEL)
        else:
            self.bert = AutoModel.from_pretrained(BERT_PRETRAIN_MODEL)
        for param in self.bert.parameters():
            param.requires_grad_(False)
        d_model = self.bert.config.to_dict()['hidden_size']
        expected_dim = (384, 768, 1024)
        assert d_model in expected_dim, f'Expected bert encoder input dim is {expected_dim}, but got {d_model}'
        self.transform = nn.TransformerEncoderLayer(d_model=d_model,
                                                    nhead=8,
                                                    dim_feedforward=2048,
                                                    batch_first=True)
        self.phone_classifier = nn.Linear(d_model, num_phones)
        self.prosody_classifier = nn.Linear(d_model, num_prosody)

    def _forward(self, x):
        mask = x['attention_mask'] == 0
        bert_output = self.bert(**x)
        x = self.transform(bert_output.last_hidden_state,
                           src_key_padding_mask=mask)
        phone_pred = self.phone_classifier(x)
        prosody_pred = self.prosody_classifier(x)
        return phone_pred, prosody_pred

    def forward(self, x):
        return self._forward(x)

    def export_forward(self, x):
        assert x.size(0) == 1
        x = {
            'input_ids': x,
            'token_type_ids': torch.zeros(1, x.size(1), dtype=torch.int64),
            'attention_mask': torch.ones(1, x.size(1), dtype=torch.int64)
        }
        phone_logits, prosody_logits = self._forward(x)
        phone_pred = F.softmax(phone_logits, dim=-1)
        prosody_pred = F.softmax(prosody_logits, dim=-1)
        return phone_pred, prosody_pred
