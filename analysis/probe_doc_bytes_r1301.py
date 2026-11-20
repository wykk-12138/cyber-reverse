"""Byte-level probe of every doc site a scanner flagged, plus the committed copy.

Third opinion on purpose: two earlier reads disagreed, because the console
re-renders U+00A7 as a replacement glyph and made a clean file look corrupt.
Only three facts settle it -- the on-disk bytes, the same site in the committed
blob, and the codepoint list. Guessing which rendering to believe is not one.
"""
import subprocess

SITES = [
    ('docs/METRICS.md', 129, 'AGENTS.md'),
    ('docs/HANDOFF.md', 500, None),
    ('docs/KASADA/11-jint-runtime.md', 2673, None),
]


def show(label, text, lineno, anchor):
    lines = text.splitlines()
    if lineno > len(lines):
        print('%s: line %d beyond EOF (%d lines)' % (label, lineno, len(lines)))
        return
    line = lines[lineno - 1]
    start = line.find(anchor) if anchor else max(0, line.find('\ufffd') - 8)
    if start < 0:
        print('%s: no anchor and no U+FFFD on line %d' % (label, lineno))
        return
    piece = line[start:start + 16]
    print('%-28s hex=%s' % (label, piece.encode('utf-8').hex(' ')))
    print('%-28s pts=%s' % ('', ' '.join('U+%04X' % ord(c) for c in piece)))


for path, lineno, anchor in SITES:
    wt = open(path, 'rb').read().decode('utf-8')
    show('working ' + path.split('/')[-1], wt, lineno, anchor)
    blob = subprocess.run(['git', 'show', 'HEAD:' + path], capture_output=True).stdout
    show('HEAD    ' + path.split('/')[-1], blob.decode('utf-8'), lineno, anchor)
