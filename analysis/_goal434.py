import io
p = r"D:\projects\cyber-reverse\docs\GOAL.md"
t = io.open(p, encoding='utf-8').read()

start = t.index('```\n把 Cybersole.exe')
end = t.index('```', start + 5) + 3

new_block = '''```
把 Cybersole.exe 5.18.32（.NET 10 NativeAOT，无 IL）在 D:\\projects\\cyber-reverse\\replica 里做成功能 1:1 复刻件：
函数数量对等、每个函数功能相等、效率相近；命名可不同，不要求字节级相同。根路径 D:\\projects\\cyber-reverse。

方法优先级（不可倒置）：先抄 seep-reverse-lab（D:\\projects\\seep-reverse-lab 的 MANUAL\\Tool\\skill），
再抄 rea（D:\\projects\\rea），都不覆盖才自己写，且须在文件头注明"为什么现有不够用"。
反编译是主参照，GUI（CUA）只用于消歧与定位。不常驻用不上的能力；缺依赖/缺版本由你侧装解决。

每轮固定循环，不允许"想起来就换目标"：
① 从 replica\\docs\\BINDING_BACKLOG.md 取一条未结案项（类型缺失/类型级缺口优先，其次名字级、再次截断文案）；
② 用 IDA（字符串 → xrefs → 函数 → Hex-Rays）或 rea investigate_feature 取得反编译证据；
③ 落实现（先 python tools\\snapshot.py；整块锚点替换，禁止按行号手术）；
④ 用工具复算验证（python tools\\metrics_report.py + 相关 xunit 用例，必要时全量）；
⑤ 更新 docs\\METRICS.md（生成，不手写）与 VERDICT.md 新一轮，写清"改了什么 → 哪条命令验证 → 数字怎么变 → 还剩什么"。

证据纪律（违反即结论作废）：
Observation 只能来自工具引用的证据；推理标 Inference + 置信度 + 备择解释；
覆盖不全/能力不支持/证据冲突一律显式 Unknown，并写清缺哪类证据；
绝不把"证据不全导致的缺席"当成"行为不存在"或"行为等价"。
结构对等 ≠ 行为对等：只能证明属性存在的成员，行为必须记 Unknown。
复刻件自己写出的 settings/tasks/solvers/checkoutHistory 不得当实机证据。
%APPDATA%\\Cybersole 与 %LOCALAPPDATA%\\Cybersole 只读。

数字只有一个来源：docs\\METRICS.md（由 python tools\\metrics_report.py 生成）。
当前四项度量 = 名字级缺口 / 类型级缺口 / 类型缺失 / 成员形状差异；任何文档不得硬编码这些数字。

完成判据（全部满足才算完成，逐条给证据）：
a) 类型级缺口 → 0、类型缺失 → 0（每条若不可得则写 Unknown + 缺什么）；
   名字级缺口全部三分类结案（可做 / 结构差异 / 不可得）；
b) 剩余仅"字符串池中截断"的文案，且每条写明为何不可得；
c) 产物级对照报告可复算（原版 target\\Cybersole.exe ↔ 复刻件 .publish-aot 产物）；
d) claim 表每条都有 authority（tool-evidence / manual-from-command / unknown）+ 命令 + gap_reason；
e) 全量套件绿 + 29 条变异测试全 fired + 全部文档数字来自 METRICS.md。

内存纪律：available < 2 GB 只用 -m:1 跑相关用例；< 1 GB 停止构建并先腾内存。
只有两类事可以停下来等 YG：原版登录凭据；DSH 重启/开关 MCP 条目。其它一切自行解决。
```'''

t = t[:start] + new_block + t[end:]

# 补一节：现在的状态与已决策项
anchor = '## 为什么这样改'
add = '''## 建 goal 之前先确认的四件事（R434 之后的现状）

| # | 检查 | 命令 | 期望 |
|---|---|---|---|
| 1 | 四项度量能一键生成 | `cd replica; python tools\\metrics_report.py --skip-tests` | 写出 `docs\\METRICS.md`，含名字级/类型级/类型缺失/形状四项 |
| 2 | 类型缺失度量已存在 | 同上，看 `type presence` 段 | `Cybersole.Models.Input` 补完后 ABSENT 名单只剩有 Unknown 理由的 |
| 3 | 已裁决项都已落地 | `docs\\R433_DECISIONS.md`、`docs\\R434_DECISIONS.md` | 陈旧数字一次改齐、函数级对照走 IDA 双实例、claim 表带 authority |
| 4 | 当前待办只剩 backlog 一条有证据 | `replica\\docs\\BINDING_BACKLOG.md` | MonitorView 五条（其余已 Unknown 结案），之后就是判据 e |

四项都成立 → 在新会话里 `create_goal`，粘贴上面那段 goal。

'''
t = t.replace(anchor, add + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('GOAL.md updated:', len(t), 'chars')
