import logging
import re

from transformers import AutoTokenizer

from . import rhy_postprocess


try:
    import onnxruntime as ort
except ImportError:
    print('Please install onnxruntime!')
    sys.exit(1)



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
        self.tokenizer = AutoTokenizer.from_pretrained(pretrain_bert_model)
        self.ppm_sess = ort.InferenceSession(polyphone_prosody_model,
                                             providers=[
                                                 # 'TensorrtExecutionProvider',
                                                 # 'CUDAExecutionProvider',
                                                 'CPUExecutionProvider'
                                             ])
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
        tokens = self.tokenizer(list(x),
                           is_split_into_words=True,
                           return_tensors="np")['input_ids']
        ort_inputs = {'input': tokens}
        ort_outs = self.ppm_sess.run(None, ort_inputs)
        prosody_pred = ort_outs[1].argmax(-1)[0][1:-1]
        # polyphone_pred = ort_outs[0].argmax(-1)[0][1:-1]
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

