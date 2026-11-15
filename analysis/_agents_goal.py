import io
p = r'D:\projects\cyber-reverse\AGENTS.md'
t = io.open(p, encoding='utf-8').read()
if 'docs/GOAL.md' not in t:
    t = t.replace('## 3. 改代码的纪律', '''## 2.5 目标与循环（新会话从这里接手）

新会话的 goal 原文、每轮五步循环、完成判据（a–e）、Unknown 的判定标准，都在 `docs/GOAL.md`。
一句话：**每轮从 `docs/BINDING_BACKLOG.md` 取一条未结案项，取证 → 落实现 → 复算 → 更新数字**，
完成判据必须逐条附证据，不许用"大概完成度"代替。

## 3. 改代码的纪律''', 1)
    io.open(p, 'w', encoding='utf-8', newline='').write(t)
    print('AGENTS.md 增加 §2.5 指向 GOAL.md')
else:
    print('AGENTS.md 已有指向')
