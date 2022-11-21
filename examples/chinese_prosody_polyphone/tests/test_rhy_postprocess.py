import sys
import pytest

from _my import rhy_postprocess as rhy


@pytest.mark.parametrize('text,expect,rank', [
    (
        '这也正是 #2 美的定义小惟家庭服务机器人 #2 四大角色 #3 的根基。',
        '这也正是 #2 美的定义小惟家庭服务机器人 #2 四大角色的根基。',
		' #3 ',
    ),
    (
        '商业保险 #2 将合并您的工资薪金 #2 计算缴纳个人所得税。',
        '商业保险将合并您的工资薪金 #2 计算缴纳个人所得税。',
		' #2 ',
    ),
	(
		'法务 #2 制定的或审核过的订单模板 #2 不需要审核',
		'法务制定的或审核过的订单模板 #2 不需要审核',
		' #2 ',
	)
])
def test_ignore_too_short_rank(text, expect, rank):
    assert rhy.ignore_too_short_rank(text, rank) == expect


@pytest.mark.parametrize('text,expect', [
    (
        '中国家庭服务机器人 #2 市场 #2 的增长潜力不容小觑。',
        '中国家庭服务机器人 #2 市场的增长潜力不容小觑。'
    ),
])
def test_compress_too_close_rank(text, expect):
    assert rhy.compress_too_close_rank(text, ' #2 ') == expect
