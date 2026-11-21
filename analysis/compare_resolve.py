"""Compare the replica's ResolveDocument with the two variants the image holds.

The replica has had a ResolveDocument since R1149 and the image holds two variants of that document differing
by one inserted field block. Before replacing anything, measure: which variant is the replica's text, and how
far from it.

Usage: python analysis/compare_resolve.py
"""
import io
import re

SOURCE = 'replica/src/Cybersole.Stores/Payments/PayPalThreeDs.cs'
text = io.open(SOURCE, encoding='utf-8').read()

match = re.search(r'ResolveDocument\s*=\s*@"(.*?)";', text, re.S)
if not match:
    raise SystemExit('ResolveDocument constant not found')

replica = match.group(1).replace('""', '"')
a = io.open('analysis/.three_ds_a.txt', encoding='utf-8').read()
b = io.open('analysis/.three_ds_b.txt', encoding='utf-8').read()

print('replica ResolveDocument: %d chars' % len(replica))
print('image variant A:         %d chars' % len(a))
print('image variant B:         %d chars' % len(b))
print()
print('replica == A: %s' % (replica == a))
print('replica == B: %s' % (replica == b))
print()
print('replica head: %s' % replica[:90].replace('\n', '\\n'))
print('A head:       %s' % a[:90].replace('\n', '\\n'))
print('B head:       %s' % b[:90].replace('\n', '\\n'))
print()
print('A in replica: %s   B block in replica: %s' % (
    replica.find(a[:200]) >= 0, replica.find('authenticationProvider') >= 0))
