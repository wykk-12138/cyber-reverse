import io
t = io.open(r'D:\projects\cyber-reverse\docs\GOAL.md', encoding='utf-8').read()
start = t.index('## ▣ goal 原文')
end = t.index('## 为什么这样改')
block = t[start:end]
print('goal 块字符数:', len(block))
print(block)
