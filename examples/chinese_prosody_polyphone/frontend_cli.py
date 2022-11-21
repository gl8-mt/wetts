import os
import sys
import re
import logging

logging.basicConfig(level='DEBUG')
log = logging

sys.path.insert(0, '.')
sys.path.insert(0, 'wetts/frontend')

from wetts.frontend.g2p_prosody import Frontend


os.environ['CUDA_VISIBLE_DEVICES'] = '-1'


# text = "我是你的语音助理呀，人工智能美少女哦。"
hanzi2pinyin_file = "local/pinyin_dict.txt"
trad2simple_file = "local/traditional2simple.txt"
polyphone_phone_file = "local/polyphone_phone.txt"
polyphone_character_file = "local/polyphone_character.txt"
# polyphone_prosody_model = "_backup/exp_v7/9.onnx"
polyphone_prosody_model = "_backup/exp_v21/9.onnx"

frontend = Frontend(hanzi2pinyin_file,
                    trad2simple_file,
                    polyphone_prosody_model,
                    polyphone_phone_file,
                    polyphone_character_file)


def compress_prosody_rank(prosody):
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


def _predict_zh_prosody(text, use_pinyin=False, compress_rank=False):
    pinyin, prosody, hanzi = frontend.g2p(text)
    log.debug('pinyin: %s', pinyin)
    log.debug('prosody: %s', prosody)
    log.debug('hanzi: %s', hanzi)

    if compress_rank:
        prosody = compress_prosody_rank(prosody)

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


def _make_items(line_count, text, use_pinyin=False):
    """
    @param use_pinyin: 输出使用拼音，否则使用汉字。
    """
    text = text.strip()

    testset_name = f'{line_count + 1:02d}'
    speaker_id = 'SSB3001'

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
            lst += _predict_zh_prosody(seg, use_pinyin=use_pinyin)

    if use_pinyin:
        pinyin_str = ' '.join(lst)
    else:
        pinyin_str = ''.join(lst)

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
            items = _make_items(i, line)
            if with_id:
                items.insert(0, utt_id)
            print(sep.join(map(str, items)), file=fp_out)

    if out_file:
        fp_out.close()

    return


if __name__ == '__main__':
    import fire
    fire.Fire(g2p_for_tts)
