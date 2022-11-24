import re
import sys

headers = [
    'line',
    'sub_idx',
    'tot_char',
    'char',
    'text'
]
sep = '\t'


def clean_text(s):
    return re.sub(r'[,.!?，。！？（）、]', '', s)


print(*headers, sep=sep)
for i, line in enumerate(sys.stdin, start=1):
    sub_sentence_lst = re.sub(f'([，。！？])', r'\1\n', line.strip()).split('\n')
    if '' in sub_sentence_lst:
        sub_sentence_lst.remove('')
    for j, x in enumerate(sub_sentence_lst, start=1):
        print(i, j, len(x), len(clean_text(x)), x, sep=sep)
