"""Compare the complete operation inventory with what the replica carries.

The region scan found 65 operations; the replica declares 20. The difference is the honest backlog of documents,
and it is only trustworthy because the enumeration read the region rather than searching for strings — `ida.py
str` reported seven, which would have made this list nonsense.

Usage: python analysis/operation_gap.py
"""
import io
import json
import os
import re

ROOT = 'replica/src'
PATTERN = re.compile(r'(?:mutation|query)\s+(\w+)\s*[\(\{]')

image = json.loads(io.open('analysis/.operations_in_image.json', encoding='utf-8').read())

replica = {}
for base, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in ('bin', 'obj')]
    for name in files:
        if not name.endswith('.cs'):
            continue
        path = os.path.join(base, name)
        text = io.open(path, encoding='utf-8', errors='replace').read()
        for found in PATTERN.finditer(text):
            replica.setdefault(found.group(1), os.path.relpath(path, ROOT))

print('image:   %d operations' % len(image))
print('replica: %d operations' % len(replica))
# R1377: these two numbers answer different questions and I read one as the other for three rounds. Say the ratio.
covered_now = len(set(image) & set(replica))
print('carried: %d of %d image operations (absent %d)' % (
    covered_now, len(image), len(set(image) - set(replica))))
print()

covered = sorted(set(image) & set(replica))
print('carried (%d): %s' % (len(covered), ', '.join(covered)))
print()

missing = sorted(set(image) - set(replica), key=lambda name: -image[name]['length'])
print('absent (%d), longest first — the biggest payloads are the ones worth taking next:' % len(missing))
total = 0
for name in missing:
    entry = image[name]
    total += entry['length']
    print('   %-34s %6d chars   %s' % (name, entry['length'], entry['addr']))
print()
print('absent characters in total: %d' % total)
