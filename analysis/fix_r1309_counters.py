"""R1309: the two documentation counters that move when a store is added.

Both guards read one number out of a document and compare it with the tree, so both had to move when
Saucony arrived:

  replica/docs/CORE_COVERAGE.md   "| flow 文件 | 18 |"        -> 19  (SauconyFlow.cs declares overrides)
  replica/docs/PARITY.md          section 3's "35 种不同的 flow" -> 36  and the "65 个注册模块" -> 66

PARITY.md is under replica/, not the repo root -- the guard walks up from the test bin directory until it
finds docs/PARITY.md, which lands inside replica. The first version of this script looked in the repo
root and died on FileNotFoundError, which is the cheapest possible way to learn that.

Byte-level with count assertions and UTF-8; these files carry CRLF.
"""
import io
import re
import sys

CORE = 'replica/docs/CORE_COVERAGE.md'
PARITY = 'replica/docs/PARITY.md'

ok = True

core = io.open(CORE, encoding='utf-8', newline='').read()
row = re.compile(r'(\|\s*flow \u6587\u4ef6\s*\|\s*)18(\s*\|)')
print('CORE_COVERAGE flow row at 18: %d' % len(row.findall(core)))
if len(row.findall(core)) == 1:
    io.open(CORE, 'w', encoding='utf-8', newline='').write(row.sub(r'\g<1>19\g<2>', core))
    print('  -> 19')
else:
    ok = False

parity = io.open(PARITY, encoding='utf-8', newline='').read()

flow_claim = re.compile(r'(\d+)(\s*\u79cd\u4e0d\u540c\u7684\s*flow)')
module_claim = re.compile(r'(\d+)(\s*\u4e2a\u6ce8\u518c\u6a21\u5757)')

flow_hits = flow_claim.findall(parity)
module_hits = module_claim.findall(parity)
print('PARITY flow-type claims: %s' % [n for n, _ in flow_hits])
print('PARITY module claims   : %s' % [n for n, _ in module_hits])

if [n for n, _ in flow_hits] == ['35']:
    parity = flow_claim.sub(lambda m: '36' + m.group(2) if m.group(1) == '35' else m.group(0), parity)
    print('  flow-type -> 36')
else:
    ok = False

if [n for n, _ in module_hits] == ['65']:
    parity = module_claim.sub(lambda m: '66' + m.group(2) if m.group(1) == '65' else m.group(0), parity)
    print('  modules   -> 66')
else:
    ok = False

io.open(PARITY, 'w', encoding='utf-8', newline='').write(parity)
sys.exit(0 if ok else 1)
