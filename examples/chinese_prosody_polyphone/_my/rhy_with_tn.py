import re
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'wetts/frontend')

import logging
log = logging

from wetts.frontend.g2p_prosody import Frontend
from rhy_postprocess import process_text


def _load_frontend_model(data_dir, model_path):
    hanzi2pinyin_file = f"{data_dir}/pinyin_dict.txt"
    trad2simple_file = f"{data_dir}/traditional2simple.txt"
    polyphone_phone_file = f"{data_dir}/polyphone_phone.txt"
    polyphone_character_file = f"{data_dir}/polyphone_character.txt"
    return Frontend(
        hanzi2pinyin_file,
        trad2simple_file,
        model_path,
        polyphone_phone_file,
        polyphone_character_file)


def _compress_prosody_rank(prosody):
    """
    Combine consecutive prosody ranks):

    ---
    org=[0 1 3 1 1 0 1 0 1 0 4]
    new=[0 0 0 0 3 0 1 0 1 0 4]
    """
    # 合并连续的 sp 预测结果
    prosody_org = prosody.copy()
    for i, rhy in enumerate(prosody[1:], start=1):
        if rhy != 0 and prosody[i-1] != 0:
            if rhy < prosody[i-1]:
                prosody[i] = prosody[i-1]  # 保留较大的韵律停顿
            prosody[i-1] = 0  # 前一个reset成0
    if any(prosody_org != prosody):
        log.warning('modified prosody (combine consecutive prosody ranks):'
            ' org=%s new=%s', prosody_org, prosody)
    return prosody


def _predict_zh_prosody(frontend, text, use_pinyin=False, compress_rank=False):
    pinyin, prosody, hanzi = frontend.g2p(text)
    log.debug('pinyin: %s', pinyin)
    log.debug('prosody: %s', prosody)
    log.debug('hanzi: %s', hanzi)

    if compress_rank:
        prosody = _compress_prosody_rank(prosody)

    if use_pinyin:
        symbols = pinyin
    else:
        # symbols = re.sub(r'\W', '', hanzi)
        symbols = hanzi

    lst = []
    for ph, rhy in zip(symbols, prosody):
        if ph != 'UNK':
            lst.append(ph)
        if rhy == 4:
            continue
        if rhy != 0:
            # lst.append('sp' + str(rhy))
            lst.append(f' #{rhy} ')
    return lst


def _predict_prosody(frontend, text, use_pinyin=False):
    # segment_lst = re.sub(r'([\Wa-zA-Z\s]+)', r'_\1_', text).split('_')
    sentence_sep = r'\Wa-zA-Z0-9\s'
    # sentence_sep = ',!?;:：；，。！？、《》“”——……（）'
    segment_lst = re.sub(rf'([{sentence_sep}]+)', r'_\1_', text).split('_')
    # print('segment_lst:', segment_lst)

    lst = []
    for seg in segment_lst:
        if not seg:
            continue
        if re.search(rf'([{sentence_sep}]+)', seg):
            lst += [seg]
        else:
            lst += _predict_zh_prosody(frontend, seg, use_pinyin=use_pinyin)

    if use_pinyin:
        pinyin_str = ' '.join(lst)
    else:
        pinyin_str = ''.join(lst)
    return pinyin_str


class ProsodyPredictor:
	def __init__(self, data_dir='local', model_path='exp/9.onnx'):
		"""
		Args:
			@data_dir: dir to dict files (polyphone/prosody/trad2sim)
			@model_path: path to bert model, in ONNX format
		"""
		self._frontend = _load_frontend_model(data_dir, model_path)

	def predict(self, text: str, use_sp: bool=False):
		"""
		Args:
			@use_sp: with `sp0/sp1` if `use_sp=True`; otherwise `#2/#3` by default.

		Returns:
			A string with prosody.
		
		i.e.:
			python _my/prosody_predictor.py predict "$(head -n1 _dump/tmp.txt)"
		"""
		hanzi_w_rank = _predict_prosody(self._frontend, text)
		text = process_text(hanzi_w_rank)
		if use_sp:
			return text.replace('#2', 'sp0').replace('#3', 'sp1')
		return text


if __name__ == '__main__':
	import fire
	fire.Fire(ProsodyPredictor)
