"""Dump full Avalonia compiled-XAML descriptors for the open type-level binding gaps.

Why not a public tool: seep-reverse-lab / rea operate on *binaries* (xrefs, decompilation).
The gap list lives in our own string pool snapshot (`pe_strings.txt`); the descriptor grammar
`<Declaring.Type>,<Owner.Type>.<Property>!Getter|Setter` is Avalonia-specific and no public tool
indexes it. This script only reads that snapshot and prints addresses so IDA xrefs can follow.

Usage: python analysis/_gap_desc.py [member ...]
"""
import io
import re
import sys

POOL = 'pe_strings.txt' if __import__('os').path.exists('pe_strings.txt') else 'analysis/pe_strings.txt'
MEMBERS = sys.argv[1:] or [
    'Toggle', 'Card', 'Username', 'Name', 'LinkChange', 'OpenFilter', 'OpenUrl',
    'Quicktask', 'View', 'Edit', 'ViewLogs', 'ProfileItems', 'Configure', 'Clock', 'Export',
]

rows = []
line_pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
for line in io.open(POOL, encoding='utf-8', errors='replace').read().splitlines():
    m = line_pat.match(line)
    if m:
        rows.append((m.group(1), m.group(2)))

desc = re.compile(
    r'((?:Cybersole|Avalonia|System)[\w.`+]*?)\s*,\s*((?:Cybersole|Avalonia|System)[\w.`+]*?)'
    r'!((?:Getter|Setter)(?:,\s*(?:Getter|Setter))*)'
)

by_member = {m: [] for m in MEMBERS}
for addr, text in rows:
    for m in desc.finditer(text):
        target, owner, kinds = m.group(1), m.group(2), m.group(3)
        leaf = owner.split('.')[-1]
        if leaf in by_member:
            by_member[leaf].append((addr, target, owner, kinds))

for member in MEMBERS:
    hits = by_member[member]
    print('== %-12s %d descriptor(s)' % (member, len(hits)))
    for addr, target, owner, kinds in hits:
        print('   %-12s %-58s owner=%-58s %s' % (addr, target, owner, kinds))
    print()
