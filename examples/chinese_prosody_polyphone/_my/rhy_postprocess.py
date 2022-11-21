"""
Function:
	在预测 Prosody 结果后，加入策略，调整停顿标记。

Method:

	1. 如果有 #3， 对应 sp0；
	2. 如果没有 #3，启用 #2；
		* 一定长度N
		* 经统计分析，暂定 N=16
			* N 字以上，需要韵律预测
			* N 字以下，不启用韵律
		* 多个 #2，使用最中间的
	3. 子句长度
		* #3 
"""

import logging
import re
logging.basicConfig(level='DEBUG')


def get_xml_break(sp):
	# return f'<break time="{sp}"/>'
	return f' {sp} '


def ignore_too_short_rank(text, rank, min_dist=6):
	lst = text.split(rank)
	lst = [x.strip() for x in lst]
	if len(lst) > 1:
		if len(lst[0]) < min_dist:
			logging.info(f'ignore {rank} at the begin of {text}')
			lst[1] = lst[0] + lst[1]
			lst.pop(0)
	if len(lst) > 1:  # 2段以上，就区分头尾
		if len(lst[-1]) < min_dist:
			logging.info(f'ignore {rank} at the end of {text}')
			lst[-2] = lst[-2] + lst[-1]
			lst.pop(-1)
	logging.debug(f'too short lst: {lst}')
	return rank.join(lst)


def compress_too_close_rank(text, rank, min_dist=6):
	lst = text.split(rank)
	lst = [x.strip() for x in lst]
	rank_lst = []
	for i, x in enumerate(lst):
		if len(x) < min_dist:
			rank_lst.append('')
		else:
			rank_lst.append(rank)
	res = []
	for x, y in zip(lst, rank_lst):
		res.append(x)
		res.append(y)
	res = res[:-1]  # drop the last rank
	return ''.join(res)


def adjust_prosody_v1(text, len_thresh=16, map_rank3='#3', map_rank2='#2', map_rank1=None):
	''''
	
	Strategy:
		* #3 映射 sp1
		* 启用 #2，映射为 sp0
	'''
	if not text:
		return text
	
	rank3 = ' #3 '
	rank2 = ' #2 '
	rank1 = ' #1 '
	xml_rank3 = get_xml_break(map_rank3) if map_rank3 else ''
	xml_rank2 = get_xml_break(map_rank2) if map_rank2 else ''

	if not map_rank1:
		text = text.replace(rank1, '')
	
	lst = text.split(rank3)

	res_lst = []
	for sub_text in lst:
		sub_text = ignore_too_short_rank(sub_text, rank2, min_dist=6)  # avoid "理解算法 #2 等 #3 都是"
		if len(sub_text) < len_thresh or rank2 not in sub_text:
			new_sub_text = sub_text.replace(rank2, '')  # ignore
		else:
			new_sub_text = sub_text.replace(rank2, xml_rank2)
		res_lst.append(new_sub_text)
	return xml_rank3.join(res_lst)


def remove_rank(text, rank):
	return text.replace(rank, '')


def process_rhy(text):
	text = remove_rank(text, ' #1 ')
	text = ignore_too_short_rank(text, ' #3 ')
	text = ignore_too_short_rank(text, ' #2 ')
	text = compress_too_close_rank(text, ' #3 ')
	text = compress_too_close_rank(text, ' #2 ')
	text = adjust_prosody_v1(text)
	# text = f'<speak>{text}</speak>'
	return text


def process_text(text):
	lst = [process_rhy(x) for x in split_sentences(text)]
	return ''.join(lst)


def split_sentences(line):
	sentence_sep = '-,.!?;:：；，。！？、《》——'
	sub_sentence_lst = re.sub(rf'([{sentence_sep}])', r'\1\n', line.strip()).split('\n')
	if '' in sub_sentence_lst:
		sub_sentence_lst.remove('')
	logging.debug(f'sub_sentence_lst: {sub_sentence_lst}')
	return sub_sentence_lst


def process_file(file, sep=' '):
	with open(file) as f:
		for line in f:
			if not line.strip():
				continue
			if sep:
				utt_id, text = line.strip().split(sep=sep, maxsplit=1)
				r = process_text(text)
				r = f'{utt_id}{sep}{r}'
			else:
				r = process_text(line)
			print(r)


def test_process_text():
	_text = """2|商业 #1 保险 #2 将合并 #1 您的 #1 工资 #1 薪金 #2 计算 #1 缴纳 #1 个人 #1 所得税。
4|您在 #1 个人 #1 所得税app中 #1 查询到您的 #1 收入 #2 会比 #1 工资单上 #1 收入 #1 增加 #3 公积金缴纳 #1 金额 #2 高于 #1 个人 #1 所得税 #1 免税 #1 上限的 #1 金额。
5|只要 #1 您的 #1 子女 #2 符合 #1 条件 #3 即可 #1 享受 #2 每位 #1 子女一千元/月的 #1 专项 #1 附加 #1 扣除。
0|这也正是 #2 美的定义小惟家庭服务机器人 #2 四大角色 #3 的根基。
"""

	lines = _text.split('\n')
	sep = '|'

	for line in lines:
		if not line.strip():
			continue
		utt_id, text = line.strip().split(sep=sep, maxsplit=1)

		new_text = process_text(text)

		# print('[OLD]', utt_id, text.replace(' #1 ', ''))
		print('[NEW]', utt_id, new_text)


if __name__ == '__main__':
	# test_process_text()
	import fire
	fire.Fire(process_file)
