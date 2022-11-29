import pytest
import faker

import random
import sys
import re

sys.path.insert(0, '.')
sys.path.insert(0, 'wetts/frontend')

from wetts.frontend.g2p_prosody import Frontend


frontend_model = None


def test_load_model(benchmark):
    global frontend_model
    # text = "我是你的语音助理呀，人工智能美少女哦。"
    hanzi2pinyin_file = "local/pinyin_dict.txt"
    trad2simple_file = "local/traditional2simple.txt"
    polyphone_phone_file = "local/polyphone_phone.txt"
    polyphone_character_file = "local/polyphone_character.txt"
    polyphone_prosody_model = "exp/9.onnx"
    # polyphone_prosody_model = "_backup/exp_v1/9.onnx"
    # polyphone_prosody_model = "_backup/exp_v7/9.onnx"
    # polyphone_prosody_model = "_backup/exp_v13/9.onnx"
    # polyphone_prosody_model = "_backup/exp_v21/9.onnx"
    # polyphone_prosody_model = "_backup/exp_v27/9.onnx"


    # frontend = benchmark(Frontend, hanzi2pinyin_file,
    frontend = Frontend(hanzi2pinyin_file,
                        trad2simple_file,
                        polyphone_prosody_model,
                        polyphone_phone_file,
                        polyphone_character_file)
    frontend_model = frontend
    return


def _predict_zh_prosody(frontend, text, use_pinyin=False):
    pinyin, prosody, hanzi = frontend.g2p(text)

    # 合并连续的 sp 预测结果
    for i, rhy in enumerate(prosody[1:]):
        if rhy != 0 and prosody[i-1] != 0:
            if rhy < prosody[i-1]:
                prosody[i] = prosody[i-1]  # 保留较大的韵律停顿
            prosody[i-1] = 0  # 前一个reset成0
    # pass

    if use_pinyin:
        symbols = pinyin
    else:
        symbols = re.sub(r'\W', '', hanzi)

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


def get_text_generator(min_words=1, max_words=510):
    fake = faker.Faker('zh_CN')

    def _gen_sentence(n_words=None):
        if not n_words:
            n_words = random.randint(min_words, max_words)
        return fake.sentence(nb_words=n_words, variable_nb_words=True)[:max_words]

    return _gen_sentence


text_generator = get_text_generator()


def run_predict():
    global frontend_model
    global text_generator

    frontend = frontend_model
    text = text_generator()
    # print(f'random text len={len(text)}, content={text}')
    # print(f'random text len={len(text)}')
    return _predict_zh_prosody(frontend, text)


@pytest.mark.parametrize('text_len', [
    5,
    10,
    30,
    50,
    100,
    150,
    200,
])
def test_predict_zh_prosody(text_len, benchmark):
    text = text_generator(text_len)
    benchmark(_predict_zh_prosody, frontend_model, text)
