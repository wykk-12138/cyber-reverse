"""Verify every 3DS document constant against the bytes that were decoded from the image."""

import io
import json
import re

SOURCE = 'replica/src/Cybersole.Stores/Payments/PayPalThreeDs.cs'
DOCS = 'analysis/.three_ds_docs.json'

text = io.open(SOURCE, encoding='utf-8').read()
docs = json.loads(io.open(DOCS, encoding='utf-8').read())
resolve_a = io.open('analysis/.three_ds_a.txt', encoding='utf-8').read()
resolve_b = io.open('analysis/.three_ds_b.txt', encoding='utf-8').read()

pairs = [
    ('LookUpDocumentWithoutProviderFields', resolve_a, 'lookup_a'),
    ('LookUpDocument', resolve_b, 'lookup_b'),
    ('AuthenticateDocument', resolve_b, 'authenticate'),
    ('ResolveDocumentWithoutProviderFields', resolve_a, None),
    ('ResolveDocument', resolve_b, None),
]

ok = True
for constant, _, key in pairs:
    match = re.search(constant + r'\s*=\s*@"(.*?)";', text, re.S)
    if not match:
        print('%-38s NOT FOUND' % constant)
        ok = False
        continue
    value = match.group(1).replace('""', '"')
    if key == 'lookup_a':
        expected, label = docs['lookup_a'], 'image lookup_a'
    elif key == 'lookup_b':
        expected, label = docs['lookup_b'], 'image lookup_b'
    elif key == 'authenticate':
        expected, label = docs['authenticate'], 'image authenticate'
    elif constant.startswith('ResolveDocumentWithout'):
        expected, label = resolve_a, 'image resolve A'
    else:
        expected, label = resolve_b, 'image resolve B'

    same = value == expected
    ok = ok and same
    print('%-38s %5d chars  %s  (%s)' % (constant, len(value), 'IDENTICAL' if same else 'DIFFERS', label))

print()
print('every constant matches its image document: %s' % ok)
raise SystemExit(0 if ok else 1)
