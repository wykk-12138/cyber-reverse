"""Diagnostic: what exactly is at replica/tools/bind_diff.py line 55 and 91.

Written after two scanners disagreed about whether this file carries U+FFFD.
The disagreement is the finding, so print codepoints, byte offsets and the
decoded char-by-char view instead of trusting either scanner.
"""
import sys

PATH = 'replica/tools/bind_diff.py'

raw = open(PATH, 'rb').read()
print('size=%d crlf=%d' % (len(raw), raw.count(b'\r\n')))
text = raw.decode('utf-8')
print('decoded_chars=%d' % len(text))

for lineno in (55, 91):
    line = text.splitlines()[lineno - 1]
    idx = line.find('AGENTS.md')
    print('--- line %d, AGENTS.md at col %d' % (lineno, idx))
    print('    hex    : %s' % line[idx:idx + 14].encode('utf-8').hex(' '))
    print('    points : %s' % ' '.join('U+%04X' % ord(c) for c in line[idx:idx + 14]))

bad = [i for i, ch in enumerate(text) if ch == '\ufffd']
print('total U+FFFD in file: %d at char offsets %s' % (len(bad), bad[:10]))
sys.exit(0)
