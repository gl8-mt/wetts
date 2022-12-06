import logging
import re

import torch
import torch.nn as nn
import torch.nn.functional as F

from transformers import AutoModel
from transformers import AutoTokenizer

try:
    import onnxruntime as ort
except ImportError:
    print('Please install onnxruntime!')
    sys.exit(1)


from . import rhy_postprocess


class FrontendModel(nn.Module):

    def __init__(self, num_phones: int, num_prosody: int, pretrain_bert_model: str = None):
        super(FrontendModel, self).__init__()
        self.bert = AutoModel.from_pretrained(pretrain_bert_model)
        for param in self.bert.parameters():
            param.requires_grad_(False)
        d_model = self.bert.config.to_dict()['hidden_size']
        assert d_model in (768, 1024), 'Expected bert encoder input dim is 768 or 1024'
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


def _add_prosody_into_text(text, prosody):
    lst = []
    for ph, rhy in zip(text, prosody):
        if ph != 'UNK':
            lst.append(ph)
        if rhy == 4:
            continue
        if rhy != 0:
            # lst.append('sp' + str(rhy))
            lst.append(f' #{rhy} ')
    return lst
    


def _predict_zh_prosody(frontend, text, use_pinyin=False):
    pinyin, prosody, hanzi = frontend.g2p(text)
    logging.debug('pinyin: %s', pinyin)
    logging.debug('prosody: %s', prosody)
    logging.debug('hanzi: %s', hanzi)

    if use_pinyin:
        symbols = pinyin
    else:
        # symbols = re.sub(r'\W', '', hanzi)
        symbols = hanzi

    return _add_prosody_into_text(symbols, prosody)



def _predict_prosody(frontend, text, use_pinyin=False):

    def _split_sentence(text):
        segment_lst = re.sub(rf'([{sentence_sep}]+)', r'_\1_', text).split('_')
        return segment_lst

    sentence_sep = r'\Wa-zA-Z\s'
    segment_lst = _split_sentence(text)
    if len(segment_lst) > 1:
        logging.info('split sentence segment list: %s', segment_lst)

    lst = []
    for seg in segment_lst:
        if not seg:
            continue
        if not re.search(rf'([{sentence_sep}]+)', seg):
            seg_lst = _predict_zh_prosody(frontend, seg, use_pinyin=use_pinyin)
            lst += seg_lst
        else:
            lst.append(seg)


    if use_pinyin:
        pinyin_str = ' '.join(lst)
    else:
        pinyin_str = ''.join(lst)
    return pinyin_str


class FrontendPtRuntime(object):

    def __init__(self,
            checkpoint: str,
            pretrain_bert_model: str,
            num_phones: int = 876,  # local/polyphone_phone.txt
            num_prosody: int = 5,   # local/prosody2id.txt
            device: str = 'cpu',
    ):
        # Init model
        model = FrontendModel(num_phones, num_prosody, pretrain_bert_model)

        model.load_state_dict(torch.load(checkpoint, map_location='cpu'))
        model.to(device)

        model.eval()

        self.model = model
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(pretrain_bert_model)

    def run(self, x):
        with torch.no_grad():
            # tokens = self.tokenizer.encode(x, add_special_tokens=False)
            inputs = self.tokenizer(list(x),
                             padding=True,
                             truncation=True,
                             is_split_into_words=True,
                             return_tensors="pt"
                         )['input_ids']
            phone_pred, prosody_pred = self.model.export_forward(inputs)
        return phone_pred, prosody_pred


class FrontendOnnxRuntime(object):

    def __init__(self,
            polyphone_prosody_model: str,
            pretrain_bert_model: str,
            device: str = 'cpu',
    ):
        provider_map = {
            'cpu': 'CPUExecutionProvider',
            'cuda': 'CUDAExecutionProvider',
            'tensorrt': 'TensorrtExecutionProvider',
            # 'mtgpu': 'xxx',
        }
        self.ppm_sess = ort.InferenceSession(
            polyphone_prosody_model,
            providers=[
                provider_map[device],
                ]
            )
        self.tokenizer = AutoTokenizer.from_pretrained(pretrain_bert_model)

    def run(self, x):
        tokens = self.tokenizer(list(x),
                           is_split_into_words=True,
                           return_tensors="np")['input_ids']
        ort_inputs = {'input': tokens}
        phone_pred, prosody_pred = self.ppm_sess.run(None, ort_inputs)
        return phone_pred, prosody_pred


class Frontend(object):

    def __init__(
        self,
        polyphone_prosody_model: str,
        pretrain_bert_model: str,
        # hanzi2pinyin_file: str,
        # trad2simple_file: str,
        # polyphone_phone_file: str,
        # polyphone_character_file: str,
    ):
        runtime_map = {
            'onnx': FrontendOnnxRuntime,
            'pt': FrontendPtRuntime,
            'pth': FrontendPtRuntime,
        }
        model_extension = polyphone_prosody_model.rsplit('.', 1)[-1]
        assert model_extension in runtime_map, \
                f'model extension must be {list(runtime_map)}, but got {model_extension}'

        runtime_cls = runtime_map[model_extension]
        logging.info(f'use runtime {runtime_cls}')

        self.sess = runtime_cls(polyphone_prosody_model, pretrain_bert_model, device='cpu')

        # self.hanzi2pinyin = Hanzi2Pinyin(hanzi2pinyin_file)
        # self.tn = Normalizer()
        # self.t2s = T2S(trad2simple_file)
        # self.polyphone_phone_dict = []
        # self.polyphone_character_dict = []
        # with open(polyphone_phone_file) as pp_f:
        #     for line in pp_f.readlines():
        #         self.polyphone_phone_dict.append(line.strip())
        # with open(polyphone_character_file) as pc_f:
        #     for line in pc_f.readlines():
        #         self.polyphone_character_dict.append(line.strip())

    def g2p(self, x):
        # # traditionl to simple
        # x = self.t2s.convert(x)
        # # text normalization
        # x = self.tn.normalize(x)
        # # hanzi2pinyin
        # pinyin = self.hanzi2pinyin.convert(x)
        # polyphone disambiguation & prosody prediction
        pinyin = None
        outs = self.sess.run(x)
        prosody_pred = outs[1].argmax(-1)[0][1:-1]
        # polyphone_pred = outs[0].argmax(-1)[0][1:-1]
        # index = 0
        # for char in x:
        #     if char in self.polyphone_character_dict:
        #         pinyin[index] = self.polyphone_phone_dict[polyphone_pred[index]]
        #     index += 1
        # return pinyin, prosody_pred
        return pinyin, prosody_pred, x


class ProsodyPredictor:

    _DEFAULT_CONFIG = {
        'pretrain_bert_model': '/nfs1/nlp/models/MTBert_v0.0.3',
        'model_path': '/nfs2/speech/model/tts/frontend/wetts_psp/model/exp_v21/9.onnx',
        # 'model_path': '/nfs2/speech/model/tts/frontend/wetts_psp/model/exp_v21/9.pt',
    }

    def __init__(self, config: dict = None):
        if config:
            assert isinstance(config, dict), "config type must be dict"
        else:
            config = ProsodyPredictor._DEFAULT_CONFIG
            
        self.frontend = Frontend(config['model_path'], config['pretrain_bert_model'])

    def predict(self, text: str, use_sp: bool=False, use_postprocess=True) -> str:
        """
        摩尔线程真棒 => 摩尔线程 sp0 真棒

        Args:
            @use_sp: with `sp0/sp1` if `use_sp=True`; otherwise `#2/#3` by default.
        """
        # text is hanzi

        # pinyin, prosody, hanzi = self.frontend.g2p(text)
        # seg_lst = _add_prosody_into_text(text, prosody)
        # text = ''.join(seg_lst)

        text = _predict_prosody(self.frontend, text)

        if use_postprocess:
            text = rhy_postprocess.process_text(text)
        if use_sp:
            text = text.replace('#2', 'sp0').replace('#3', 'sp1')
        return text


if __name__ == '__main__':
	import fire
	fire.Fire(ProsodyPredictor)

