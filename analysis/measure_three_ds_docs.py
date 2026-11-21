"""R1324: the 3DS look-up and authenticate documents, measured the same way the resolve pair was.

R1323 found that the resolve mutation exists twice in the image — two dialects differing by one inserted field
block, each referenced once — and that the replica already held the longer one. The same question applies to
the two remaining 3DS operations, and this time it is asked before anything is written:

  ThreeDsLookUpMutation       0x1470E261C (877) and 0x1470E2CCC (905)  -- two of them
  ThreeDsAuthenticateMutation 0x1470E1FAC (837)                      -- one of them

For each: decode, compare with the replica's constant, and diff the pair. The output decides what the round
does, which is the point of measuring first.

Usage: python analysis/measure_three_ds_docs.py
"""
import difflib
import io
import json
import re
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SOURCES = {
    'lookup_a': 0x1470E261C,
    'lookup_b': 0x1470E2CCC,
    'authenticate': 0x1470E1FAC,
}
REPLICA = 'replica/src/Cybersole.Stores/Payments/PayPalThreeDs.cs'
OUT = 'analysis/.three_ds_docs.json'


def read_string(chars_va):
    """Decode a frozen UTF-16 string, 8 KiB at a time — a single large request changes the reply's shape."""
    res = call('get_bytes', {'regions': [{'addr': hex(chars_va - 12), 'size': 12}]})
    if isinstance(res, str):
        res = json.loads(res.splitlines()[0])
    header = bytes(int(t, 16) for t in res[0]['data'].split())
    length = int.from_bytes(header[8:12], 'little')

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


def replica_constant(name):
    text = io.open(REPLICA, encoding='utf-8').read()
    match = re.search(name + r'\s*=\s*@"(.*?)";', text, re.S)
    return match.group(1).replace('""', '"') if match else None


def main():
    docs = {}
    for name, address in SOURCES.items():
        docs[name] = read_string(address)
        print('%-13s 0x%09X  %d chars' % (name, address, len(docs[name])))

    print()
    for name, constant in (('lookup_a', 'LookUpDocument'), ('lookup_b', 'LookUpDocument'),
                           ('authenticate', 'AuthenticateDocument')):
        text = replica_constant(constant)
        print('%-13s vs replica %-20s %s (%d chars replica)' % (
            name, constant, 'IDENTICAL' if text == docs[name] else 'differs',
            len(text) if text is not None else -1))

    print()
    a, b = docs['lookup_a'], docs['lookup_b']
    print('lookup_a vs lookup_b: %d vs %d chars, similarity %.3f' % (
        len(a), len(b), difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()))
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == 'equal':
            continue
        print('  %-8s A[%d:%d] %s' % (tag, i1, i2, a[i1:i2][:150].encode('unicode_escape').decode('ascii')))
        print('  %-8s B[%d:%d] %s' % ('', j1, j2, b[j1:j2][:150].encode('unicode_escape').decode('ascii')))

    io.open(OUT, 'w', encoding='utf-8', newline='').write(json.dumps(docs, ensure_ascii=False, indent=2))
    print('\nwrote %s' % OUT)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
