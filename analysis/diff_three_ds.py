"""Diff the two ResolveThreeDsContingency documents and save both as UTF-8.

0x1470D7974 is 10846 characters and 0x1470DC9BC is 10958 in the inventory sample. Two documents that differ by
112 characters in the same family means one of them is a variant of the other, and which one runs is a question
worth answering before either is landed: landing both would double a 10 KB constant, landing the wrong one puts
a document in the replica that the store may not accept.

Usage: python analysis/diff_three_ds.py
"""
import difflib
import io
import json
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

A = 0x1470D7974
B = 0x1470DC9BC


def read_string(chars_va):
    res = call('get_bytes', {'regions': [{'addr': hex(chars_va - 12), 'size': 12}]})
    # The MCP client can answer with several JSON lines; the first one carries the region.
    if isinstance(res, str):
        res = json.loads(res.splitlines()[0])
    header = bytes(int(t, 16) for t in res[0]['data'].split())
    length = int.from_bytes(header[8:12], 'little')

    # The bridge answers in chunks of its own choosing, so read in 8 KiB windows until the declared length is
    # covered. A single 22 KB request came back in a different shape and the parse failed on it.
    blob = b''
    while len(blob) < length * 2:
        res = call('get_bytes', {'regions': [{'addr': hex(chars_va + len(blob)), 'size': 8192}]})
        if isinstance(res, str):
            res = json.loads(res.splitlines()[0])
        chunk = bytes(int(t, 16) for t in res[0]['data'].split())
        if not chunk:
            break
        blob += chunk
    return blob.decode('utf-16-le', errors='replace')[:length]


def main():
    a = read_string(A)
    b = read_string(B)
    print('A 0x%X  %d chars' % (A, len(a)))
    print('B 0x%X  %d chars' % (B, len(b)))
    print()

    matcher = difflib.SequenceMatcher(None, a, b, autojunk=False)
    changed = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            continue
        changed += 1
        print('%-8s A[%d:%d] %s' % (tag, i1, i2, a[i1:i2][:160].encode('unicode_escape').decode('ascii')))
        print('%-8s B[%d:%d] %s' % ('', j1, j2, b[j1:j2][:160].encode('unicode_escape').decode('ascii')))
    print()
    print('difference regions: %d   similarity: %.3f' % (
        changed, matcher.ratio()))

    io.open('analysis/.three_ds_a.txt', 'w', encoding='utf-8', newline='').write(a)
    io.open('analysis/.three_ds_b.txt', 'w', encoding='utf-8', newline='').write(b)
    print('wrote analysis/.three_ds_a.txt and .three_ds_b.txt')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
