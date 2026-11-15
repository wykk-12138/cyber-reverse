import io
src = r'''"""Consolidated copy-gap report: one table for every locale area.

R422: the first version shelled out to the other two tools once per area (38 processes) and died with E_OUTOFMEMORY on a
tight machine. This one walks the source tree once and computes both numbers in-process.
"""
import io, os, re, difflib

POOL = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
SRC = r"D:\projects\cyber-reverse\replica\src"
OUT = r"D:\projects\cyber-reverse\replica\docs\COPY_QUEUE.md"

AREAS = ['Accounts','Proxies','Tasks','Profiles','Analytics','Auth','Billing','Checkout','Data',
         'HistoryWindow','Monitor','ProfileCsv','Release','Settings','SmartActions','TaskCreator',
         'TaskGroup','Utilities','GroupModal']

raw = io.open(POOL, encoding='utf-8', errors='replace').read()
pairs = sorted(set(re.findall(r'"([A-Z][\w.]*\.[\w.]+)":\s*"([^"\n]{1,90})"', raw)))

text_parts, literals = [], set()
for dp, _d, fns in os.walk(SRC):
    if f"{os.sep}obj{os.sep}" in dp or f"{os.sep}bin{os.sep}" in dp:
        continue
    for fn in fns:
        if fn.endswith('.cs'):
            body = io.open(os.path.join(dp, fn), encoding='utf-8', errors='replace').read()
            text_parts.append(body)
            literals.update(re.findall(r'"([^"\\\n]{8,70})"', body))
text = "\n".join(text_parts)

rows = []
for area in AREAS:
    mine = [(k, v) for k, v in pairs if k.split('.')[0].lower() == area.lower()]
    missing = [(k, v) for k, v in mine if v not in text]
    near = 0
    for k, v in mine:
        if v in text:
            continue
        if any(difflib.SequenceMatcher(None, v.lower(), l.lower()).ratio() >= 0.75 for l in literals):
            near += 1
    rows.append((area, len(mine), len(missing), near))

lines = ['# 文案缺口清单（自动生成：`python tools/copy_audit_report.py`）', '',
         '| 区域 | 键/值对 | 原文缺失 | 近似错误 |', '|---|---|---|---|']
for a, total, missing, near in rows:
    lines.append('| `%s` | %d | %d | %d |' % (a, total, missing, near))
lines += ['', '## 怎么读', '',
          '- **原文缺失**：这句原文在 `src/` 里一处都没有 → 要么没做，要么写了英文同义句。',
          '- **近似错误**：几乎相同但不等 → 需要人工三分类（真缺陷 / 拼接假阳性 / 位置未定）。',
          '', '## 已知的三分类结论（R398/R401）', '',
          '| 类别 | 例子 | 处置 |', '|---|---|---|',
          '| 真缺陷 | `Disconnect` 缺席，只有状态词 | 已补（R401） |',
          '| 拼接假阳性 | `" Custom Size"` vs `1 Custom Size` | 忽略 |',
          '| 位置未定 | `Add Size` vs `Add Size(s)` | 先确认是哪个按钮 |', '',
          '## 无宿主的区域', '',
          '`Monitor` 的 7 条属于一个**复刻件里还不存在的页面**（没有 `MonitorView`）—— 不是待接线，是页面未实现。']

io.open(OUT, 'w', encoding='utf-8', newline='').write('\n'.join(lines) + '\n')
print('wrote COPY_QUEUE.md')
for a, total, missing, near in rows:
    print('   %-14s %3d  %3d missing  %3d near' % (a, total, missing, near))
'''
io.open(r"D:\projects\cyber-reverse\replica\tools\copy_audit_report.py", 'w', encoding='utf-8', newline='').write(src)
print('tool rewritten in-process')
