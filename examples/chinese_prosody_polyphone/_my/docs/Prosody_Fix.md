# Prosody Fix

## 韵律 good case 文本影响分析

* 文本行数

```sh
$ wc -l prosody_tuned/*.txt
  123 prosody_tuned/eval_domain_chatbot.txt
   90 prosody_tuned/eval_domain_literature.txt
   66 prosody_tuned/eval_domain_news.txt
  279 total
```

* 带 Prosody 标记的文本行数

```sh
$ grep -c '#[0-4]' prosody_tuned/*.txt
prosody_tuned/eval_domain_chatbot.txt:54
prosody_tuned/eval_domain_literature.txt:6
prosody_tuned/eval_domain_news.txt:37
```

* 初步评估 Prosody 影响率

| domain     | lines | prosody_lines | prosody_rate |
| ---------- | ----- | ------------- | ------------ |
| chatbot    | 123   | 54            | 43.90%       |
| literature | 90    | 6             | 6.67%        |
| news       | 66    | 37            | 56.06%       |
