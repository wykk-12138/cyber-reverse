"""Recover compiler-generated name context around `get_<Member>` / `<Member>b__N` entries.

Why not a public tool: this is the NativeAOT closure/method-name table, stored as concatenated
name fragments in the image. rea's managed tools are IL-only (NativeAOT has no IL), and IDA has no
symbols here (`sub_*` only). The fragments still carry the compiler's own identifiers
(`<get_Toggle>b__14_0`, `<ToggleTask>b__1 <DeleteTask>b__0`), which is the only surviving
name-level evidence about *what* a bound member does.

Usage: python analysis/_nameblobs.py Member [Member ...]
       python analysis/_nameblobs.py --grep 'get_Toggle'
"""
import io
import re
import sys

POOL = 'analysis/pe_strings.txt'
args = sys.argv[1:]
grep_only = args and args[0] == '--grep'
words = args[1:] if grep_only else args
if not words:
    words = ['Toggle']

line_pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = []
for line in io.open(POOL, encoding='utf-8', errors='replace').read().splitlines():
    m = line_pat.match(line)
    if m:
        rows.append((m.group(1), m.group(2)))

# Fragments in these blobs are separated by arbitrary single characters; split on them so a
# match can be reported with a couple of neighbours on each side.
frag = re.compile(r'[<>A-Za-z0-9_]{4,}')

for word in words:
    pattern = re.compile(re.escape(word)) if grep_only else re.compile(r'(?:get_|set_)' + re.escape(word) + r'\b')
    print('=== %r' % word)
    for addr, text in rows:
        for m in pattern.finditer(text):
            window = text[max(0, m.start() - 120):m.end() + 200]
            print('   %-11s %s' % (addr, window))
    print()
