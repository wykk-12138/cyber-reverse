import io
p = r'D:\projects\cyber-reverse\replica\tools\backlog_report.py'
t = io.open(p, encoding='utf-8').read()
head = '''"""按"类型在复刻件里存不存在"给绑定缺口分类。

用法（仓库根目录）：
    <python> tools\\backlog_report.py

A 类 = 类已存在、只差成员（可以一轮做掉几个）
B 类 = 类不存在（要先抽控件/扩模型，或记为结构差异）
数字口径与 tests/Cybersole.Tests/BindingGapRatchetTests.cs 一致：剥注释 + 排除泛型噪音。
"""

'''
if not t.startswith('"""'):
    io.open(p, 'w', encoding='utf-8', newline='').write(head + t)
print('tool copied into the repo with a header')
