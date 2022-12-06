import pytest

from _my import prosody_predictor as psp


@pytest.fixture(scope='module')
def psp_onnx_model():
    config = {
        'pretrain_bert_model': '/nfs1/nlp/models/MTBert_v0.0.3',
        'model_path': '/nfs2/speech/model/tts/frontend/wetts_psp/model/exp_v21/9.onnx',
    }
    yield psp.ProsodyPredictor(config=config)


@pytest.fixture(scope='module')
def psp_pt_model():
    config = {
        'pretrain_bert_model': '/nfs1/nlp/models/MTBert_v0.0.3',
        'model_path': '/nfs2/speech/model/tts/frontend/wetts_psp/model/exp_v21/9.pt',
    }
    yield psp.ProsodyPredictor(config=config)


@pytest.mark.parametrize('text,expect,use_sp', [
    (
        '这也正是美的定义小惟家庭服务机器人四大角色的根基。',
        '这也正是美的定义小惟家庭服务机器人 #2 四大角色的根基。',
        False,
    ),
    (
        '这也正是美的定义小惟家庭服务机器人四大角色的根基。',
        '这也正是美的定义小惟家庭服务机器人 sp0 四大角色的根基。',
        True,
    ),
    (
        '唐剑说：“从前端算法、云平台、语音模组、自然语言理解算法等都是我们自研的。”',
        '唐剑说：“从前端算法、云平台、语音模组、自然语言理解算法等 #3 都是我们自研的。”',
        False,
    ),
    (
        '唐剑说：“从前端算法、云平台、语音模组、自然语言理解算法等都是我们自研的。”',
        '唐剑说：“从前端算法、云平台、语音模组、自然语言理解算法等 sp1 都是我们自研的。”',
        True,
    ),
    (
        '商业保险将合并您的工资薪金计算缴纳个人所得税。',
        '商业保险将合并您的工资薪金 #2 计算缴纳个人所得税。',
        False,
    ),
    (
        '法务制定的或审核过的订单模板不需要审核',
        '法务制定的或审核过的订单模板不需要审核',
        False,
    )
])
def test_prosody_predictor(text, expect, use_sp, psp_onnx_model, psp_pt_model):
    assert psp_onnx_model.predict(text, use_sp=use_sp) == expect
    assert psp_pt_model.predict(text, use_sp=use_sp) == expect

