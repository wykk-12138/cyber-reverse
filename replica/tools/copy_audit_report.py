"""Consolidated copy-gap report: one table for every locale area.

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

# R981: the three constants above are the defaults; this lets them be overridden from the command line before anything is
# opened, and the rest of the module is untouched.
#
# The reason is the guard, not convenience. `CopyAuditConsistencyTests` requires the detail row count to equal the
# summary's missing total, and with the real gap at zero that invariant is 0 == 0 -- no edit to either loop can break it,
# so no mutation of this file can make the guard fail. A guard that cannot fail is not evidence. The guard therefore also
# runs this tool over a two-line fixture in which one key's name appears in the source while its value does not, which is
# the one shape where the wide and narrow predicates disagree. Without these flags the tool can only ever be pointed at the
# real tree and the guard stays untestable.
import argparse as _argparse

_ap = _argparse.ArgumentParser(description="Consolidated copy-gap report (defaults: the real pool, source and output).")
_ap.add_argument("--pool", default=POOL, help="string pool to read key/value pairs from")
_ap.add_argument("--src", default=SRC, help="source tree to look the values up in")
_ap.add_argument("--out", default=OUT, help="report to write")
_args = _ap.parse_args()
POOL, SRC, OUT = _args.pool, _args.src, _args.out

raw = io.open(POOL, encoding='utf-8', errors='replace').read()
# R542: the first pattern was r'"([A-Z][\w.]*\.[\w.]+)":\s*"([^"\n]{1,90})"'. `[^"\n]` stops at the first double
# quote, so any value containing an escaped quote (`\"{0}\"`) was cut at the backslash and the *fragment* was then
# looked for in the source. Five keys were reported as "truncated in the string pool" on that basis.
#
# The pool actually holds them intact:
#     "ProfileCsv.Error.UnknownCountry": "Unknown country \"{0}\"",
#     "Settings.General.MonitorConcurrency.Tooltip": "… when using the \"Shared Monitor\" monitor mode.",
#
# So the value pattern now admits backslash escapes, and the length cap is raised well past the longest real
# value. Anything still missing after this is genuinely absent from the source, not cut off by us.
pairs = sorted(set(
    (m.group(1), m.group(2).replace('\\"', '"').replace('\\\\', '\\'))
    for m in re.finditer(r'"([A-Z][\w.]*\.[\w.]+)":\s*"((?:[^"\\\n]|\\.){1,400})"', raw)
))

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


def _source_forms(value):
    """Ways a runtime string can be spelled inside a C# source file. (R589)

    The first form is the value itself; the second escapes backslash, quote, newline and tab the way a C# literal
    does. Without the second, a value containing a double quote can never match the source and is reported missing.
    """
    yield value
    yield value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t")


def _present(value, text):
    if any(form in text for form in _source_forms(value)):
        return True
    # R626: a value containing newlines is usually written as two adjacent literals joined with "\n", so the whole
    # string never appears contiguously. `Utilities.StoreGroups.Delete.UsedMessageFormat` was reported missing for
    # exactly this reason while its text sat in the source, split in two. Requiring every non-empty part is precise:
    # it cannot be satisfied by a coincidence of fragments.
    # R626: the pool keeps `\n` as the two characters backslash+n, not as a newline, so both spellings must be
    # considered. `Utilities.StoreGroups.Delete.UsedMessageFormat` was reported missing for exactly this reason while
    # its text sat in the source, split across two adjacent literals.
    sep = "\n" if "\n" in value else ("\\n" if "\\n" in value else None)
    if sep is not None:
        parts = [p.strip() for p in value.split(sep) if p.strip()]
        if len(parts) > 1 and all(any(form in text for form in _source_forms(p)) for p in parts):
            return True
    return False


def _without_comments(text):
    """Source with comments removed. (R626)

    A locale key mentioned in a trailing comment is not a key the code looks up. The `_satisfied` predicate accepted
    any occurrence, so `// Utilities.StoreGroups.Delete.UsedMessageFormat` counted as a reference -- the number came
    out right by accident while the rule was wrong.
    """
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"//[^\n]*", " ", text)
    return text


def _satisfied(key, value, text, code):
    """Is this locale entry in use? (R622/R626)

    The value (or all of its newline-separated parts) appearing in the source is one signal. An application that
    resolves text through a locale table **never** spells the value in code -- it looks the key up -- so a key the
    code references also counts.

    But it must be referenced *in code*: `code` is the source with comments stripped, because a key named only in a
    comment is documentation, not a lookup.
    """
    if _present(value, text):
        return True
    return key in code


# R626: comments are not lookups -- the key predicate runs against the source with comments stripped
code = _without_comments(text)

rows = []
for area in AREAS:
    mine = [(k, v) for k, v in pairs if k.split('.')[0].lower() == area.lower()]
    missing = [(k, v) for k, v in mine if not _satisfied(k, v, text, code)]
    near = 0
    for k, v in mine:
        if _satisfied(k, v, text, code):
            continue
        if any(difflib.SequenceMatcher(None, v.lower(), l.lower()).ratio() >= 0.75 for l in literals):
            near += 1
    rows.append((area, len(mine), len(missing), near))

lines = ['# 文案缺口清单（自动生成：`python tools/copy_audit_report.py`）', '',
         '> 本文件是**生成物**，数字每次重跑都会刷新。汇总口径见 `docs/METRICS.md`（R433 裁决 1）。', '',
         '| 区域 | 键/值对 | 原文缺失 | 近似错误 |', '|---|---|---|---|']
for a, total, missing, near in rows:
    lines.append('| `%s` | %d | %d | %d |' % (a, total, missing, near))
lines += ['', '## 怎么读', '',
          '- **原文缺失**：这句原文**和它的 key 名**在 `src/` 里都一处没有 → 代码从不查这条文案。',
          '  只要 key 名出现就算"在用"（R622）：走 locale 的应用不会把值写在源码里，它按 key 查表。',
          '- **近似错误**：几乎相同但不等 → 需要人工三分类（真缺陷 / 拼接假阳性 / 位置未定）。',
          '', '## 已知的三分类结论（R398/R401）', '',
          '| 类别 | 例子 | 处置 |', '|---|---|---|',
          '| 真缺陷 | `Disconnect` 缺席，只有状态词 | 已补（R401） |',
          '| 拼接假阳性 | `" Custom Size"` vs `1 Custom Size` | 忽略 |',
          '| 位置未定 | `Add Size` vs `Add Size(s)` | 先确认是哪个按钮 |', '',
          '## 无宿主的区域', '',
          '`Monitor` 的 7 条属于一个**复刻件里还不存在的页面**（没有 `MonitorView`）—— 不是待接线，是页面未实现。']

# R542: the table above only says **how many** keys are absent. A criterion that requires "each one says why it
# is unobtainable" needs the keys themselves, so list them. Without this the count 5 is unfalsifiable.
lines += ['', '## 原文缺失明细（R542 新增）', '',
          '> 判据 b 要求"每条写明为何不可得"。下表是那几条本体 —— 没有它，"5 条"只是一个无法核对的数。', '',
          '| 区域 | 键 | 原文 |', '|---|---|---|']
# R590: this loop used `if v not in text` -- the narrow comparison R589 replaced in the totals above. The two
# numbers disagreed (4 in the summary, 6 rows here) because one consumer of the predicate was updated and the other
# was not. Same predicate for both now.
detail_rows = 0
for area in AREAS:
    mine = [(k, v) for k, v in pairs if k.split('.')[0].lower() == area.lower()]
    for k, v in mine:
        if not _satisfied(k, v, text, code):
            lines.append('| `%s` | `%s` | %s |' % (area, k, v))
            detail_rows += 1

io.open(OUT, 'w', encoding='utf-8', newline='').write('\n'.join(lines) + '\n')
print('wrote COPY_QUEUE.md')
total_missing = 0
for a, total, missing, near in rows:
    print('   %-14s %3d  %3d missing  %3d near' % (a, total, missing, near))
    total_missing += missing
# R590: print both, so a future divergence shows up in the command output instead of hiding inside the file.
# R591: this must NOT look like a zone row. `metrics_report.py` parses `^\s+(\S+)\s+\d+\s+(\d+) missing`, so
# `TOTAL  649  4 missing` was counted as a fourth zone and the published figure became 8 (in 4 zones).
print('   ---- summary ---- %d zone(s) | %d key(s) | %d missing | %d near'
      % (sum(1 for r in rows if r[2]), sum(r[1] for r in rows), total_missing, sum(r[3] for r in rows)))
print('   detail rows: %d  (must equal the TOTAL missing count)' % detail_rows)
if detail_rows != total_missing:
    print('   WARNING: detail rows %d != total missing %d' % (detail_rows, total_missing))
