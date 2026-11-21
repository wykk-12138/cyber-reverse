"""Find every constant in the replica whose text was pasted from a truncated display.

WarhammerQueries.ApproveOnboardPaymentMutation ends with the literal marker "[4040 chars total]" — a tool's
truncation notice that got pasted into the source. That document is therefore malformed and the store would
reject it. One instance means the history of this repository probably contains more, so the whole tree is
scanned for the shape: a bracketed integer followed by "chars total".

Usage: python analysis/find_pasted_truncation.py
"""
import io
import os
import re

MARKER = re.compile(r'\[\d+\s*chars? total\]')

hits = 0
for base, dirs, files in os.walk('replica'):
    dirs[:] = [d for d in dirs
               if d not in ('bin', 'obj', '.publish-aot', '.publish-aot-prev', '.publish-aot-new',
                            '.mutation-backup', '.snapshots')]
    for name in files:
        if not name.endswith(('.cs', '.json', '.md')):
            continue
        path = os.path.join(base, name)
        text = io.open(path, encoding='utf-8', errors='replace').read()
        for match in MARKER.finditer(text):
            line = text[:match.start()].count('\n') + 1
            print('%s:%d  %s' % (path, line, match.group(0)))
            hits += 1

print()
print('markers found: %d' % hits)
