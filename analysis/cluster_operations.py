"""Group the absent operations by address, because senders sit in feature blocks.

R1345 found five operations of one storefront API by looking at the neighbours of a single sender, and R1346
finished that family in one round instead of five. The same structure should be visible without any new IDA work:
the inventory already carries an address for every document, and documents of one feature are laid down together.

This sorts the absent operations by address and reports runs of neighbours, so the next round can take a block
rather than a document.

Usage: python analysis/cluster_operations.py
"""
import io
import json
import os
import re

IMAGE = 'analysis/.operations_in_image.json'
ROOT = 'replica/src'
PATTERN = re.compile(r'(?:mutation|query)\s+(\w+)\s*[\(\{]')

image = json.loads(io.open(IMAGE, encoding='utf-8').read())

carried = set()
for base, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in ('bin', 'obj')]
    for name in files:
        if not name.endswith('.cs'):
            continue
        text = io.open(os.path.join(base, name), encoding='utf-8', errors='replace').read()
        for found in PATTERN.finditer(text):
            carried.add(found.group(1))

absent = [(name, entry['addr'], entry['length']) for name, entry in image.items() if name not in carried]
absent.sort(key=lambda row: row[1])

print('absent operations: %d' % len(absent))
print()

GAP = 0x4000        # documents of one feature are within a few pages of each other
block = []
blocks = []
for row in absent:
    if block and row[1] - block[-1][1] > GAP:
        blocks.append(block)
        block = []
    block.append(row)
if block:
    blocks.append(block)

blocks.sort(key=lambda group: -sum(row[2] for row in group))
for group in blocks:
    total = sum(row[2] for row in group)
    print('--- %d operations, %d characters, %#x..%#x' % (len(group), total, group[0][1], group[-1][1]))
    for name, addr, length in group:
        print('    %-34s %6d chars  %#x' % (name, length, addr))
