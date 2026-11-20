"""R1313: the five counters that move when a store is added, in one asserted pass.

Same shape as R1309, and the same reason each one is real rather than a number nudged to go green:

  ArrowAndBeastTests / CoreTests   66 -> 67   (CreateAll() gained AoFlow)
  CORE_COVERAGE.md  flow row       19 -> 20   (AoFlow.cs declares overrides)
  VERDICT.md status row            66 -> 67
  PARITY.md  counts                66 -> 67 modules, 36 -> 37 distinct flow classes

The first version of this script compared `findall` output against a bare string, which fails for every
pattern that has groups -- `findall` returns tuples there, so the check rejected all four document edits
while the file was already correct. The helper below takes the group index.

Byte-level, count-asserted, UTF-8 with CRLF preserved.
"""
import io
import re
import sys

ok = True


def patch(path, pattern, group, expected, replacement):
    """Replace exactly one match whose captured `group` reads `expected`."""
    global ok
    text = io.open(path, encoding='utf-8', newline='').read()
    found = re.findall(pattern, text)
    value = found[0][group] if found and isinstance(found[0], tuple) else (found[0] if found else None)
    print('%-34s found=%d value=%r' % (path.split('/')[-1], len(found), value))
    if len(found) != 1 or value != expected:
        ok = False
        return
    io.open(path, 'w', encoding='utf-8', newline='').write(re.sub(pattern, replacement, text, count=1))
    print('   -> patched')


patch('replica/tests/Cybersole.Tests/ArrowAndBeastTests.cs',
      r'Assert\.Equal\((\d+), count\);', 0, '66', 'Assert.Equal(67, count);')
patch('replica/tests/Cybersole.Tests/CoreTests.cs',
      r'Assert\.Equal\((\d+), registry\.Modules\.Count\);', 0, '66',
      'Assert.Equal(67, registry.Modules.Count);')
patch('replica/docs/CORE_COVERAGE.md',
      r'(\|\s*flow \u6587\u4ef6\s*\|\s*)(\d+)(\s*\|)', 1, '19', r'\g<1>20\g<3>')
patch('replica/docs/VERDICT.md',
      r'(\|\s*\u6ce8\u518c\u6a21\u5757\s*\|\s*\*\*)(\d+)(\*\*)', 1, '66', r'\g<1>67\g<3>')
patch('replica/docs/PARITY.md',
      r'(\d+)(\s*\u4e2a\u6ce8\u518c\u6a21\u5757)', 0, '66', r'67\g<2>')
patch('replica/docs/PARITY.md',
      r'(\d+)(\s*\u79cd\u4e0d\u540c\u7684\s*flow)', 0, '36', r'37\g<2>')

sys.exit(0 if ok else 1)
