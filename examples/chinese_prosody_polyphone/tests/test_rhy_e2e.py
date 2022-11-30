import pytest

from _my import prosody_predictor as psp


@pytest.fixture(scope='module')
def psp_model():
    # yield psp.ProsodyPredictor('local', 'exp/9.onnx')
    yield psp.ProsodyPredictor('local', '_backup/exp_v21/9.onnx')


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
        '唐剑说：“从前端算法、云平台、语音模组、自然语言理解算法 #2 等 #3 都是我们自研的。”',
        '唐剑说：“从前端算法、云平台、语音模组、自然语言理解算法等 #3 都是我们自研的。”',
        False,
    ),
    (
        '唐剑说：“从前端算法、云平台、语音模组、自然语言理解算法 #2 等 #3 都是我们自研的。”',
        '唐剑说：“从前端算法、云平台、语音模组、自然语言理解算法等 sp1 都是我们自研的。”',
        True,
    ),
    (
        '商业保险将合并您的工资薪金计算缴纳个人所得税。',
        '商业保险将合并您的工资薪金 #2 计算缴纳个人所得税。',
		False,
    ),
	(
		'法务 #2 制定的或审核过的订单模板 #2 不需要审核',
		'法务制定的或审核过的订单模板不需要审核',
		False,
	)
])
def test_prosody_predictor(text, expect, use_sp, psp_model):
    assert psp_model.predict(text, use_sp=use_sp) == expect


@pytest.mark.parametrize('text_len', [
    5,
    10,
    20,
    30,
    50,
    100,
    150,
    200,
])
def test_benchmark(text_len, benchmark, psp_model):
    import faker
    fake = faker.Faker('zh_CN')
    text = fake.sentence(nb_words=text_len, variable_nb_words=True)[:text_len]
    benchmark(psp_model.predict, text, use_sp=True)
