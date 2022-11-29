import os
import sys
import logging

# logging.basicConfig(level='DEBUG')

sys.path.insert(0, '.')
sys.path.insert(0, 'wetts/frontend')

from wetts.frontend.g2p_prosody import Frontend
from _my.prosody_predictor import _load_frontend_model, _predict_prosody


# os.environ['CUDA_VISIBLE_DEVICES'] = '-1'


def _make_items(text, use_pinyin=False, line_count=None):
    """
    @param use_pinyin: 输出使用拼音，否则使用汉字。
    """
    global g_frontend
    
    text = text.strip()

    # if line_count:
    #     testset_name = f'{line_count + 1:02d}'
    
    if not g_frontend:
        g_frontend = _load_frontend_model(_data_dir, _polyphone_prosody_model)
    pinyin_str = _predict_prosody(g_frontend, text, use_pinyin)

    items = [
        # testset_name,
        # speaker_id,
        # '',  # placeholder for yichao@mt
        # text,
        pinyin_str,
        # ' '.join(pinyin),
    ]
    return items


def g2p_for_tts(in_file, out_file=None, with_id=False, sep= ' '):
    # QYTest01|SSB3001||mo2 er3 sp1 xian4 cheng2|摩尔线程

    # text_file = 'prosody_test_zh.txt'

    if out_file:
        fp_out = open(out_file, 'w')
    else:
        fp_out = sys.stdout

    with open(in_file) as fp:
        for i, line in enumerate(fp):
            if with_id:
                utt_id, line = line.split(maxsplit=1)
            items = _make_items(line, line_count=i)
            if with_id:
                items.insert(0, utt_id)
            print(sep.join(map(str, items)), file=fp_out)

    if out_file:
        fp_out.close()

    return


if __name__ == '__main__':
    import fire
    _data_dir='local'
    _polyphone_prosody_model = "_backup/exp_v21/9.onnx"
    g_frontend = None
    fire.Fire(g2p_for_tts)
