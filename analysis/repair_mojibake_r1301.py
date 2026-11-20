"""R1301 step 2: repair the two committed doc defects, byte-verified.

Both were already in HEAD, which is why neither is a regression from the phase-2
work: the guard only walked replica/{src,tests,tools,docs} and only looked at
.cs/.md/.json/.ps1, so repository-root docs were never scanned and no .py tool
script ever was either. Both blind spots are closed in this same round.

  docs/HANDOFF.md:501                ... 过去一<U+FFFD>直在少报  ->  过去一直在少报
  docs/KASADA/11-jint-runtime.md:2673  | 打<FFFD><FFFD><FFFD> | 结果 |  ->  | 打法 | 结果 |

The second one is settled by the sentence that introduces the table two lines
above it ("三种打法："), not by guessing at the missing glyph.

docs/METRICS.md is deliberately NOT patched here: it is generated, and its
damage came from metrics_report.py capturing child stdout with errors="replace"
while the child emitted GBK. The generator is fixed in this round and the file
is regenerated; editing the generated copy would hide the cause.

Each patch asserts its expected occurrence count and refuses on any mismatch, so
a wrong-file edit cannot pass silently. Byte-level hex of every touched site is
printed after the write.
"""
import sys

PATCHES = [
    ('docs/HANDOFF.md',
     '\u8fc7\u53bb\u4e00\ufffd\u76f4', '\u8fc7\u53bb\u4e00\u76f4', 1),
    ('docs/KASADA/11-jint-runtime.md',
     '\u6253\ufffd\ufffd\ufffd', '\u6253\u6cd5', 1),
]


def main():
    ok = True
    for path, before, after, want in PATCHES:
        raw = open(path, 'rb').read()
        text = raw.decode('utf-8')
        got = text.count(before)
        if got != want:
            print('REFUSED  %-40s found=%d want=%d' % (path, got, want))
            ok = False
            continue
        open(path, 'wb').write(text.replace(before, after).encode('utf-8'))
        print('patched  %-40s x%d' % (path, got))

    print('--- verification: hex of each repaired site, and remaining U+FFFD count ---')
    for path, _before, after, _want in PATCHES:
        text = open(path, 'rb').read().decode('utf-8')
        at = text.find(after)
        piece = text[at:at + len(after) + 4]
        print('%-40s hex=%s  remaining_U+FFFD=%d'
              % (path, piece.encode('utf-8').hex(' '), text.count('\ufffd')))
        if text.count('\ufffd'):
            ok = False
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
