"""R1380b: the C8 row must stay six cells — my rewrite gave four and the claims audit dropped the row.

`analysis/check_claims.py` walks every claim table and keeps rows with at least six cells; `ClaimsCoverageTests` compares
its row count with an independent count. My replacement row had four cells, so the script's count fell by one and the
guard failed. The row is restored to six cells with the new status inside it.
"""
import io

PATH = 'docs/PARITY_CLAIMS.md'
text = io.open(PATH, encoding='utf-8').read()

old = ('| C8 | 字符串池对等 | **instrument**（R1380：`analysis/c8_string_class_compare.py`，'
       '按 locale 键/URL/错误消息/dependency 四类对照，四条限制随报告输出） | — |')
new = ('| C8 | 字符串池对等 | **instrument** | **R1380 仪器** | '
       '`python analysis/c8_string_class_compare.py --write-doc` | '
       '四类对照（locale 键/URL/错误消息/dependency）已可复算；四条限制随报告输出，**不是对等判决** |')

if old not in text:
    raise SystemExit('the four-cell row is not there; nothing to fix')

text = text.replace(old, new, 1)
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('C8 row restored to six cells')
