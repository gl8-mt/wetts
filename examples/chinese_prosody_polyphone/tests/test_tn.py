import pytest

from tn.chinese.normalizer import Normalizer


tn = Normalizer()


@pytest.mark.parametrize('text,expect', [
	(
		'美智光电研发及技术人员共有179人，占员工总人数的比例为25.11%。',
		'美智光电研发及技术人员共有一百七十九人, 占员工总人数的比例为百分之二十五点一一.'
	)
])
def test_text_normalize(text, expect):
	assert tn.normalize(text) == expect
