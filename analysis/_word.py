"""Search the string pool for occurrences of a word, showing which *kind* of string each is.

Why not `find_regex` in IDA: the pool snapshot is 10x faster to grep for exploratory work, and the
IDA side is only worth a round-trip once a candidate is chosen. Addresses printed here are file
offsets; IDA VAs are recovered by the plugin's own find_regex when needed.

Usage: python analysis/_word.py Toggle [more words...]
"""
import io
import re
import sys

WORDS = [w for w in sys.argv[1:]] or ['Toggle']
line_pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')


def kind(text):
    if re.search(r'(?:Cybersole|Avalonia|System)[\w.`+]*,[\w.`+]*!', text):
        return 'descriptor'
    if text.startswith('"') and '":' in text:
        return 'locale'
    if re.fullmatch(r'[A-Za-z_][\w.]*', text):
        return 'identifier'
    if re.fullmatch(r'[a-z][A-Za-z0-9_]*', text):
        return 'camel'
    if text.startswith('http'):
        return 'url'
    return 'text'


rows = []
for line in io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines():
    m = line_pat.match(line)
    if m:
        rows.append((m.group(1), m.group(2)))

for word in WORDS:
    pat = re.compile(r'(?<![A-Za-z])' + re.escape(word) + r'(?![a-z])')
    hits = [(a, t) for a, t in rows if pat.search(t)]
    print('=== %-14s %d hit(s)' % (word, len(hits)))
    seen = set()
    for addr, text in hits:
        k = kind(text)
        key = (k, text[:70])
        if key in seen:
            continue
        seen.add(key)
        print('   %-11s %-10s %s' % (addr, k, text[:190]))
    print()
